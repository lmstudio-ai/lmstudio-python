"""Plugin API client implementation."""

# Plugins are expected to maintain multiple concurrently open channels and handle
# multiple concurrent server requests, so plugin implementations are always async

import asyncio
import json
import os
import runpy
import sys
import warnings

from datetime import datetime, UTC
from functools import partial
from pathlib import Path
from random import randrange
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    TypeAlias,
    TypeVar,
    assert_never,
)

from anyio import create_task_group

from ..schemas import DictObject, EmptyDict
from ..history import AnyChatMessage, AnyChatMessageDict
from ..json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    LMStudioChannelClosedError,
    ToolDefinition,
)
from ..async_api import AsyncClient, AsyncSession
from .._kv_config import dict_from_kvconfig
from .._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    PluginsRpcProcessingHandleUpdateParameter,
    PluginsRpcSetConfigSchematicsParameter,
    ProcessingUpdate,
    ProcessingUpdateDebugInfoBlockCreate,
    ProcessingUpdateStatusCreate,
    PromptPreprocessingRequest,
    PromptPreprocessingCompleteDict,
    StatusStepState,
)
from .sdk_api import LMStudioPluginInitError
from .config_schemas import BaseConfigSchema

__all__ = [
    "PromptPreprocessorController",
]

# Warn about the plugin API stability, since it is still experimental
_PLUGIN_API_STABILITY_WARNING = """\
Note the plugin API is not yet stable and may change without notice in future releases
"""

# TODO: Separate out the specifics of each hook channel to dedicated submodules


class PromptPreprocessingAbortEvent(ChannelRxEvent[str]):
    pass


class PromptPreprocessingRequestEvent(ChannelRxEvent[PromptPreprocessingRequest]):
    pass


PromptPreprocessingRxEvent: TypeAlias = (
    PromptPreprocessingAbortEvent
    | PromptPreprocessingRequestEvent
    | ChannelCommonRxEvent
)


class PromptPreprocessingEndpoint(
    ChannelEndpoint[tuple[str, str], PromptPreprocessingRxEvent, EmptyDict]
):
    """API channel endpoint to register a development plugin and receive credentials."""

    _API_ENDPOINT = "setPromptPreprocessor"
    _NOTICE_PREFIX = "Prompt preprocessing"

    def __init__(self) -> None:
        super().__init__({})

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[PromptPreprocessingRxEvent]:
        match contents:
            case None:
                raise LMStudioChannelClosedError(
                    "Server failed to complete development plugin registration."
                )
            case {"type": "abort", "task_id": str(task_id)}:
                yield PromptPreprocessingAbortEvent(task_id)
            case {"type": "preprocess"} as request_dict:
                parsed_request = PromptPreprocessingRequest._from_any_api_dict(
                    request_dict
                )
                yield PromptPreprocessingRequestEvent(parsed_request)
            case unmatched:
                self.report_unknown_message(unmatched)

    def handle_rx_event(self, event: PromptPreprocessingRxEvent) -> None:
        match event:
            case PromptPreprocessingAbortEvent(task_id):
                self._logger.info(f"Aborting {task_id}", task_id=task_id)
            case PromptPreprocessingRequestEvent(request):
                task_id = request.task_id
                self._logger.info(
                    "Received prompt preprocessing request", task_id=task_id
                )
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)


class AsyncSessionPlugins(AsyncSession):
    """Async client session for the plugins namespace."""

    API_NAMESPACE = "plugins"


PluginRequest: TypeAlias = (
    PromptPreprocessingRequest | TokenGenerationRequest | ProvideToolsInitSession
)
TPluginRequest = TypeVar("TPluginRequest", bound=PluginRequest)


