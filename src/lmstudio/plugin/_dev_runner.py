"""Plugin dev client implementation."""

import asyncio
import io
import os
import signal
import subprocess
import sys

from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from threading import Event as SyncEvent
from typing import Any, AsyncGenerator, Iterable, TypeAlias

from typing_extensions import (
    # Native in 3.11+
    assert_never,
)

from .runner import (
    ENV_CLIENT_ID,
    ENV_CLIENT_KEY,
    PluginClient,
)
from ..schemas import DictObject
from ..json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    LMStudioChannelClosedError,
)
from .._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelRegisterDevelopmentPluginCreationParameter as DevPluginRegistrationRequest,
    PluginsChannelRegisterDevelopmentPluginCreationParameterDict as DevPluginRegistrationRequestDict,
    PluginsChannelRegisterDevelopmentPluginToServerPacketEndDict as DevPluginRegistrationEndDict,
)


class DevPluginRegistrationReadyEvent(ChannelRxEvent[None]):
    pass


DevPluginRegistrationRxEvent: TypeAlias = (
    DevPluginRegistrationReadyEvent | ChannelCommonRxEvent
)


class DevPluginRegistrationEndpoint(
    ChannelEndpoint[
        tuple[str, str], DevPluginRegistrationRxEvent, DevPluginRegistrationRequestDict
    ]
):
    """API channel endpoint to register a development plugin and receive credentials."""

    _API_ENDPOINT = "registerDevelopmentPlugin"
    _NOTICE_PREFIX = "Register development plugin"

    def __init__(self, owner: str, name: str) -> None:
        # TODO: Set "python" as the type once LM Studio supports that
        params = DevPluginRegistrationRequest._from_api_dict(
            {
                "manifest": {
                    "type": "plugin",
                    "runner": "node",
                    "owner": owner,
                    "name": name,
                }
            }
        )
        super().__init__(params)

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[DevPluginRegistrationRxEvent]:
        match contents:
            case None:
                raise LMStudioChannelClosedError(
                    "Server failed to complete development plugin registration."
                )
            case {
                "type": "ready",
                "clientIdentifier": str(client_id),
                "clientPasskey": str(client_key),
            }:
                yield self._set_result((client_id, client_key))
            case unmatched:
                self.report_unknown_message(unmatched)

    def handle_rx_event(self, event: DevPluginRegistrationRxEvent) -> None:
        match event:
            case DevPluginRegistrationReadyEvent(_):
                pass
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)


class DevPluginClient(PluginClient):
    def _get_registration_endpoint(self) -> DevPluginRegistrationEndpoint:
        return DevPluginRegistrationEndpoint(self.owner, self.name)

    @asynccontextmanager
    async def register_dev_plugin(self) -> AsyncGenerator[tuple[str, str], None]:
        """Register a dev plugin on entry, deregister it on exit."""
        endpoint = self._get_registration_endpoint()
        async with self.plugins._create_channel(endpoint) as channel:
            registration_result = await channel.wait_for_result()
            try:
                yield registration_result
            finally:
                message: DevPluginRegistrationEndDict = {"type": "end"}
                await channel.send_message(message)

    async def _run_plugin_task(
        self, result_queue: asyncio.Queue[int], debug: bool = False
    ) -> None:
        notify_subprocess_thread = SyncEvent()
        async with self.register_dev_plugin() as (client_id, client_key):
            wait_for_subprocess = asyncio.ensure_future(
                asyncio.to_thread(
                    partial(
                        _run_plugin_in_child_process,
                        self._plugin_path,
                        client_id,
                        client_key,
                        notify_subprocess_thread,
                        debug=debug,
                    )
                )
            )
            try:
                result = await wait_for_subprocess
            except asyncio.CancelledError:
                # Likely a Ctrl-C press, which is the expected termination process
                notify_subprocess_thread.set()
                result_queue.put_nowait(0)
                raise
            # Subprocess terminated, pass along its return code in the parent process
            await result_queue.put(result)

    async def run_plugin(
        self, *, allow_local_imports: bool = True, debug: bool = False
    ) -> int:
        if not allow_local_imports:
            raise ValueError("Local imports are always permitted for dev plugins")
        result_queue: asyncio.Queue[int] = asyncio.Queue()
        # Run in the task manager, so this gets cleaned up before the websocket handler
        await self._task_manager.schedule_task(
            partial(self._run_plugin_task, result_queue, debug)
        )
        return await result_queue.get()


def _get_creation_flags() -> int:
    if sys.platform == "win32":
        return subprocess.CREATE_NEW_PROCESS_GROUP
    return 0


def _start_child_process(
    command: list[str], *, text: bool | None = True, **kwds: Any
) -> subprocess.Popen[str]:
    creationflags = kwds.pop("creationflags", 0)
    creationflags |= _get_creation_flags()
    return subprocess.Popen(command, text=text, creationflags=creationflags, **kwds)


def _get_interrupt_signal() -> signal.Signals:
    if sys.platform == "win32":
        return signal.CTRL_C_EVENT
    return signal.SIGINT


_PLUGIN_INTERRUPT_SIGNAL = _get_interrupt_signal()
_PLUGIN_STATUS_POLL_INTERVAL = 1
_PLUGIN_STOP_TIMEOUT = 2


def _interrupt_child_process(process: subprocess.Popen[Any], timeout: float) -> int:
    process.send_signal(_PLUGIN_INTERRUPT_SIGNAL)
    try:
        return process.wait(timeout)
    except TimeoutError:
        process.kill()
        raise


# TODO: support the same source code change monitoring features as `lms dev`
def _run_plugin_in_child_process(
    plugin_path: Path,
    client_id: str,
    client_key: str,
    abort_event: SyncEvent,
    *,
    debug: bool = False,
) -> int:
    env = os.environ.copy()
    env[ENV_CLIENT_ID] = client_id
    env[ENV_CLIENT_KEY] = client_key
    package_name = __spec__.parent
    assert package_name is not None
    debug_option = ("--debug",) if debug else ()
    # If stdout is unbuffered, specify the same in the child process
    stdout = sys.__stdout__
    unbuffered_arg: tuple[str, ...]
    if stdout is None or not isinstance(stdout.buffer, io.BufferedWriter):
        unbuffered_arg = ("-u",)
    else:
        unbuffered_arg = ()

    command: list[str] = [
        sys.executable,
        *unbuffered_arg,
        "-m",
        package_name,
        *debug_option,
        os.fspath(plugin_path),
    ]
    process = _start_child_process(command, env=env)
    while True:
        result = process.poll()
        if result is not None:
            print("Child process terminated unexpectedly")
            break
        if abort_event.wait(_PLUGIN_STATUS_POLL_INTERVAL):
            print("Gracefully terminating child process...")
            result = _interrupt_child_process(process, _PLUGIN_STOP_TIMEOUT)
            break
    return result


async def run_plugin_async(
    plugin_dir: str | os.PathLike[str], *, debug: bool = False
) -> int:
    """Asynchronously execute a plugin in development mode."""
    async with DevPluginClient(plugin_dir) as dev_client:
        return await dev_client.run_plugin(debug=debug)


def run_plugin(plugin_dir: str | os.PathLike[str], *, debug: bool = False) -> int:
    """Execute a plugin in development mode."""
    return asyncio.run(run_plugin_async(plugin_dir, debug=debug))
