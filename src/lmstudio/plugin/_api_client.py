"""Plugin API client implementation."""

# Plugins are expected to maintain multiple concurrently open channels and handle
# multiple concurrent server requests, so plugin implementations are always async

import os
import warnings

from ..schemas import DictObject
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
    PluginsChannelSetGeneratorToClientPacketAbort as TokenGenerationAbort,
    PluginsChannelSetGeneratorToClientPacketAbortDict as TokenGenerationAbortDict,
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    PluginsChannelSetGeneratorToClientPacketGenerateDict as TokenGenerationRequestDict,
    PluginsChannelSetGeneratorToServerPacketAborted as TokenGenerationAborted,
    PluginsChannelSetGeneratorToServerPacketAbortedDict as TokenGenerationAbortedDict,
    PluginsChannelSetGeneratorToServerPacketComplete as TokenGenerationComplete,
    PluginsChannelSetGeneratorToServerPacketCompleteDict as TokenGenerationCompleteDict,
    PluginsChannelSetGeneratorToServerPacketError as TokenGenerationError,
    PluginsChannelSetGeneratorToServerPacketErrorDict as TokenGenerationErrorDict,
    PluginsChannelSetGeneratorToServerPacketFragmentGenerated as TokenGenerationFragment,
    PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict as TokenGenerationFragmentDict,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated as ToolCallGenerationFragment,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict as ToolCallGenerationFragmentDict,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded as ToolCallGenerationEnded,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict as ToolCallGenerationEndedDict,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed as ToolCallGenerationFailed,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict as ToolCallGenerationFailedDict,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived as ToolCallGenerationNameReceived,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict as ToolCallGenerationNameReceivedDict,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted as ToolCallGenerationStarted,
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict as ToolCallGenerationStartedDict,
    PluginsChannelSetPromptPreprocessorToClientPacketAbort as PromptPreprocessingAbort,
    PluginsChannelSetPromptPreprocessorToClientPacketAbortDict as PromptPreprocessingAbortDict,
    PluginsChannelSetPromptPreprocessorToClientPacketPreprocess as PromptPreprocessingRequest,
    PluginsChannelSetPromptPreprocessorToClientPacketPreprocessDict as PromptPreprocessingRequestDict,
    PluginsChannelSetPromptPreprocessorToServerPacketAborted as PromptPreprocessingAbortedDict,
    PluginsChannelSetPromptPreprocessorToServerPacketAbortedDict as PromptPreprocessing,
    PluginsChannelSetPromptPreprocessorToServerPacketComplete as PromptPreprocessingComplete,
    PluginsChannelSetPromptPreprocessorToServerPacketCompleteDict as PromptPreprocessingCompleteDict,
    PluginsChannelSetPromptPreprocessorToServerPacketError as PromptPreprocessingError,
    PluginsChannelSetPromptPreprocessorToServerPacketErrorDict as PromptPreprocessingErrorDict,
    PluginsChannelSetToolsProviderToClientPacketAbortToolCall as ProvideToolsAbort,
    PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict as ProvideToolsAbortDict,
    PluginsChannelSetToolsProviderToClientPacketCallTool as ProvideToolsCallRequest,
    PluginsChannelSetToolsProviderToClientPacketCallToolDict as ProvideToolsCallRequestDict,
    PluginsChannelSetToolsProviderToClientPacketDiscardSession as ProvideToolsDiscardSession,
    PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict as ProvideToolsDiscardSessionDict,
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    PluginsChannelSetToolsProviderToClientPacketInitSessionDict as ProvideToolsInitSessionDict,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed as ProvideToolsSessionInitFailed,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict as ProvideToolsSessionInitFailedDict,
    PluginsChannelSetToolsProviderToServerPacketSessionInitialized as ProvideToolsSessionInitialized,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict as ProvideToolsSessionInitializedDict,
    PluginsChannelSetToolsProviderToServerPacketToolCallComplete as ProvideToolsCallComplete,
    PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict as ProvideToolsCallCompleteDict,
    PluginsChannelSetToolsProviderToServerPacketToolCallError as ProvideToolsCallError,
    PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict as ProvideToolsCallErrorDict,
    PluginsChannelSetToolsProviderToServerPacketToolCallStatus as ProvideToolsCallStatus,
    PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict as ProvideToolsCallStatusDict,
    PluginsChannelSetToolsProviderToServerPacketToolCallWarn as ProvideToolsCallWarn,
    PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict as ProvideToolsCallWarnDict,
)


# Warn about the plugin API stability, since it is still experimental
_PLUGIN_API_STABILITY_WARNING = """\
Note the plugin API is not yet stable and may change without notice in future releases
"""


class AsyncSessionPlugins(AsyncSession):
    """Async client session for the plugins namespace."""

    API_NAMESPACE = "plugins"


class PluginClient(AsyncClient):
    def __init__(self) -> None:
        warnings.warn(_PLUGIN_API_STABILITY_WARNING, FutureWarning)
        super().__init__()

    _ALL_SESSIONS = (
        # Possible TODO: add other sessions here if necessary
        # *ASyncSession._ALL_SESSIONS,
        AsyncSessionPlugins,
    )

    @property
    def plugins(self) -> AsyncSessionPlugins:
        """Return the plugins API client session."""
        return self._get_session(AsyncSessionPlugins)


ENV_CLIENT_ID = "LMS_PLUGIN_CLIENT_IDENTIFIER"
ENV_CLIENT_KEY = "LMS_PLUGIN_CLIENT_PASSKEY"


def get_plugin_credentials_from_env() -> tuple[str, str]:
    return os.environ[ENV_CLIENT_ID], os.environ[ENV_CLIENT_KEY]


def run_plugin(plugin_path: str | os.PathLike[str]) -> int:
    """Execute a plugin in application mode."""
    try:
        client_id, client_key = get_plugin_credentials_from_env()
    except KeyError:
        print(
            f"ERROR: {ENV_CLIENT_ID} and {ENV_CLIENT_KEY} must both be set in the environment"
        )
        return 1
    print("Plugin execution is not yet implemented")
    input("Press Enter to terminate execution...")
    return 0
