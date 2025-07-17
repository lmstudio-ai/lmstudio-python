"""Common utilities to invoke and support plugin hook implementations."""

from datetime import datetime, UTC
from pathlib import Path
from random import randrange
from typing import (
    Any,
    Callable,
    Generic,
    TypeAlias,
    TypeVar,
)

from ...async_api import AsyncSession
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    PromptPreprocessingRequest,
    SerializedKVConfigSettings,
    StatusStepStatus,
)
from ..config_schemas import BaseConfigSchema

__all__ = [
    "AsyncSessionPlugins",
    "TPluginConfigSchema",
    "TGlobalConfigSchema",
]


class AsyncSessionPlugins(AsyncSession):
    """Async client session for the plugins namespace."""

    API_NAMESPACE = "plugins"


PluginRequest: TypeAlias = (
    PromptPreprocessingRequest | TokenGenerationRequest | ProvideToolsInitSession
)
TPluginRequest = TypeVar("TPluginRequest", bound=PluginRequest)
TPluginConfigSchema = TypeVar("TPluginConfigSchema", bound=BaseConfigSchema)
TGlobalConfigSchema = TypeVar("TGlobalConfigSchema", bound=BaseConfigSchema)
TConfig = TypeVar("TConfig", bound=BaseConfigSchema)


class HookController(Generic[TPluginRequest, TPluginConfigSchema, TGlobalConfigSchema]):
    """Common base class for plugin hook API access controllers."""

    def __init__(
        self,
        session: AsyncSessionPlugins,
        request: TPluginRequest,
        plugin_config_schema: type[TPluginConfigSchema],
        global_config_schema: type[TGlobalConfigSchema],
    ) -> None:
        """Initialize common hook controller settings."""
        self.session = session
        self.plugin_config = self._parse_config(
            request.plugin_config, plugin_config_schema
        )
        self.global_config = self._parse_config(
            request.global_plugin_config, global_config_schema
        )
        work_dir = request.working_directory_path
        self.working_path = Path(work_dir) if work_dir else None

    @classmethod
    def _parse_config(
        cls, config: SerializedKVConfigSettings, schema: type[TConfig]
    ) -> TConfig:
        if schema is None:
            schema = BaseConfigSchema
        return schema._parse(config)

    @classmethod
    def _create_ui_block_id(self) -> str:
        return f"{datetime.now(UTC)}-{randrange(0, 2**32):08x}"


StatusUpdateCallback: TypeAlias = Callable[[str, StatusStepStatus, str], Any]


class StatusBlockController:
    """API access to update a UI status block in-place."""

    def __init__(
        self,
        block_id: str,
        update_ui: StatusUpdateCallback,
    ) -> None:
        """Initialize status block controller."""
        self._id = block_id
        self._update_ui = update_ui

    async def notify_waiting(self, message: str) -> None:
        """Report task is waiting (static icon) in the status block."""
        await self._update_ui(self._id, "waiting", message)

    async def notify_working(self, message: str) -> None:
        """Report task is working (dynamic icon) in the status block."""
        await self._update_ui(self._id, "loading", message)

    async def notify_error(self, message: str) -> None:
        """Report task error in the status block."""
        await self._update_ui(self._id, "error", message)

    async def notify_canceled(self, message: str) -> None:
        """Report task cancellation in the status block."""
        await self._update_ui(self._id, "canceled", message)

    async def notify_done(self, message: str) -> None:
        """Report task completion in the status block."""
        await self._update_ui(self._id, "done", message)
