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
    asynccontextmanager,
    AsyncExitStack,
)
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Coroutine,
    Callable,
    NoReturn,
    TypeVar,
)

# Synchronous API still uses an async websocket (just in a background thread)
from anyio import create_task_group
from exceptiongroup import suppress
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
        self._loop_started = threading.Event()
        self._terminate = asyncio.Event()
        self._event_loop: asyncio.AbstractEventLoop | None = None
        # Annoyingly, we have to mark the background thread as a daemon thread to
        # prevent hanging at shutdown. Even checking `sys.is_finalizing()` is inadequate
        # https://discuss.python.org/t/should-sys-is-finalizing-report-interpreter-finalization-instead-of-runtime-finalization/76695
        super().__init__(name=name, daemon=True)
        weakref.finalize(self, self.terminate)

    def run(self) -> None:
        """Run an async event loop in the background thread."""
        # Only public to override threading.Thread.run
        asyncio.run(self._run_until_terminated())

    def wait_for_loop(self) -> asyncio.AbstractEventLoop | None:
        """Wait for the event loop to start from a synchronous foreground thread."""
        if self._event_loop is None and not self._loop_started.is_set():
            self._loop_started.wait()
        return self._event_loop

    async def wait_for_loop_async(self) -> asyncio.AbstractEventLoop | None:
        """Wait for the event loop to start from an asynchronous foreground thread."""
        return await asyncio.to_thread(self.wait_for_loop)

    def called_in_background_loop(self) -> bool:
        """Returns true if currently running in this thread's event loop, false otherwise."""
        loop = self._event_loop
        if loop is None:
            # No loop active in background thread -> can't be running in it
            return False
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop in this thread -> can't be running in the background thread's loop
            return False
        # Otherwise, check if the running loop is the background thread's loop
        return running_loop is loop

    async def _request_termination(self) -> bool:
        assert self.called_in_background_loop()
        if self._terminate.is_set():
            return False
        self._terminate.set()
        return True

    def request_termination(self) -> SyncFuture[bool]:
        """Request termination of the event loop (without blocking)."""
        loop = self._event_loop
        if loop is None or self._terminate.is_set():
            result: SyncFuture[bool] = SyncFuture()
            result.set_result(False)
            return result
        return self.schedule_background_task(self._request_termination())

    def terminate(self) -> bool:
        """Request termination of the event loop from a synchronous foreground thread."""
        return self.request_termination().result()

    async def terminate_async(self) -> bool:
        """Request termination of the event loop from an asynchronous foreground thread."""
        return await asyncio.to_thread(self.terminate)

    async def _run_until_terminated(self) -> None:
        """Run task in the background thread until termination is requested."""
        self._event_loop = asyncio.get_running_loop()
        self._loop_started.set()
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        raise_on_termination, terminated_exc = self._raise_on_termination()
        with suppress(terminated_exc):
            try:
                async with create_task_group() as tg:
                    tg.start_soon(self._run_task_target)
                    tg.start_soon(raise_on_termination)
            finally:
                # Event loop is about to shut down
                self._event_loop = None

    async def _run_task_target(self) -> None:
        if self._task_target is not None:
            main_task = self._task_target()
            self._task_target = None
            await main_task

    def _raise_on_termination(
        self,
    ) -> tuple[Callable[[], Awaitable[NoReturn]], type[Exception]]:
        class TerminateTask(Exception):
            pass

        async def raise_on_termination() -> NoReturn:
            await self._terminate.wait()
            raise TerminateTask

        return raise_on_termination, TerminateTask

    def schedule_background_task(self, coro: Coroutine[Any, Any, T]) -> SyncFuture[T]:
        """Schedule given coroutine in the background event loop."""
        loop = self._event_loop
        assert loop is not None
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def run_background_task(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run given coroutine in the background event loop and wait for the result."""
        return self.schedule_background_task(coro).result()

    async def run_background_task_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run given coroutine in the background event loop and await the result."""
        return await asyncio.to_thread(self.run_background_task, coro)

    def call_in_background(self, callback: Callable[[], Any]) -> None:
        """Call given non-blocking function in the background event loop."""
        loop = self._event_loop
        assert loop is not None
        loop.call_soon_threadsafe(callback)


# TODO: Allow multiple websockets to share a single event loop thread
# (reduces thread usage in sync API, blocker for async API migration)
class AsyncWebsocketThread(BackgroundThread):
    def __init__(
        self,
        ws_url: str,
        auth_details: DictObject,
        enqueue_message: Callable[[DictObject], bool],
        log_context: LogEventContext,
    ) -> None:
        self._auth_details = auth_details
        self._connection_attempted = asyncio.Event()
        self._connection_failure: Exception | None = None
        self._auth_failure: Any | None = None
        self._terminate = asyncio.Event()
        self._ws_url = ws_url
        self._ws: AsyncWebSocketSession | None = None
        self._rx_task: asyncio.Task[None] | None = None
        self._queue_message = enqueue_message
        super().__init__(task_target=self._run_main_task)
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, thread_id=self.name)

    def connect(self) -> bool:
        if not self.is_alive():
            self.start()
        loop = self.wait_for_loop()  # Block until connection has been attempted
        if loop is None:
            return False
        asyncio.run_coroutine_threadsafe(
            self._connection_attempted.wait(), loop
        ).result()
        return self._ws is not None

    def disconnect(self) -> None:
        if self._ws is not None:
            self.terminate()
        # Ensure thread has terminated
        self.join()

    async def _run_main_task(self) -> None:
        self._logger.info("Websocket thread started")
        try:
            await self._main_task()
        except BaseException:
            err_msg = "Terminating websocket thread due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            # Ensure the foreground thread is unblocked even if the
            # background async task errors out completely
            self._connection_attempted.set()
        self._logger.info("Websocket thread terminated")

    # TODO: Improve code sharing between this background thread async websocket
    #       and the async-native AsyncLMStudioWebsocket implementation
    async def _main_task(self) -> None:
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
            del self._queue_message
            # Websocket is about to be disconnected
            self._ws = None

        resources.callback(_clear_task_state)
        async with resources:
            self._logger.debug("Websocket connected")
            self._ws = ws
            if not await self._authenticate():
                return
            async with self._manage_demultiplexing():
                self._connection_attempted.set()
                self._logger.info(f"Websocket session established ({self._ws_url})")
                # Keep the event loop alive until termination is requested
                await self._terminate.wait()

    async def _send_json(self, message: DictObject) -> None:
        # This is only called if the websocket has been created
        assert self.called_in_background_loop()
        ws = self._ws
        assert ws is not None
        try:
            await ws.send_json(message)
        except Exception as exc:
            err = LMStudioWebsocket._get_tx_error(message, exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _receive_json(self) -> Any:
        # This is only called if the websocket has been created
        assert self.called_in_background_loop()
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
        assert self.called_in_background_loop()
        ws = self._ws
        assert ws is not None
        auth_message = self._auth_details
        await self._send_json(auth_message)
        auth_result = await self._receive_json()
        self._logger.debug("Websocket authenticated", json=auth_result)
        if not auth_result["success"]:
            self._auth_failure = auth_result["error"]
            return False
        return True

    @asynccontextmanager
    async def _manage_demultiplexing(
        self,
    ) -> AsyncGenerator[asyncio.Task[None], None]:
        assert self.called_in_background_loop()
        self._rx_task = rx_task = asyncio.create_task(self._demultiplexing_task())
        try:
            yield rx_task
        finally:
            if rx_task.cancel():
                try:
                    await rx_task
                except asyncio.CancelledError:
                    pass

    async def _process_next_message(self) -> bool:
        """Process the next message received on the websocket.

        Returns True if a message queue was updated.
        """
        # This is only called if the websocket has been created
        assert self.called_in_background_loop()
        ws = self._ws
        assert ws is not None
        message = await ws.receive_json()
        return await asyncio.to_thread(self._queue_message, message)

    async def _demultiplexing_task(self) -> None:
        """Process received messages until connection is terminated."""
        try:
            await self._receive_messages()
        finally:
            self._logger.info("Websocket closed, terminating demultiplexing task.")

        raise_on_termination, terminated_exc = self._raise_on_termination()

    async def _receive_messages(self) -> None:
        """Process received messages until task is cancelled."""
        while True:
            try:
                await self._process_next_message()
            except (LMStudioWebsocketError, HTTPXWSException):
                if self._ws is not None:
                    # Websocket failed unexpectedly (rather than due to client shutdown)
                    self._logger.exception("Websocket failed, terminating session.")
                    self._terminate.set()
                break

    def send_json(self, message: DictObject) -> None:
        # Block until message has been sent
        self.run_background_task(self._send_json(message))
