"""Plugin dev client implementation."""

import asyncio
import os
import subprocess
import sys

from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator, Iterable, TypeAlias, assert_never

from ._api_client import (
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

    def __init__(self) -> None:
        # TODO: Set "python" as the type once LM Studio supports that
        # TODO: Accept plugin name and owner info as parameters
        params = DevPluginRegistrationRequest._from_api_dict(
            {
                "manifest": {
                    "type": "plugin",
                    "runner": "node",
                    "owner": "ancoghlan",
                    "name": "example-plugin",
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
        return DevPluginRegistrationEndpoint()

    @asynccontextmanager
    async def register_dev_plugin(self) -> AsyncGenerator[tuple[str, str], None]:
        """Register a dev plugin on entry, deregister it on exit."""
        endpoint = self._get_registration_endpoint()
        async with self.plugins._create_channel(endpoint) as channel:
            try:
                yield await channel.wait_for_result()
            finally:
                message: DevPluginRegistrationEndDict = {"type": "end"}
                await channel.send_message(message)

    async def run_plugin(self, plugin_path: str | os.PathLike[str]) -> int:
        async with self.register_dev_plugin() as (client_id, client_key):
            result = await asyncio.to_thread(
                partial(
                    _run_plugin_in_child_process, plugin_path, client_id, client_key
                )
            )
            result.check_returncode()
            return result.returncode


# TODO: support the same subprocess monitoring features as `lms dev`
def _run_plugin_in_child_process(
    plugin_path: str | os.PathLike[str], client_id: str, client_key: str
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env[ENV_CLIENT_ID] = client_id
    env[ENV_CLIENT_KEY] = client_key
    package_name = __spec__.parent
    assert package_name is not None
    command: list[str] = [
        sys.executable,
        "-m",
        package_name,
        os.fspath(plugin_path),
    ]
    return subprocess.run(command, text=True, env=env)


async def run_plugin_async(plugin_path: str | os.PathLike[str]) -> int:
    """Asynchronously execute a plugin in development mode."""
    async with DevPluginClient() as dev_client:
        return await dev_client.run_plugin(plugin_path)


def run_plugin(plugin_path: str | os.PathLike[str]) -> int:
    """Execute a plugin in development mode."""
    return asyncio.run(run_plugin_async(plugin_path))
