"""Define plugin config schemas."""

from dataclasses import Field, dataclass, fields
from typing import (
    Any,
    ClassVar,
    Generic,
    Sequence,
    TypeVar,
    cast,
)

from typing_extensions import (
    # Native in 3.11+
    Self,
    dataclass_transform,
)

from .._kv_config import dict_from_kvconfig
from .._sdk_models import (
    SerializedKVConfigSchematics,
    SerializedKVConfigSchematicsField,
    SerializedKVConfigSettings,
)
from ..sdk_api import sdk_public_api
from .sdk_api import LMStudioPluginInitError, plugin_sdk_type

# Available as lmstudio.plugin.*
__all__ = [
    "BaseConfigSchema",
    "config_field",
]

_T = TypeVar("_T")

_CONFIG_FIELDS_KEY = "__kv_config_fields__"


@dataclass(frozen=True, slots=True)
class _ConfigField(Generic[_T]):
    """Plugin config field specification."""

    label: str
    hint: str

    @property
    def default(self) -> _T:
        """The default value for this config field."""
        # Defaults must be static values, as the UI isn't directly running any plugin code
        raise NotImplementedError

    # This never actually gets called (as __set_name__ switches to the default value at runtime)
    # However, it's here so type checkers accept field definitions as matching their value type
    def __get__(
        self, _obj: "BaseConfigSchema | None", _obj_type: type["BaseConfigSchema"]
    ) -> _T:
        return self.default

    def __set_name__(self, obj_type: type["BaseConfigSchema"], name: str) -> None:
        if not issubclass(obj_type, BaseConfigSchema):
            msg = f"Plugin config fields must be defined on {BaseConfigSchema.__name__} instances"
            raise LMStudioPluginInitError(msg)
        # Append this field to the config fields for this schema, creating the list if necessary
        config_fields: list[SerializedKVConfigSchematicsField]
        config_fields = obj_type.__dict__.get(_CONFIG_FIELDS_KEY, None)
        if config_fields is None:
            # First config field defined for this schema, so create the config field list
            config_fields = []
            try:
                inherited_fields = getattr(obj_type, _CONFIG_FIELDS_KEY)
            except AttributeError:
                pass
            else:
                # Any inherited fields are included first
                config_fields.extend(inherited_fields)
            setattr(obj_type, _CONFIG_FIELDS_KEY, config_fields)
        config_fields.append(self._to_kv_field(name))
        # Replace the UI config field spec with a regular dataclass default value
        setattr(obj_type, name, self.default)

    def _to_kv_field(self, name: str) -> SerializedKVConfigSchematicsField:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class _ConfigBool(_ConfigField[bool]):
    """Boolean config field."""

    default: bool

    def _to_kv_field(self, name: str) -> SerializedKVConfigSchematicsField:
        return SerializedKVConfigSchematicsField(
            short_key=name,
            full_key=name,
            type_key="boolean",
            type_params={
                "displayName": self.label,
                "hint": self.hint,
            },
            default_value=self.default,
        )


@dataclass(frozen=True, slots=True)
class _ConfigInt(_ConfigField[int]):
    """Integer config field."""

    default: int

    def _to_kv_field(self, name: str) -> SerializedKVConfigSchematicsField:
        return SerializedKVConfigSchematicsField(
            short_key=name,
            full_key=name,
            type_key="numeric",
            type_params={
                "displayName": self.label,
                "hint": self.hint,
                "int": True,
            },
            default_value=self.default,
        )


@dataclass(frozen=True, slots=True)
class _ConfigFloat(_ConfigField[float]):
    """Floating point config field."""

    default: float

    def _to_kv_field(self, name: str) -> SerializedKVConfigSchematicsField:
        return SerializedKVConfigSchematicsField(
            short_key=name,
            full_key=name,
            type_key="numeric",
            type_params={
                "displayName": self.label,
                "hint": self.hint,
                "int": False,
            },
            default_value=self.default,
        )


@dataclass(frozen=True, slots=True)
class _ConfigString(_ConfigField[str]):
    """String config field."""

    default: str

    def _to_kv_field(self, name: str) -> SerializedKVConfigSchematicsField:
        return SerializedKVConfigSchematicsField(
            short_key=name,
            full_key=name,
            type_key="string",
            type_params={
                "displayName": self.label,
                "hint": self.hint,
            },
            default_value=self.default,
        )


@sdk_public_api()
def config_field(*, label: str, hint: str, default: _T) -> _T:
    """Define a plugin config field to be displayed and updated via the app UI."""
    # This type hint intentionally doesn't match the actual returned type
    # (the relevant ConfigField[_T] subclass). This is to ensure that
    # type checkers will accept config field initialisations like
    # "attr: int = config_field(...)".
    descriptor: _ConfigField[Any]
    match default:
        case bool():
            descriptor = _ConfigBool(label, hint, default)
        case float():
            descriptor = _ConfigFloat(label, hint, default)
        case int():
            descriptor = _ConfigInt(label, hint, default)
        case str():
            descriptor = _ConfigString(label, hint, default)
        case _:
            msg = f"Unsupported type for plugin config field: {type(default)!r}"
            raise LMStudioPluginInitError(msg)
    return cast(_T, descriptor)


# TODO: Cover additional config field types
# TODO: Allow optional constraints and UI display features
#       (the similarity of the _to_kv_field methods will reduce when this is done)


class _ImplicitDataClass(type):
    def __new__(
        meta_cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> type:
        cls: type = super().__new__(meta_cls, name, bases, namespace)
        return dataclass()(cls)


@dataclass_transform(field_specifiers=(config_field,))
@plugin_sdk_type
class BaseConfigSchema(metaclass=_ImplicitDataClass):
    """Base class for plugin configuration schema definitions."""

    # This uses the custom metaclass to automatically make subclasses data classes
    # Declare that behaviour in a way that mypy will fully accept
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    # ConfigField.__set_name__ lazily creates this class variable
    __kv_config_fields__: ClassVar[Sequence[SerializedKVConfigSchematicsField]]

    @classmethod
    def _to_kv_config_schematics(cls) -> SerializedKVConfigSchematics | None:
        """Convert to wire format for transmission to the app server."""
        try:
            config_fields = cls.__kv_config_fields__
        except AttributeError:
            # No config fields have been defined on this config schema
            # This is fine (as it allows for placeholders in code skeletons)
            return None
        return SerializedKVConfigSchematics(fields=config_fields)

    @classmethod
    def _default_config(cls) -> dict[str, Any]:
        default_config: dict[str, Any] = {}
        config_spec = cls()
        for field in fields(config_spec):
            attr = field.name
            default_config[attr] = getattr(config_spec, attr)
        return default_config

    @classmethod
    def _parse(cls, dynamic_config: SerializedKVConfigSettings) -> Self:
        config = cls._default_config()
        config.update(dict_from_kvconfig(dynamic_config))
        return cls(**config)
