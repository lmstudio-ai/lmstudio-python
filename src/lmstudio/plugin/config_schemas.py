"""Define plugin config schemas."""

from typing import Any

from msgspec import Struct

from ..schemas import BaseModel, DictObject
from .._kv_config import dict_from_kvconfig
from .._sdk_models import (
    SerializedKVConfigSchematics,
    SerializedKVConfigSchematicsField,
    SerializedKVConfigSettings,
)

from .sdk_api import LMStudioPluginInitError


class ConfigField(Struct, omit_defaults=True, kw_only=True, frozen=True):
    """String config field."""

    label: str
    hint: str

    @property
    def default(self) -> Any:
        """The default value for this config field."""
        raise NotImplementedError


class ConfigString(ConfigField, frozen=True):
    """String config field."""

    default: str


# TODO: Cover additional config field types


class BaseConfigSchema(BaseModel, omit_defaults=False):
    """Base class for plugin configuration schema definitions."""

    @classmethod
    def _to_kv_config_schematics(cls) -> SerializedKVConfigSchematics:
        """Convert to wire format for transmission to the app server."""
        fields: list[SerializedKVConfigSchematicsField] = []
        config_spec = cls()
        for attr in config_spec.__struct_fields__:
            field_spec = getattr(config_spec, attr, None)
            kv_field: SerializedKVConfigSchematicsField
            match field_spec:
                case ConfigString(label=label, hint=hint, default=default):
                    kv_field = SerializedKVConfigSchematicsField(
                        short_key=attr,
                        full_key=attr,
                        type_key="string",
                        type_params={
                            "displayName": label,
                            "hint": hint,
                        },
                        default_value=default,
                    )

                case ConfigField():
                    err_msg = f"{field_spec!r} is not an instance of a known {ConfigField!r} subclass"
                    raise LMStudioPluginInitError(err_msg)
                case unmatched:
                    raise LMStudioPluginInitError(
                        f"Expected {ConfigField!r} instance, not {unmatched!r}"
                    )
            fields.append(kv_field)
        return SerializedKVConfigSchematics(fields=fields)

    @classmethod
    def _default_config(cls) -> dict[str, Any]:
        default_config: dict[str, Any] = {}
        config_spec = cls()
        for attr in config_spec.__struct_fields__:
            default_config[attr] = getattr(config_spec, attr).default
        return default_config

    @classmethod
    def _parse(cls, dynamic_config: SerializedKVConfigSettings) -> DictObject:
        config = cls._default_config()
        config.update(dict_from_kvconfig(dynamic_config))
        return config
