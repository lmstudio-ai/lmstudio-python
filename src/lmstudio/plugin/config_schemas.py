"""Define plugin config schemas."""

from msgspec import Struct

from ..schemas import BaseModel


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
