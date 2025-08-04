"""Shared core async websocket implementation for the LM Studio remote access API."""

# Sync API: runs in dedicated background thread
# Async convenience API (once implemented): runs in dedicated background thread
# Async structured API: runs in foreground event loop

# Callback handling rules:
#
# * All callbacks are synchronous (use external async queues if needed)
# * All callbacks must be invoked from the *foreground* thread/event loop

import asyncio


# Python 3.10 compatibility: use concurrent.futures.TimeoutError instead of the builtin
# In 3.11+, these are the same type, in 3.10 futures have their own timeout exception
from concurrent.futures import Future as SyncFuture, TimeoutError as SyncFutureTimeout
from contextvars import ContextVar
from contextlib import AsyncExitStack, contextmanager
from functools import partial
from typing import (
    Any,
    Awaitable,
    Coroutine,
    Callable,
    ClassVar,
    Generator,
    TypeAlias,
    TypeVar,
)
from typing_extensions import (
    # Native in 3.11+
    Self,
)

from anyio import create_task_group, move_on_after
from httpx_ws import aconnect_ws, AsyncWebSocketSession, HTTPXWSException

from .schemas import DictObject
from .sdk_api import LMStudioRuntimeError
from .json_api import (
    LMStudioWebsocket,
    LMStudioWebsocketError,
    MultiplexingManager,
    RxQueue,
)

from ._logging import LogEventContext, new_logger

T = TypeVar("T")

__all__ = [
    "SyncFutureTimeout",
    "AsyncTaskManager",
    "AsyncWebsocketHandler",
]


class AsyncTaskManager:
    _LMS_TASK_MANAGER: ClassVar[ContextVar[Self]] = ContextVar("_LMS_TASK_MANAGER")

    def __init__(self, *, on_activation: Callable[[], Any] | None = None) -> None:
        self._activated = False
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._on_activation = on_activation
        self._task_queue: asyncio.Queue[Callable[[], Awaitable[Any]]] = asyncio.Queue()
        self._terminate = asyncio.Event()
        self._terminated = asyncio.Event()
        # For the case where the task manager is run via its context manager
        self._tm_started = asyncio.Event()
        self._tm_task: asyncio.Task[Any] | None = None

    ACTIVATION_TIMEOUT = 5  # Just starts an async task, should be fast
    TERMINATION_TIMEOUT = 20  # May have to shut down TCP links

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

    async def __aenter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        if self._tm_task is None:
            self._tm_task = asyncio.create_task(self.run_until_terminated())
        with move_on_after(self.ACTIVATION_TIMEOUT):
            await self._tm_started.wait()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.request_termination()
        with move_on_after(self.TERMINATION_TIMEOUT, shield=True):
            await self._terminated.wait()

    @classmethod
    def get_running_task_manager(cls) -> Self:
        try:
            return cls._LMS_TASK_MANAGER.get()
        except LookupError:
            err_msg = "No async task manager active in current context"
            raise LMStudioRuntimeError(err_msg) from None

    def ensure_running_in_task_loop(self) -> None:
        this_loop = self._event_loop
        if this_loop is None:
            # Task manager isn't active -> no coroutine can be running in it
            raise LMStudioRuntimeError(f"{self!r} is currently inactive.")
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop in this thread -> can't be running in the task manager
            running_loop = None
        # Check if the running loop is the task manager's loop
        if running_loop is not this_loop:
            err_details = f"Expected: {this_loop!r} Running: {running_loop!r}"
            err_msg = f"{self!r} is running in a different event loop ({err_details})."
            raise LMStudioRuntimeError(err_msg)

    def is_running_in_task_loop(self) -> bool:
        try:
            self.ensure_running_in_task_loop()
        except LMStudioRuntimeError:
            return False
        return True

    def ensure_running_in_task_manager(self) -> None:
        # Task manager must be active in the running event loop
        self.ensure_running_in_task_loop()
        running_tm = self.get_running_task_manager()
        if running_tm is not self:
            err_details = f"Expected: {self!r} Running: {running_tm!r}"
            err_msg = f"Task is running in a different task manager ({err_details})."
            raise LMStudioRuntimeError(err_msg)

    async def request_termination(self) -> bool:
        """Request termination of the task manager from the same thread."""
        if not self.is_running_in_task_loop():
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
        if not self.is_running_in_task_loop():
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

    def _mark_as_running(self: Self) -> None:
        # Explicit type hint to work around https://github.com/python/mypy/issues/16871
        if self._event_loop is not None:
            raise LMStudioRuntimeError("Async task manager is already running")
        self._event_loop = asyncio.get_running_loop()
        self._activated = True
        self._LMS_TASK_MANAGER.set(self)
        notify = self._on_activation
        if notify is not None:
            notify()
        self._tm_started.set()

    async def run_until_terminated(
        self, func: Callable[[], Coroutine[Any, Any, Any]] | None = None
    ) -> None:
        """Run task manager until termination is requested."""
        self._mark_as_running()
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
        self.ensure_running_in_task_loop()
        await self._task_queue.put(func)

    def schedule_task_threadsafe(self, func: Callable[[], Awaitable[Any]]) -> None:
        """Schedule given task in the task manager's base coroutine from any thread.

        Important: task must NOT access any scoped resources from the scheduling scope.
        """
        self.run_coroutine_threadsafe(self.schedule_task(func))

    def run_coroutine_threadsafe(self, coro: Coroutine[Any, Any, T]) -> SyncFuture[T]:
        """Call given coroutine in the task manager's event loop from any thread.

        Important: coroutine must NOT access any scoped resources from the calling scope.
        """
        loop = self._event_loop
        if loop is None:
            raise RuntimeError(f"{self!r} is currently inactive.")
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def call_threadsafe(self, func: Callable[[], T]) -> SyncFuture[T]:
        """Call non-blocking function in the background event loop and make the result available.

        Important: function must NOT access any scoped resources from the calling scope.
        """

        async def coro() -> T:
            return func()

        return self.run_coroutine_threadsafe(coro())

    def call_soon_threadsafe(self, func: Callable[[], Any]) -> asyncio.Handle:
        """Call given non-blocking function in the background event loop."""
        loop = self._event_loop
        if loop is None:
            raise RuntimeError(f"{self!r} is currently inactive.")
        return loop.call_soon_threadsafe(func)


