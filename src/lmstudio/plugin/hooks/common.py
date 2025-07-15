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
from ..._kv_config import dict_from_kvconfig
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    PromptPreprocessingRequest,
    StatusStepStatus,
)
from ..config_schemas import BaseConfigSchema


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