class HookController(Generic[TPluginRequest]):
    """Common base class for plugin hook API access controllers."""

    def __init__(
        self,
        session: AsyncSessionPlugins,
        request: TPluginRequest,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> None:
        """Initialize common hook controller settings."""
        self.session = session
        self.plugin_config = (
            plugin_config._parse(request.plugin_config) if plugin_config else {}
        )
        self.global_config = dict_from_kvconfig(request.global_plugin_config)
        work_dir = request.working_directory_path
        self.working_path = Path(work_dir) if work_dir else None


class PromptPreprocessorController(HookController[PromptPreprocessingRequest]):
    """API access for prompt preprocessor hook implementations."""

    def __init__(
        self,
        session: AsyncSessionPlugins,
        request: PromptPreprocessingRequest,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> None:
        """Initialize prompt preprocessor hook controller."""
        super().__init__(session, request, plugin_config)
        self._tbd_config = dict_from_kvconfig(request.config)  # TODO: check contents
        self.pci = request.pci
        self.token = request.token

    @classmethod
    def _create_block_id(self) -> str:
        return f"{datetime.now(UTC)}-{randrange(-sys.maxsize, sys.maxsize)}"

    async def _send_handle_update(self, update: ProcessingUpdate) -> Any:
        handle_update = PluginsRpcProcessingHandleUpdateParameter(
            pci=self.pci,
            token=self.token,
            update=update,
        )
        return await self.session.remote_call("processingHandleUpdate", handle_update)

    # TODO: Provide a structured API for manipulating UI status blocks in-place
    async def notify_done(self, message: str) -> None:
        """Report task completion in a new UI status block."""
        await self._send_handle_update(
            ProcessingUpdateStatusCreate(
                id=self._create_block_id(),
                state=StatusStepState(
                    status="done",
                    text=message,
                ),
            ),
        )


PromptPreprocessorHook = Callable[
    [PromptPreprocessorController, AnyChatMessage], Awaitable[AnyChatMessageDict | None]
]


class TokenGeneratorController(HookController[TokenGenerationRequest]):
    """API access for token generator hook implementations."""


TokenGeneratorHook = Callable[[TokenGeneratorController], Awaitable[None]]


class ToolsProviderController(HookController[ProvideToolsInitSession]):
    """API access for tools provider hook implementations."""


ToolsProviderHook = Callable[
    [ToolsProviderController], Awaitable[Iterable[ToolDefinition]]
]


class PluginClient(AsyncClient):
    def __init__(
        self,
        plugin_dir: str | os.PathLike[str],
        client_id: str | None = None,
        client_key: str | None = None,
    ) -> None:
        warnings.warn(_PLUGIN_API_STABILITY_WARNING, FutureWarning)
        self._client_id = client_id
        self._client_key = client_key
        super().__init__()
        self._hook_ready_events = {
            "prompt_preprocessor": asyncio.Event(),
            "token_generator": asyncio.Event(),
            "tools_provider": asyncio.Event(),
        }
        # TODO: Nicer error handling, move file reading to class method and make this a data class
        self._plugin_path = plugin_path = Path(plugin_dir)
        manifest_path = plugin_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["type"] != "plugin":
            raise LMStudioPluginInitError(f"Invalid manifest type: {manifest['type']}")
        if (
            manifest["runner"] != "node"
        ):  # TODO: Change to "python" once that is supported
            raise LMStudioPluginInitError(
                f"Invalid manifest runner: {manifest['runner']}"
            )
        self._owner = manifest["owner"]
        self._name = manifest["name"]

    _ALL_SESSIONS = (
        # Possible TODO: add other sessions here if
        # necessary for controller implementations
        # *ASyncSession._ALL_SESSIONS,
        AsyncSessionPlugins,
    )

    def _create_auth_message(self) -> DictObject:
        """Create an LM Studio websocket authentication message."""
        if self._client_id is None or self._client_key is None:
            return super()._create_auth_message()
        # Use plugin credentials to unlock the full plugin client API
        return self._format_auth_message(self._client_id, self._client_key)

    @property
    def plugins(self) -> AsyncSessionPlugins:
        """Return the plugins API client session."""
        return self._get_session(AsyncSessionPlugins)

    async def run_hook_prompt_preprocessor(
        self,
        hook_impl: PromptPreprocessorHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept prompt preprocessing requests."""
        hook_ready_event = self._hook_ready_events["prompt_preprocessor"]
        if hook_impl is None:
            print("No hook defined for prompt preprocessing requests")
            hook_ready_event.set()
            return False
        endpoint = PromptPreprocessingEndpoint()
        session = self.plugins
        async with session._create_channel(endpoint) as channel:
            hook_ready_event.set()
            print("Opened channel to receive prompt preprocessing requests...")

            async def _invoke_hook(request: PromptPreprocessingRequest) -> None:
                message = request.input
                hook_controller = PromptPreprocessorController(
                    session, request, plugin_config
                )
                # TODO once stable: use sdk_api_callback context manager
                response = await hook_impl(hook_controller, message)
                if response is None:
                    response = message.to_dict()
                await channel.send_message(
                    PromptPreprocessingCompleteDict(
                        type="complete",
                        taskId=request.task_id,
                        processed=response,
                    )
                )

            async with create_task_group() as tg:
                print("Waiting for prompt preprocessing requests...")
                async for contents in channel.rx_stream():
                    print(f"Handling prompt preprocessing channel message: {contents}")
                    for event in endpoint.iter_message_events(contents):
                        print("Handling prompt preprocessing channel event")
                        endpoint.handle_rx_event(event)
                        match event:
                            case PromptPreprocessingRequestEvent():
                                print("Running prompt preprocessing request hook")
                                tg.start_soon(_invoke_hook, event.arg)
                    if endpoint.is_finished:
                        break
        return True

    async def run_hook_token_generator(
        self,
        hook_impl: TokenGeneratorHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept token generation requests."""
        hook_ready_event = self._hook_ready_events["token_generator"]
        if hook_impl is None:
            print("No hook defined for token generation requests")
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined token generation hook
        return True

    async def run_hook_tools_provider(
        self,
        hook_impl: ToolsProviderHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept tools provider requests."""
        # TODO: Retrieve hook definition from plugin
        hook_ready_event = self._hook_ready_events["tools_provider"]
        if hook_impl is None:
            print("No hook defined for tools provider requests")
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined tools provision hook
        return True

    # TODO: Cleanup the assorted debugging prints (either remove or migrate to logging)
    async def run_plugin(self, *, allow_local_imports: bool = False) -> int:
        # TODO: Nicer error handling
        source_path = self._plugin_path / "src"
        plugin_path = source_path / "plugin.py"
        if not plugin_path.exists():
            raise FileNotFoundError(plugin_path)
        print(f"Running {plugin_path}")
        if allow_local_imports:
            # We don't try to revert the path change, as that can have odd side-effects
            sys.path.insert(0, str(source_path))
        plugin_ns = runpy.run_path(str(plugin_path), run_name="__lms_plugin__")
        prompt_preprocessor: PromptPreprocessorHook | None = plugin_ns.get(
            "preprocess_prompt", None
        )
        config_schema: type[BaseConfigSchema] | None = plugin_ns.get(
            "ConfigSchema", None
        )
        if config_schema is not None:
            if not issubclass(config_schema, BaseConfigSchema):
                raise LMStudioPluginInitError(
                    f"Expected {BaseConfigSchema!r} subclass definition, not {config_schema!r}"
                )
            await self.plugins.remote_call(
                "setConfigSchematics",
                PluginsRpcSetConfigSchematicsParameter(
                    schematics=config_schema._to_kv_config_schematics(),
                ),
            )
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        async with create_task_group() as tg:
            tg.start_soon(
                self.run_hook_prompt_preprocessor, prompt_preprocessor, config_schema
            )
            tg.start_soon(self.run_hook_token_generator, None, config_schema)
            tg.start_soon(self.run_hook_tools_provider, None, config_schema)
            # Should this have a time limit set to guard against SDK bugs?
            await asyncio.gather(*(e.wait() for e in self._hook_ready_events.values()))
            await self.plugins.remote_call("pluginInitCompleted")
            # Indicate that prompt processing is ready
            # Terminate all running tasks when termination is requested
            try:
                await asyncio.to_thread(partial(input, "Press Enter to terminate..."))
            finally:
                tg.cancel_scope.cancel()
        return 0


ENV_CLIENT_ID = "LMS_PLUGIN_CLIENT_IDENTIFIER"
ENV_CLIENT_KEY = "LMS_PLUGIN_CLIENT_PASSKEY"


def get_plugin_credentials_from_env() -> tuple[str, str]:
    return os.environ[ENV_CLIENT_ID], os.environ[ENV_CLIENT_KEY]


async def run_plugin_async(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> int:
    """Asynchronously execute a plugin in development mode."""
    try:
        client_id, client_key = get_plugin_credentials_from_env()
    except KeyError:
        print(
            f"ERROR: {ENV_CLIENT_ID} and {ENV_CLIENT_KEY} must both be set in the environment"
        )
        return 1
    async with PluginClient(plugin_dir, client_id, client_key) as plugin_client:
        return await plugin_client.run_plugin(allow_local_imports=allow_local_imports)


def run_plugin(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> int:
    """Execute a plugin in application mode."""
    return asyncio.run(
        run_plugin_async(plugin_dir, allow_local_imports=allow_local_imports)
    )
