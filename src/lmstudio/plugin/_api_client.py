"""Plugin API client implementation."""

# Plugins are expected to maintain multiple concurrently open channels and handle
# multiple concurrent server requests, so plugin implementations are always async

import asyncio
import os
import warnings

from functools import partial
from typing import Iterable, TypeAlias, assert_never

from anyio import create_task_group

from ..schemas import DictObject, EmptyDict
from ..async_api import AsyncClient, AsyncSession
from ..json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    LMStudioChannelClosedError,
)
from .._sdk_models import (
    # TODO: Define aliases at schema generation time
    # PluginsChannelSetGeneratorToClientPacketAbort as TokenGenerationAbort,
    # PluginsChannelSetGeneratorToClientPacketAbortDict as TokenGenerationAbortDict,
    # PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    # PluginsChannelSetGeneratorToClientPacketGenerateDict as TokenGenerationRequestDict,
    # PluginsChannelSetGeneratorToServerPacketAborted as TokenGenerationAborted,
    # PluginsChannelSetGeneratorToServerPacketAbortedDict as TokenGenerationAbortedDict,
    # PluginsChannelSetGeneratorToServerPacketComplete as TokenGenerationComplete,
    # PluginsChannelSetGeneratorToServerPacketCompleteDict as TokenGenerationCompleteDict,
    # PluginsChannelSetGeneratorToServerPacketError as TokenGenerationError,
    # PluginsChannelSetGeneratorToServerPacketErrorDict as TokenGenerationErrorDict,
    # PluginsChannelSetGeneratorToServerPacketFragmentGenerated as TokenGenerationFragment,
    # PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict as TokenGenerationFragmentDict,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated as ToolCallGenerationFragment,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict as ToolCallGenerationFragmentDict,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded as ToolCallGenerationEnded,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict as ToolCallGenerationEndedDict,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed as ToolCallGenerationFailed,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict as ToolCallGenerationFailedDict,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived as ToolCallGenerationNameReceived,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict as ToolCallGenerationNameReceivedDict,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted as ToolCallGenerationStarted,
    # PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict as ToolCallGenerationStartedDict,
    PluginsChannelSetPromptPreprocessorToClientPacketPreprocess as PromptPreprocessingRequest,
    # PluginsChannelSetPromptPreprocessorToServerPacketAbortedDict as PromptPreprocessingAbortedDict,
    PluginsChannelSetPromptPreprocessorToServerPacketCompleteDict as PromptPreprocessingCompleteDict,
    # PluginsChannelSetPromptPreprocessorToServerPacketErrorDict as PromptPreprocessingErrorDict,
    # PluginsChannelSetToolsProviderToClientPacketAbortToolCall as ProvideToolsAbort,
    # PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict as ProvideToolsAbortDict,
    # PluginsChannelSetToolsProviderToClientPacketCallTool as ProvideToolsCallRequest,
    # PluginsChannelSetToolsProviderToClientPacketCallToolDict as ProvideToolsCallRequestDict,
    # PluginsChannelSetToolsProviderToClientPacketDiscardSession as ProvideToolsDiscardSession,
    # PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict as ProvideToolsDiscardSessionDict,
    # PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    # PluginsChannelSetToolsProviderToClientPacketInitSessionDict as ProvideToolsInitSessionDict,
    # PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed as ProvideToolsSessionInitFailed,
    # PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict as ProvideToolsSessionInitFailedDict,
    # PluginsChannelSetToolsProviderToServerPacketSessionInitialized as ProvideToolsSessionInitialized,
    # PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict as ProvideToolsSessionInitializedDict,
    # PluginsChannelSetToolsProviderToServerPacketToolCallComplete as ProvideToolsCallComplete,
    # PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict as ProvideToolsCallCompleteDict,
    # PluginsChannelSetToolsProviderToServerPacketToolCallError as ProvideToolsCallError,
    # PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict as ProvideToolsCallErrorDict,
    # PluginsChannelSetToolsProviderToServerPacketToolCallStatus as ProvideToolsCallStatus,
    # PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict as ProvideToolsCallStatusDict,
    # PluginsChannelSetToolsProviderToServerPacketToolCallWarn as ProvideToolsCallWarn,
    # PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict as ProvideToolsCallWarnDict,
    TextDataDict,
)


