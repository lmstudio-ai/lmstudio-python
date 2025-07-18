"""Invoking and supporting token generator hook implementations."""

from typing import Any, Awaitable, Callable
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
)

from .common import (
    HookController,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "TokenGeneratorController",
    "TokenGeneratorHook",
    # "run_token_generator",
]


class TokenGeneratorController(
    HookController[TokenGenerationRequest, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for token generator hook implementations."""


TokenGeneratorHook = Callable[[TokenGeneratorController[Any, Any]], Awaitable[None]]
