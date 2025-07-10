"""Support for implementing LM Studio plugins in Python."""

from msgspec import Struct

from ..schemas import BaseModel

# Using wildcard imports to export API symbols is acceptable
# ruff: noqa: F403

from ._api_client import *

# TODO: Define `sdk_plugin_type` to fix up reported class modules,
#       as well as `sdk_plugin_api*` decorators

# TODO: Move the config types to a submodule


class BaseConfig(BaseModel, omit_defaults=False):
    """Base class for plugin configuration schema definitions."""

    pass


class ConfigField(Struct, omit_defaults=True, kw_only=True, frozen=True):
    """String config field."""

    label: str
    hint: str


class ConfigString(ConfigField, frozen=True):
    """String config field."""

    default: str


# TODO: Cover additional config field types
