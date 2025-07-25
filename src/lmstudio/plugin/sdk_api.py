"""Common definitions for defining the plugin SDK interfaces."""

from typing import TypeVar

from ..sdk_api import LMStudioRuntimeError, LMStudioValueError

_PLUGIN_SDK_SUBMODULE = ".".join(__name__.split(".")[:-1])

_C = TypeVar("_C", bound=type)

# Available as lmstudio.plugin.*
__all__ = [
    "LMStudioPluginInitError",
    "LMStudioPluginRuntimeError",
]


def plugin_sdk_type(cls: _C) -> _C:
    """Indicates a class forms part of the public plugin SDK boundary.

    Sets `__module__` to the plugin SDK submodule import rather than
    leaving it set to the implementation module.

    Note: methods are *not* implicitly decorated as public SDK APIs
    """
    cls.__module__ = _PLUGIN_SDK_SUBMODULE
    return cls


@plugin_sdk_type
class LMStudioPluginRuntimeError(LMStudioRuntimeError):
    """Plugin runtime behaviour was not as expected."""


@plugin_sdk_type
class LMStudioPluginInitError(LMStudioValueError):
    """Plugin initialization value was not as expected."""
