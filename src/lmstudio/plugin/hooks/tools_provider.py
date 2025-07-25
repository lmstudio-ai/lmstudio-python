"""Invoking and supporting tools provider hook implementations."""

from typing import Any, Awaitable, Callable, Iterable

from ...json_api import (
    ToolDefinition,
)

from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
)

from ..config_schemas import BaseConfigSchema
from .common import (
    AsyncSessionPlugins,
    HookController,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "ToolsProviderController",
    "ToolsProviderHook",
    "run_tools_provider",
]


class ToolsProviderController(
    HookController[ProvideToolsInitSession, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for tools provider hook implementations."""


ToolsProviderHook = Callable[
    [ToolsProviderController[Any, Any]], Awaitable[Iterable[ToolDefinition]]
]


async def run_tools_provider(
    plugin_name: str,
    hook_impl: ToolsProviderHook,
    plugin_config_schema: type[BaseConfigSchema],
    global_config_schema: type[BaseConfigSchema],
    session: AsyncSessionPlugins,
    notify_ready: Callable[[], Any],
) -> None:
    """Accept tools provider session requests."""
    raise NotImplementedError
