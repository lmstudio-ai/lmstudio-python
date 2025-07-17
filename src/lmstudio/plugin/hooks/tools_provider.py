"""Invoking and supporting tools provider hook implementations."""

from typing import Any, Awaitable, Callable, Iterable

from ...json_api import (
    ToolDefinition,
)

from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
)

from .common import (
    HookController,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

__all__ = [
    "ToolsProviderController",
    "ToolsProviderHook",
]


class ToolsProviderController(
    HookController[ProvideToolsInitSession, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for tools provider hook implementations."""


ToolsProviderHook = Callable[
    [ToolsProviderController[Any, Any]], Awaitable[Iterable[ToolDefinition]]
]
