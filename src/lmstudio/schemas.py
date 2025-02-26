"""Structured JSON values for LM Studio APIs."""

import json

from typing import (
    Any,
    ClassVar,
    Generic,
    Mapping,
    Protocol,
    Self,
    Sequence,
    TypeVar,
    cast,
    runtime_checkable,
)

from msgspec import Struct, convert, to_builtins
from msgspec.json import schema

from .sdk_api import LMStudioValueError, sdk_public_api, sdk_public_type

__all__ = [
    "BaseModel",
    "ModelSchema",
    "DictObject",
    "DictSchema",
]

DictObject = Mapping[str, Any]  # Any JSON-compatible string-keyed dict
DictSchema = Mapping[str, Any]  # JSON schema as a string-keyed dict


def _format_json(data: Any, *, sort_keys: bool = True) -> str:
    return json.dumps(data, indent=2, sort_keys=sort_keys)


def _to_json_schema(cls: type, *, omit: Sequence[str] = ()) -> DictSchema:
    json_schema = schema(cls)
    schema_ref: str | None = json_schema.get("$ref", None)
    if schema_ref is not None:
        # The LM Studio API doesn't like schema definitions with
        # top level "$ref" keys referring to a named subschema,
        # so extract the target schema and use its field values
        # (this isn't fully general, but it works for `msgspec`)
        del json_schema["$ref"]
        _, schema_defs_key, schema_name = schema_ref.split("/")
        subschemas: dict[str, dict[str, Any]] = json_schema[schema_defs_key]
        named_schema = subschemas.pop(schema_name, None)
        if named_schema is None:
            raise LMStudioValueError(
                f"Could not resolve {schema_ref!r} in {json_schema!r}"
            )
        for field in omit:
            named_schema.pop(field, None)
        json_schema.update(named_schema)
    return json_schema


@sdk_public_type
@runtime_checkable
class ModelSchema(Protocol):
    """Protocol for classes that provide a JSON schema for their model."""

    @classmethod
    def model_json_schema(cls) -> DictSchema:
        """Return a JSON schema dict describing this model."""
        ...


@sdk_public_type
class BaseModel(Struct, omit_defaults=True, kw_only=True):
    """Base class for structured prediction output formatting."""

    # Allows structured predictions using a `pydantic.BaseModel` inspired format,
    # even in applications that don't otherwise depend on Pydantic

    @classmethod
    def model_json_schema(cls) -> DictSchema:
        """Returns JSON Schema dict describing the format of this class."""
        # Schema descriptions are always converted to dict[str, Any], but
        # Python type checkers don't know that. Use `cast` to notify them.
        return cast(
            dict[str, Any], to_builtins(_to_json_schema(cls), order="deterministic")
        )


_CAMEL_CASE_OVERRIDES = {
    # This is the one key in the API that capitalizes the `V` in `KV`
    "useFp16ForKvCache": "useFp16ForKVCache",
}


def _snake_case_to_camelCase(key: str) -> str:
    first, *rest = key.split("_")
    camelCase = "".join((first, *(w.capitalize() for w in rest)))
    return _CAMEL_CASE_OVERRIDES.get(camelCase, camelCase)


def _snake_case_keys_to_camelCase(data: DictObject) -> DictObject:
    translated_data: dict[str, Any] = {}
    dicts_to_process = [(data, translated_data)]
    queued_dict_ids = set((id(data),))

    def _queue_dict(input_dict: DictObject, output_dict: dict[str, Any]) -> None:
        dict_id = id(input_dict)
        if dict_id in queued_dict_ids:
            raise LMStudioValueError("Data structure cycles are not supported.")
        queued_dict_ids.add(dict_id)
        dicts_to_process.append((input_dict, output_dict))

    for input_dict, output_dict in dicts_to_process:
        for k, v in input_dict.items():
            new_value: Any
            match v:
                case {}:
                    new_dict: dict[str, Any] = {}
                    _queue_dict(v, new_dict)
                    new_value = new_dict
                case [*_]:
                    new_list: list[Any] = []
                    for item in v:
                        new_item: Any
                        match item:
                            case {}:
                                new_dict_item: dict[str, Any] = {}
                                _queue_dict(item, new_dict_item)
                                new_item = new_dict_item
                            case [*_]:
                                raise LMStudioValueError(
                                    "Lists of lists are not supported."
                                )
                            case _:
                                new_item = item
                        new_list.append(new_item)
                    new_value = new_list
                case _:
                    new_value = v
            if "_" in k:
                new_k = _snake_case_to_camelCase(k)
            else:
                new_k = k
            output_dict[new_k] = new_value
    return translated_data


# Typed dict values conform to `object`, rather than to `Any`
# https://github.com/python/mypy/issues/8994
TWireFormat = TypeVar("TWireFormat", bound=Mapping[str, object])


class LMStudioStruct(Generic[TWireFormat], Struct, omit_defaults=True, kw_only=True):
    """Base class for LM Studio-specific structured JSON values."""

    # Inherited metaclass keyword arguments:
    #
    # * "None" fields should be omitted, not sent as "null"
    # * Allow non-default fields after default fields
    #

    # This is actually defined in msgspec.Struct,
    # but is missing from the published type stubs:
    # https://github.com/jcrist/msgspec/pull/813
    __struct_encode_fields__: ClassVar[tuple[str, ...]]

    @classmethod
    def _from_any_api_dict(cls, data: DictObject) -> Self:
        """Attempt to create an instance from a camelCase string-keyed dict."""
        return convert(data, cls)

    @classmethod
    def _from_api_dict(cls, data: TWireFormat) -> Self:
        """Attempt to create an instance from a camelCase string-keyed dict."""
        # SDK code should use `_from_any_api_dict` directly rather than external casts
        return cls._from_any_api_dict(data)

    @classmethod
    def _from_any_dict(cls, data: DictObject) -> Self:
        """Attempt to create an instance from a camelCase or snake_case string-keyed dict."""
        # `convert` won't report validation errors for optional fields, so we always check
        # for snake_case keys. SDK code should use `_from_api_dict` instead when the keys
        # are known to already be using camelCase multi-word formatting.
        return convert(_snake_case_keys_to_camelCase(data), cls)

    @classmethod
    @sdk_public_api()
    def from_dict(cls, data: TWireFormat) -> Self:
        """Attempt to create an instance from a camelCase or snake_case string-keyed dict."""
        # Statically type checked API for creating instances from mappings
        # SDK code should use `_from_any_dict` directly rather than external casts
        return cls._from_any_dict(data)

    def to_dict(self) -> TWireFormat:
        """Convert instance to a camelCase string-keyed dictionary."""
        # Struct instances are always converted to their corresponding dict,
        # but Python type checkers don't know that. Use `cast` to notify them.
        return cast(TWireFormat, to_builtins(self, order="deterministic"))

    def __str__(self) -> str:
        type_name = type(self).__name__
        formatted_data = _format_json(self.to_dict())
        return f"{type_name}.from_dict({formatted_data})"


AnyLMStudioStruct = LMStudioStruct[Any]
