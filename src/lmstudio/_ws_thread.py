"""Background thread async websocket implementation for the LM Studio remote access API."""

# Sync API
# Async convenience API (once implemented)

import asyncio
import threading
import weakref

from contextlib import contextmanager
from typing import (
    Any,
    Coroutine,
    Callable,
    Generator,
    TypeAlias,
    TypeVar,
)

from httpx_ws import AsyncWebSocketSession

from .schemas import DictObject

from ._logging import new_logger, LogEventContext
from ._ws_impl import AsyncTaskManager, AsyncWebsocketHandler

# Allow the core client websocket management to be shared across all SDK interaction APIs
# See https://discuss.python.org/t/daemon-threads-and-background-task-termination/77604
# (Note: this implementation has the elements needed to run on *current* Python versions
# and omits the generalised features that the SDK doesn't need)
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
        self._loop_started = loop_started = threading.Event()
        self._task_manager = AsyncTaskManager(on_activation=loop_started.set)
        # Annoyingly, we have to mark the background thread as a daemon thread to
        # prevent hanging at shutdown. Even checking `sys.is_finalizing()` is inadequate
        # https://discuss.python.org/t/should-sys-is-finalizing-report-interpreter-finalization-instead-of-runtime-finalization/76695
        # TODO: skip thread daemonization when running in a subinterpreter
        # (and also disable the convenience API in subinterpreters to avoid hanging on shutdown)
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


# By default, the weakref finalization atexit hook is registered lazily.
# This can lead to shutdown sequencing issues if SDK users attempt to access
# client instances (such as the default sync client) from atexit hooks
# registered at import time (so they may end up running after the weakref
# finalization hook has already terminated background threads)
# Creating this finalizer here ensures the weakref finalization hook is
# registered at import time, and hence runs *after* any such hooks
# (assuming the lmstudio SDK is imported before the hooks are registered)
def _register_weakref_atexit_hook() -> None:
    class C:
        pass

    weakref.finalize(C(), int)


_register_weakref_atexit_hook()
del _register_weakref_atexit_hook


class AsyncWebsocketThread(BackgroundThread):
    def __init__(self, log_context: LogEventContext | None = None) -> None:
        super().__init__(task_target=self._log_thread_execution)
        self._logger = logger = new_logger(type(self).__name__)
        logger.update_context(log_context, thread_id=self.name)

    async def _log_thread_execution(self) -> None:
        self._logger.info("Websocket handling thread started")
        never_set = asyncio.Event()
        try:
            # Run the event loop until termination is requested
            await never_set.wait()
        except (asyncio.CancelledError, GeneratorExit):
            raise
        except BaseException:
            err_msg = "Terminating websocket thread due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            self._logger.info("Websocket thread terminated")


SyncChannelInfo: TypeAlias = tuple[int, Callable[[float | None], Any]]
SyncRemoteCallInfo: TypeAlias = tuple[int, Callable[[float | None], Any]]


class SyncToAsyncWebsocketBridge:
    def __init__(
        self,
        ws_thread: AsyncWebsocketThread,
        ws_url: str,
        auth_details: DictObject,
        log_context: LogEventContext,
    ) -> None:
        self._ws_handler = AsyncWebsocketHandler(
            ws_thread.task_manager,
            ws_url,
            auth_details,
            log_context,
        )
        self._logger = logger = new_logger(type(self).__name__)
        logger.update_context(log_context)

    def connect(self) -> bool:
        return self._ws_handler.connect_threadsafe()

    def disconnect(self) -> None:
        self._ws_handler.disconnect_threadsafe()

    def send_json(self, message: DictObject) -> None:
        self._ws_handler.send_json_threadsafe(message)

    @contextmanager
    def open_channel(self) -> Generator[SyncChannelInfo, None, None]:
        ws_handler = self._ws_handler
        rx_queue, getter = ws_handler.new_threadsafe_rx_queue()
        channel_id = ws_handler.acquire_channel_id_threadsafe(rx_queue)
        try:
            yield channel_id, getter
        finally:
            ws_handler.release_channel_id_threadsafe(channel_id, rx_queue)

    @contextmanager
    def start_call(self) -> Generator[SyncRemoteCallInfo, None, None]:
        ws_handler = self._ws_handler
        rx_queue, getter = ws_handler.new_threadsafe_rx_queue()
        call_id = ws_handler.acquire_call_id_threadsafe(rx_queue)
        try:
            yield call_id, getter
        finally:
            ws_handler.release_call_id_threadsafe(call_id, rx_queue)

    def notify_client_termination_threadsafe(self) -> int:
        """Send None to all clients with open receive queues (from foreground thread)."""
        return self._ws_handler.notify_client_termination_threadsafe()

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
