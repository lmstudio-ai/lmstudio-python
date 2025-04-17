"""Shared core async websocket implementation for the LM Studio remote access API."""

# Sync API: runs in background thread with sync queues
# Async convenience API: runs in background thread with async queues
# Async structured API: runs in foreground event loop

# Callback handling rules:
#
# * All callbacks are synchronous (use external async queues if needed)
# * All callbacks must be invoked from the *foreground* thread/event loop

import asyncio
import threading
import weakref

from concurrent.futures import Future as SyncFuture
from contextlib import (
    AsyncExitStack,
)
from typing import (
    Any,
    Awaitable,
    Coroutine,
    Callable,
    TypeVar,
)

# Synchronous API still uses an async websocket (just in a background thread)
from anyio import create_task_group, move_on_after
from httpx_ws import aconnect_ws, AsyncWebSocketSession, HTTPXWSException

from .schemas import DictObject
from .json_api import LMStudioWebsocket, LMStudioWebsocketError

from ._logging import get_logger, LogEventContext


# Allow the core client websocket management to be shared across all SDK interaction APIs
# See https://discuss.python.org/t/daemon-threads-and-background-task-termination/77604
# (Note: this implementation has the elements needed to run on *current* Python versions
# and omits the generalised features that the SDK doesn't need)
# Already used by the sync API, async client is still to be migrated
T = TypeVar("T")


class AsyncTaskManager:
    def __init__(self, *, on_activation: Callable[[], Any] | None) -> None:
        self._activated = False
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._on_activation = on_activation
        self._task_queue: asyncio.Queue[Callable[[], Awaitable[Any]]] = asyncio.Queue()
        self._terminate = asyncio.Event()
        self._terminated = asyncio.Event()

    @property
    def activated(self) -> bool:
        return self._activated

    @property
    def active(self) -> bool:
        return (
            self._activated
            and self._event_loop is not None
            and not self._terminated.is_set()
        )

    def check_running_in_task_loop(self, *, allow_inactive: bool = False) -> bool:
        """Returns if running in this manager's event loop, raises RuntimeError otherwise."""
        this_loop = self._event_loop
        if this_loop is None:
            # Task manager isn't active -> no coroutine can be running in it
            if allow_inactive:
                # No exception, but indicate the task manager isn't actually running
                return False
            raise RuntimeError(f"{self!r} is currently inactive.")
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop in this thread -> can't be running in the task manager
            running_loop = None
        # Check if the running loop is the task manager's loop
        if running_loop is not this_loop:
            err_details = f"Expected: {this_loop!r} Running: {running_loop!r}"
            err_msg = f"{self!r} is running in a different event loop ({err_details})."
            raise RuntimeError(err_msg)
        return True

    async def request_termination(self) -> bool:
        """Request termination of the task manager from the same thread."""
        if not self.check_running_in_task_loop(allow_inactive=True):
            return False
        if self._terminate.is_set():
            return False
        self._terminate.set()
        return True

    def request_termination_threadsafe(self) -> SyncFuture[bool]:
        """Request termination of the task manager from any thread."""
        loop = self._event_loop
        if loop is None:
            result: SyncFuture[bool] = SyncFuture()
            result.set_result(False)
            return result
        return self.run_coroutine_threadsafe(self.request_termination())

    async def wait_for_termination(self) -> None:
        """Wait in the same thread for the task manager to indicate it has terminated."""
        if not self.check_running_in_task_loop(allow_inactive=True):
            return
        await self._terminated.wait()

    def wait_for_termination_threadsafe(self) -> None:
        """Wait in any thread for the task manager to indicate it has terminated."""
        loop = self._event_loop
        if loop is None:
            if not self._activated:
                raise RuntimeError(f"{self!r} is not yet active.")
            # Previously activated without an active event loop -> already terminated
            return
        self.run_coroutine_threadsafe(self.wait_for_termination()).result()

    async def terminate(self) -> None:
        """Terminate the task manager from the same thread."""
        if await self.request_termination():
            await self.wait_for_termination()

    def terminate_threadsafe(self) -> None:
        """Terminate the task manager from any thread."""
        if self.request_termination_threadsafe().result():
            self.wait_for_termination_threadsafe()

    def _init_event_loop(self) -> None:
        if self._event_loop is not None:
            raise RuntimeError()
        self._event_loop = asyncio.get_running_loop()
        self._activated = True
        notify = self._on_activation
        if notify is not None:
            notify()

    async def run_until_terminated(
        self, func: Callable[[], Coroutine[Any, Any, Any]] | None = None
    ) -> None:
        """Run task manager until termination is requested."""
        self._init_event_loop()
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        try:
            async with create_task_group() as tg:
                tg.start_soon(self._accept_queued_tasks)
                if func is not None:
                    tg.start_soon(func)
                # Terminate all running tasks when termination is requested
                try:
                    await self._terminate.wait()
                finally:
                    tg.cancel_scope.cancel()
        finally:
            # Event loop is about to shut down
            self._terminated.set()
            self._event_loop = None

    async def _accept_queued_tasks(self) -> None:
        async with create_task_group() as additional_tasks:
            while True:
                task_func = await self._task_queue.get()
                additional_tasks.start_soon(task_func)

    async def schedule_task(self, func: Callable[[], Awaitable[Any]]) -> None:
        """Schedule given task in the task manager's base coroutine from the same thread.

        Important: task must NOT access any scoped resources from the scheduling scope.
        """
        self.check_running_in_task_loop()
        await self._task_queue.put(func)

    def schedule_task_threadsafe(self, func: Callable[[], Awaitable[Any]]) -> None:
        """Schedule given task in the task manager's base coroutine from any thread.

        Important: task must NOT access any scoped resources from the scheduling scope.
        """
        loop = self._event_loop
        if loop is None:
            raise RuntimeError(f"{self!r} is currently inactive.")
        asyncio.run_coroutine_threadsafe(self.schedule_task(func), loop)

    def run_coroutine_threadsafe(self, coro: Coroutine[Any, Any, T]) -> SyncFuture[T]:
        """Call given coroutine in the task manager's event loop from any thread.

        Important: coroutine must NOT access any scoped resources from the calling scope.
        """
        loop = self._event_loop
        if loop is None:
            raise RuntimeError(f"{self!r} is currently inactive.")
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def call_soon_threadsafe(self, func: Callable[[], Any]) -> asyncio.Handle:
        """Call given non-blocking function in the background event loop."""
        loop = self._event_loop
        if loop is None:
            raise RuntimeError(f"{self!r} is currently inactive.")
        return loop.call_soon_threadsafe(func)


