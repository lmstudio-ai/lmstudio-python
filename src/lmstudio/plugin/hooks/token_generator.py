"""Invoking and supporting token generator hook implementations."""

from typing import Awaitable, Callable
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetGeneratorToClientPacketGenerate as TokenGenerationRequest,
)

from .common import HookController

__all__ = [
    "TokenGeneratorController",
    "TokenGeneratorHook",
]


class TokenGeneratorController(HookController[TokenGenerationRequest]):
    """API access for token generator hook implementations."""


TokenGeneratorHook = Callable[[TokenGeneratorController], Awaitable[None]]
