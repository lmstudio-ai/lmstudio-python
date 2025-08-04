"""Common utilities to invoke and support plugin hook implementations."""

import asyncio

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from random import randrange
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Generic,
    TypeAlias,
    TypeVar,
)

from anyio import move_on_after

from ...async_api import _AsyncSession
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    ProvideToolsInitSession,
    PromptPreprocessingRequest,
    SerializedKVConfigSettings,
    StatusStepStatus,
)
from ..config_schemas import BaseConfigSchema

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "_AsyncSessionPlugins",
    "TPluginConfigSchema",
    "TGlobalConfigSchema",
]


class _AsyncSessionPlugins(_AsyncSession):
    """Async client session for the plugins namespace."""

    API_NAMESPACE = "plugins"


PluginRequest: TypeAlias = (
    PromptPreprocessingRequest | TokenGenerationRequest | ProvideToolsInitSession
)
TPluginRequest = TypeVar("TPluginRequest", bound=PluginRequest)
TPluginConfigSchema = TypeVar("TPluginConfigSchema", bound=BaseConfigSchema)
TGlobalConfigSchema = TypeVar("TGlobalConfigSchema", bound=BaseConfigSchema)
TConfig = TypeVar("TConfig", bound=BaseConfigSchema)


class ServerRequestError(RuntimeError):
    """Plugin received an invalid request from the API server."""


class HookController(Generic[TPluginRequest, TPluginConfigSchema, TGlobalConfigSchema]):
    """Common base class for plugin hook API access controllers."""

    def __init__(
        self,
        session: _AsyncSessionPlugins,
        request: TPluginRequest,
        plugin_config_schema: type[TPluginConfigSchema],
        global_config_schema: type[TGlobalConfigSchema],
    ) -> None:
        """Initialize common hook controller settings."""
        self.session = session
        self.request = request
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
        return f"{datetime.now(timezone.utc)}-{randrange(0, 2**32):08x}"


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

    @asynccontextmanager
    async def notify_aborted(self, message: str) -> AsyncIterator[None]:
        """Report asyncio.CancelledError as cancellation in the status block."""
        try:
            yield
        except asyncio.CancelledError:
            # Allow the notification to be sent, but don't necessarily wait for the reply
            with move_on_after(0.2, shield=True):
                await self.notify_canceled(message)
            raise