AsyncChannelInfo: TypeAlias = tuple[int, Callable[[], Awaitable[Any]]]
AsyncRemoteCallInfo: TypeAlias = tuple[int, Callable[[], Awaitable[Any]]]


class AsyncWebsocketHandler:
    """Async task handler for a single websocket connection."""

    WS_DISCONNECT_TIMEOUT = 10

    def __init__(
        self,
        task_manager: AsyncTaskManager,
        ws_url: str,
        auth_details: DictObject,
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
        self._logger = logger = new_logger(type(self).__name__)
        logger.update_context(log_context, ws_url=ws_url)
        self._mux = MultiplexingManager(logger)

    async def connect(self) -> bool:
        """Connect websocket from the task manager's event loop."""
        task_manager = self._task_manager
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
        self._task_manager.ensure_running_in_task_loop()
        # Websocket handler task may already have been cancelled,
        # but the closure can be requested multiple times without issue
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
        self._logger.debug("Websocket handling task started")
        try:
            await self._handle_ws()
        except (asyncio.CancelledError, GeneratorExit):
            raise
        except BaseException:
            err_msg = "Terminating websocket task due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            # Ensure connections attempt are unblocked even if the
            # background async task errors out completely
            self._connection_attempted.set()
            self._logger.debug("Websocket task terminated")

    async def _handle_ws(self) -> None:
        resources = AsyncExitStack()
        try:
            # For reliable shutdown, handler must run entirely inside the task manager
            self._task_manager.ensure_running_in_task_manager()
            ws: AsyncWebSocketSession = await resources.enter_async_context(
                aconnect_ws(self._ws_url)
            )
        except Exception as exc:
            self._connection_failure = exc
            raise

        def _clear_task_state() -> None:
            # Websocket is about to be disconnected (if it isn't already)
            self._ws = None

        resources.callback(_clear_task_state)
        async with resources:
            self._logger.debug("Websocket connected")
            self._ws = ws
            if not await self._authenticate():
                return
            self._connection_attempted.set()
            self._logger.info("Websocket session established")
            # Task will run until message reception fails or is cancelled
            try:
                await self._receive_messages()
            finally:
                self._logger.debug("Websocket demultiplexing task terminated.")
                # Notify foreground thread of background thread termination
                # (this covers termination due to link failure)
                await self.notify_client_termination()
                dc_timeout = self.WS_DISCONNECT_TIMEOUT
                with move_on_after(dc_timeout, shield=True) as cancel_scope:
                    # Workaround an anyio/httpx-ws issue with task cancellation:
                    # https://github.com/frankie567/httpx-ws/issues/107
                    self._ws = None
                    try:
                        await ws.close()
                    except Exception:
                        # Closing may fail if the link is already down
                        pass
                if cancel_scope.cancelled_caught:
                    self._logger.warn(
                        f"Failed to close websocket in {dc_timeout} seconds."
                    )
                else:
                    self._logger.info("Websocket closed.")

    async def send_json(self, message: DictObject) -> None:
        # This is only called if the websocket has been created
        self._task_manager.ensure_running_in_task_loop()
        ws = self._ws
        if ws is None:
            # Assume app is shutting down and the owning task has already been cancelled
            rx_queue = self._mux.map_tx_message(message)
            if rx_queue is not None:
                await rx_queue.put(None)
            return
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

    def run_background_coroutine(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run given coroutine in the event loop and wait for the result."""
        return self._task_manager.run_coroutine_threadsafe(coro).result()

    @contextmanager
    def open_channel(self) -> Generator[AsyncChannelInfo, None, None]:
        self._task_manager.ensure_running_in_task_loop()
        rx_queue: RxQueue = asyncio.Queue()
        with self._mux.assign_channel_id(rx_queue) as call_id:
            yield call_id, rx_queue.get

    @contextmanager
    def start_call(self) -> Generator[AsyncRemoteCallInfo, None, None]:
        self._task_manager.ensure_running_in_task_loop()
        rx_queue: RxQueue = asyncio.Queue()
        with self._mux.assign_call_id(rx_queue) as call_id:
            yield call_id, rx_queue.get

    def new_threadsafe_rx_queue(self) -> tuple[RxQueue, Callable[[float | None], Any]]:
        rx_queue: RxQueue = asyncio.Queue()
        return rx_queue, partial(self._rx_queue_get_threadsafe, rx_queue)

    def acquire_channel_id_threadsafe(self, rx_queue: RxQueue) -> int:
        future = self._task_manager.call_threadsafe(
            partial(self._mux.acquire_channel_id, rx_queue)
        )
        return future.result()  # Wait for background thread to assign the ID

    def release_channel_id_threadsafe(self, channel_id: int, rx_queue: RxQueue) -> None:
        self._task_manager.call_soon_threadsafe(
            partial(self._mux.release_channel_id, channel_id, rx_queue)
        )

    def acquire_call_id_threadsafe(self, rx_queue: RxQueue) -> int:
        future = self._task_manager.call_threadsafe(
            partial(self._mux.acquire_call_id, rx_queue)
        )
        return future.result()  # Wait for background thread to assign the ID

    def release_call_id_threadsafe(self, call_id: int, rx_queue: RxQueue) -> None:
        self._task_manager.call_soon_threadsafe(
            partial(self._mux.release_call_id, call_id, rx_queue)
        )

    def _rx_queue_get_threadsafe(self, rx_queue: RxQueue, timeout: float | None) -> Any:
        future = self._task_manager.run_coroutine_threadsafe(rx_queue.get())
        try:
            return future.result(timeout)
        except SyncFutureTimeout:
            future.cancel()
            raise

    async def _receive_json(self) -> Any:
        # This is only called if the websocket has been created
        if __debug__:
            # This should only be called as part of the self._handle_ws task
            self._task_manager.ensure_running_in_task_manager()
        ws = self._ws
        if ws is None:
            # Assume app is shutting down and the owning task has already been cancelled
            return
        try:
            return await ws.receive_json()
        except Exception as exc:
            err = LMStudioWebsocket._get_rx_error(exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _authenticate(self) -> bool:
        # This is only called if the websocket has been created
        if __debug__:
            # This should only be called as part of the self._handle_ws task
            self._task_manager.ensure_running_in_task_manager()
        ws = self._ws
        if ws is None:
            # Assume app is shutting down and the owning task has already been cancelled
            return False
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
        if __debug__:
            # This should only be called as part of the self._handle_ws task
            self._task_manager.ensure_running_in_task_manager()
        ws = self._ws
        if ws is None:
            # Assume app is shutting down and the owning task has already been cancelled
            return False
        message = await ws.receive_json()
        return await self._enqueue_message(message)

    async def _receive_messages(self) -> None:
        """Process received messages until task is cancelled."""
        while True:
            try:
                await self._process_next_message()
            except (LMStudioWebsocketError, HTTPXWSException):
                if self._ws is not None and not self._ws_disconnected.is_set():
                    # Websocket failed unexpectedly (rather than due to client shutdown)
                    self._logger.error("Websocket failed, terminating session.")
                break

    async def _enqueue_message(self, message: Any) -> bool:
        if message is None:
            self._logger.info(f"Websocket session failed ({self._ws_url})")
            self._ws = None
            return await self.notify_client_termination() > 0
        rx_queue = self._mux.map_rx_message(message)
        if rx_queue is None:
            return False
        await rx_queue.put(message)
        return True

    async def notify_client_termination(self) -> int:
        """Send None to all clients with open receive queues (from background thread)."""
        num_clients = 0
        for rx_queue in self._mux.all_queues():
            await rx_queue.put(None)
            num_clients += 1
        self._logger.debug(
            f"Notified {num_clients} clients of websocket termination",
            num_clients=num_clients,
        )
        return num_clients

    def notify_client_termination_threadsafe(self) -> int:
        """Send None to all clients with open receive queues (from foreground thread)."""
        return self.run_background_coroutine(self.notify_client_termination())
