"""Invoking and supporting token generator hook implementations."""

from typing import Any, Awaitable, Callable
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
)

from ..config_schemas import BaseConfigSchema
from .common import (
    _AsyncSessionPlugins,
    HookController,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "TokenGeneratorController",
    "TokenGeneratorHook",
    "run_token_generator",
]


class TokenGeneratorController(
    HookController[TokenGenerationRequest, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for token generator hook implementations."""


TokenGeneratorHook = Callable[[TokenGeneratorController[Any, Any]], Awaitable[None]]


async def run_token_generator(
    plugin_name: str,
    hook_impl: TokenGeneratorHook,
    plugin_config_schema: type[BaseConfigSchema],
    global_config_schema: type[BaseConfigSchema],
    session: _AsyncSessionPlugins,
    notify_ready: Callable[[], Any],
) -> None:
    """Accept token generation requests."""
    raise NotImplementedError