# Warn about the plugin API stability, since it is still experimental
_PLUGIN_API_STABILITY_WARNING = """\
Note the plugin API is not yet stable and may change without notice in future releases
"""


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


class PluginClient(AsyncClient):
    def __init__(
        self, client_id: str | None = None, client_key: str | None = None
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

    _ALL_SESSIONS = (
        # Possible TODO: add other sessions here if necessary
        # *ASyncSession._ALL_SESSIONS,
        AsyncSessionPlugins,
    )

    def _create_auth_message(self) -> DictObject:
        """Create an LM Studio websocket authentication message."""
        if self._client_id is None or self._client_key is None:
            return super()._create_auth_message()
        # Use plugin credentials to unlock the full plugin client API
        return {
            "authVersion": 1,
            "clientIdentifier": self._client_id,
            "clientPasskey": self._client_key,
        }

    @property
    def plugins(self) -> AsyncSessionPlugins:
        """Return the plugins API client session."""
        return self._get_session(AsyncSessionPlugins)

    async def run_hook_prompt_preprocessor(self) -> bool:
        """Accept prompt preprocessing requests."""
        hook_ready_event = self._hook_ready_events["prompt_preprocessor"]
        # TODO: Retrieve hook definition from plugin
        hook_defined = True
        if not hook_defined:
            hook_ready_event.set()
            return False
        endpoint = PromptPreprocessingEndpoint()
        async with self.plugins._create_channel(endpoint) as channel:
            hook_ready_event.set()
            async for contents in channel.rx_stream():
                for event in endpoint.iter_message_events(contents):
                    endpoint.handle_rx_event(event)
                    # TODO: Dispatch to plugin defined prompt processing hook
                    match event:
                        case PromptPreprocessingRequestEvent():
                            request = event.arg
                            response = request.input.to_dict()
                            if response["role"] == "user":
                                # Add a prefix to all user messages
                                prefix: TextDataDict = {
                                    "type": "text",
                                    "text": "And now for something completely different:",
                                }
                                response["content"] = [prefix, *response["content"]]
                            await channel.send_message(
                                PromptPreprocessingCompleteDict(
                                    type="complete",
                                    taskId=request.task_id,
                                    processed=response,
                                )
                            )
                if endpoint.is_finished:
                    break
        return True

    async def run_hook_token_generator(self) -> bool:
        """Accept token generation requests."""
        hook_ready_event = self._hook_ready_events["token_generator"]
        # TODO: Retrieve hook definition from plugin
        hook_defined = False
        if not hook_defined:
            # Plugin doesn't define this hook -> nothing to be set up
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined token generation hook
        return True

    async def run_hook_tools_provider(self) -> bool:
        """Accept token generation requests."""
        # TODO: Retrieve hook definition from plugin
        hook_ready_event = self._hook_ready_events["tools_provider"]
        hook_defined = False
        if not hook_defined:
            # Plugin doesn't define this hook -> nothing to be set up
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined tools provision hook
        return True

    async def run_plugin(self, plugin_path: str | os.PathLike[str]) -> int:
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        print("Running example plugin")
        async with create_task_group() as tg:
            tg.start_soon(self.run_hook_prompt_preprocessor)
            tg.start_soon(self.run_hook_token_generator)
            tg.start_soon(self.run_hook_tools_provider)
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


async def run_plugin_async(plugin_path: str | os.PathLike[str]) -> int:
    """Asynchronously execute a plugin in development mode."""
    try:
        client_id, client_key = get_plugin_credentials_from_env()
    except KeyError:
        print(
            f"ERROR: {ENV_CLIENT_ID} and {ENV_CLIENT_KEY} must both be set in the environment"
        )
        return 1
    async with PluginClient(client_id, client_key) as plugin_client:
        return await plugin_client.run_plugin(plugin_path)


def run_plugin(plugin_path: str | os.PathLike[str]) -> int:
    """Execute a plugin in application mode."""
    return asyncio.run(run_plugin_async(plugin_path))
