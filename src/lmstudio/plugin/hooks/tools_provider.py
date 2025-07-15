"""Invoking and supporting tools provider hook implementations."""

from typing import Awaitable, Callable, Iterable

from ...json_api import (
    ToolDefinition,
)

from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
)

from .common import HookController

__all__ = [
    "ToolsProviderController",
    "ToolsProviderHook",
]


class ToolsProviderController(HookController[ProvideToolsInitSession]):
    """API access for tools provider hook implementations."""


ToolsProviderHook = Callable[
    [ToolsProviderController], Awaitable[Iterable[ToolDefinition]]
]