class BackgroundThread(threading.Thread):
    """Background async event loop thread."""

    def __init__(
        self,
        task_target: Callable[[], Coroutine[Any, Any, Any]] | None = None,
        name: str | None = None,
    ) -> None:
        # Accepts the same args as `threading.Thread`, *except*:
        #   * a  `task_target` coroutine replaces the `target` function
        #   * No `daemon` option (always runs as a daemon)
        # Variant: accept `debug` and `loop_factory` options to forward to `asyncio.run`
        # Alternative: accept a `task_runner` callback, defaulting to `asyncio.run`
        self._task_target = task_target
        self._loop_started = loop_started = threading.Event()
        self._task_manager = AsyncTaskManager(on_activation=loop_started.set)
        # Annoyingly, we have to mark the background thread as a daemon thread to
        # prevent hanging at shutdown. Even checking `sys.is_finalizing()` is inadequate
        # https://discuss.python.org/t/should-sys-is-finalizing-report-interpreter-finalization-instead-of-runtime-finalization/76695
        super().__init__(name=name, daemon=True)
        weakref.finalize(self, self.terminate)

    @property
    def task_manager(self) -> AsyncTaskManager:
        return self._task_manager

    def start(self, wait_for_loop: bool = True) -> None:
        """Start background thread and (optionally) wait for the event loop to be ready."""
        super().start()
        if wait_for_loop:
            self.wait_for_loop()

    def run(self) -> None:
        """Run an async event loop in the background thread."""
        # Only public to override threading.Thread.run
        asyncio.run(self._task_manager.run_until_terminated(self._task_target))

    def wait_for_loop(self) -> asyncio.AbstractEventLoop | None:
        """Wait for the event loop to start from a synchronous foreground thread."""
        if self._task_manager._event_loop is None and not self._task_manager.activated:
            self._loop_started.wait()
        return self._task_manager._event_loop

    async def wait_for_loop_async(self) -> asyncio.AbstractEventLoop | None:
        """Wait for the event loop to start from an asynchronous foreground thread."""
        return await asyncio.to_thread(self.wait_for_loop)

    def terminate(self) -> bool:
        """Request termination of the event loop from a synchronous foreground thread."""
        return self._task_manager.request_termination_threadsafe().result()

    async def terminate_async(self) -> bool:
        """Request termination of the event loop from an asynchronous foreground thread."""
        return await asyncio.to_thread(self.terminate)

    def schedule_background_task(self, func: Callable[[], Any]) -> None:
        """Schedule given task in the event loop from a synchronous foreground thread."""
        self._task_manager.schedule_task_threadsafe(func)

    async def schedule_background_task_async(self, func: Callable[[], Any]) -> None:
        """Schedule given task in the event loop from an asynchronous foreground thread."""
        return await asyncio.to_thread(self.schedule_background_task, func)

    def run_background_coroutine(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run given coroutine in the event loop and wait for the result."""
        return self._task_manager.run_coroutine_threadsafe(coro).result()

    async def run_background_coroutine_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run given coroutine in the event loop and await the result."""
        return await asyncio.to_thread(self.run_background_coroutine, coro)

    def call_in_background(self, func: Callable[[], Any]) -> None:
        """Call given non-blocking function in the background event loop."""
        self._task_manager.call_soon_threadsafe(func)


class AsyncWebsocketThread(BackgroundThread):
    def __init__(self, log_context: LogEventContext | None = None) -> None:
        super().__init__(task_target=self._log_thread_execution)
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, thread_id=self.name)

    async def _log_thread_execution(self) -> None:
        self._logger.info("Websocket handling thread started")
        never_set = asyncio.Event()
        try:
            # Run the event loop until termination is requested
            await never_set.wait()
        except BaseException:
            err_msg = "Terminating websocket thread due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            self._logger.info("Websocket thread terminated")


# TODO: Improve code sharing between AsyncWebsocketHandler and
#       the async-native AsyncLMStudioWebsocket implementation
class AsyncWebsocketHandler:
    """Async task handler for a single websocket connection."""

    WS_DISCONNECT_TIMEOUT = 10

    def __init__(
        self,
        task_manager: AsyncTaskManager,
        ws_url: str,
        auth_details: DictObject,
        enqueue_message: Callable[[DictObject], bool],
        log_context: LogEventContext | None = None,
    ) -> None:
        self._auth_details = auth_details
        self._connection_attempted = asyncio.Event()
        self._connection_failure: Exception | None = None
        self._auth_failure: Any | None = None
        self._task_manager = task_manager
        self._ws_url = ws_url
        self._ws: AsyncWebSocketSession | None = None
        self._ws_disconnected = asyncio.Event()
        self._rx_task: asyncio.Task[None] | None = None
        self._enqueue_message = enqueue_message
        self._logger = get_logger(type(self).__name__)
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context)

    async def connect(self) -> bool:
        """Connect websocket from the task manager's event loop."""
        task_manager = self._task_manager
        assert task_manager.check_running_in_task_loop()
        await task_manager.schedule_task(self._logged_ws_handler)
        await self._connection_attempted.wait()
        return self._ws is not None

    def connect_threadsafe(self) -> bool:
        """Connect websocket from any thread."""
        task_manager = self._task_manager
        task_manager.run_coroutine_threadsafe(self.connect()).result()
        return self._ws is not None

    async def disconnect(self) -> None:
        """Disconnect websocket from the task manager's event loop."""
        assert self._task_manager.check_running_in_task_loop()
        self._ws_disconnected.set()
        ws = self._ws
        if ws is None:
            return
        await ws.close()

    def disconnect_threadsafe(self) -> None:
        """Disconnect websocket from any thread."""
        task_manager = self._task_manager
        task_manager.run_coroutine_threadsafe(self.disconnect()).result()

    async def _logged_ws_handler(self) -> None:
        self._logger.info("Websocket handling task started")
        try:
            await self._handle_ws()
        except BaseException:
            err_msg = "Terminating websocket task due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            # Ensure the foreground thread is unblocked even if the
            # background async task errors out completely
            self._connection_attempted.set()
        self._logger.info("Websocket task terminated")

    async def _handle_ws(self) -> None:
        assert self._task_manager.check_running_in_task_loop()
        resources = AsyncExitStack()
        try:
            ws: AsyncWebSocketSession = await resources.enter_async_context(
                aconnect_ws(self._ws_url)
            )
        except Exception as exc:
            self._connection_failure = exc
            raise

        def _clear_task_state() -> None:
            # Break the reference cycle with the foreground thread
            del self._enqueue_message
            # Websocket is about to be disconnected
            self._ws = None

        resources.callback(_clear_task_state)
        async with resources:
            self._logger.debug("Websocket connected")
            self._ws = ws
            if not await self._authenticate():
                return
            self._connection_attempted.set()
            self._logger.info(f"Websocket session established ({self._ws_url})")
            # Task will run until message reception fails or is cancelled
            try:
                await self._receive_messages()
            finally:
                self._logger.info("Websocket demultiplexing task terminated.")
                dc_timeout = self.WS_DISCONNECT_TIMEOUT
                with move_on_after(dc_timeout, shield=True) as cancel_scope:
                    # Workaround an anyio/httpx-ws issue with task cancellation:
                    # https://github.com/frankie567/httpx-ws/issues/107
                    self._ws = None
                    await ws.close()
                if cancel_scope.cancelled_caught:
                    self._logger.warn(
                        f"Failed to close websocket in {dc_timeout} seconds."
                    )
                else:
                    self._logger.info("Websocket closed.")

    async def send_json(self, message: DictObject) -> None:
        # This is only called if the websocket has been created
        assert self._task_manager.check_running_in_task_loop()
        ws = self._ws
        assert ws is not None
        try:
            await ws.send_json(message)
        except Exception as exc:
            err = LMStudioWebsocket._get_tx_error(message, exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    def send_json_threadsafe(self, message: DictObject) -> None:
        future = self._task_manager.run_coroutine_threadsafe(self.send_json(message))
        future.result()  # Block until the message is sent

    async def _receive_json(self) -> Any:
        # This is only called if the websocket has been created
        assert self._task_manager.check_running_in_task_loop()
        ws = self._ws
        assert ws is not None
        try:
            return await ws.receive_json()
        except Exception as exc:
            err = LMStudioWebsocket._get_rx_error(exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _authenticate(self) -> bool:
        # This is only called if the websocket has been created
        assert self._task_manager.check_running_in_task_loop()
        ws = self._ws
        assert ws is not None
        auth_message = self._auth_details
        await self.send_json(auth_message)
        auth_result = await self._receive_json()
        self._logger.debug("Websocket authenticated", json=auth_result)
        if not auth_result["success"]:
            self._auth_failure = auth_result["error"]
            return False
        return True

    async def _process_next_message(self) -> bool:
        """Process the next message received on the websocket.

        Returns True if a message queue was updated.
        """
        # This is only called if the websocket has been created
        assert self._task_manager.check_running_in_task_loop()
        ws = self._ws
        assert ws is not None
        message = await ws.receive_json()
        # Enqueueing messages may be a blocking call
        # TODO: Require it to return an Awaitable, move to_thread call to the sync bridge
        return await asyncio.to_thread(self._enqueue_message, message)

    async def _receive_messages(self) -> None:
        """Process received messages until task is cancelled."""
        while True:
            try:
                await self._process_next_message()
            except (LMStudioWebsocketError, HTTPXWSException):
                if self._ws is not None and not self._ws_disconnected.is_set():
                    # Websocket failed unexpectedly (rather than due to client shutdown)
                    self._logger.exception("Websocket failed, terminating session.")
                break


class SyncToAsyncWebsocketBridge:
    def __init__(
        self,
        ws_thread: AsyncWebsocketThread,
        ws_url: str,
        auth_details: DictObject,
        enqueue_message: Callable[[DictObject], bool],
        log_context: LogEventContext,
    ) -> None:
        self._ws_handler = AsyncWebsocketHandler(
            ws_thread.task_manager, ws_url, auth_details, enqueue_message, log_context
        )

    def connect(self) -> bool:
        return self._ws_handler.connect_threadsafe()

    def disconnect(self) -> None:
        self._ws_handler.disconnect_threadsafe()

    def send_json(self, message: DictObject) -> None:
        self._ws_handler.send_json_threadsafe(message)

    # These attributes are currently accessed directly...
    @property
    def _ws(self) -> AsyncWebSocketSession | None:
        return self._ws_handler._ws

    @property
    def _connection_failure(self) -> Exception | None:
        return self._ws_handler._connection_failure

    @property
    def _auth_failure(self) -> Any | None:
        return self._ws_handler._auth_failure
