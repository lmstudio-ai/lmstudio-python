"""Test schema processing support."""

# Work around https://github.com/jcrist/msgspec/issues/847
from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType
from typing import Any, Iterator, Mapping, Type

import pytest

from lmstudio import AnyModelSpecifier, ModelQuery, ModelQueryDict
from lmstudio.schemas import _snake_case_keys_to_camelCase, LMStudioStruct
from lmstudio.sdk_api import LMStudioValueError
from lmstudio.json_api import (
    _model_spec_to_api_dict,
    ModelSessionTypes,
    ModelTypesEmbedding,
    ModelTypesLlm,
)
from lmstudio._sdk_models import (
    ModelSpecifierInstanceReference,
    ModelSpecifierInstanceReferenceDict,
    ModelSpecifierQuery,
    ModelSpecifierQueryDict,
    PluginsChannelStartToolUseSessionToServerPacketCallTool as LegacyToolCall,
    PluginsChannelStartToolUseSessionToServerPacketCallToolDict as LegacyToolCallDict,
    ToolCallRequest,
    ToolCallRequestDict,
)
from msgspec import ValidationError

from .support import EXPECTED_LLM_ID


def test_lists_of_lists_rejected() -> None:
    with pytest.raises(ValueError, match="Lists of lists"):
        _snake_case_keys_to_camelCase({"key": [[]]})


def test_data_cycles_rejected() -> None:
    data: dict[str, Any] = {"key": None}
    data["key"] = data
    with pytest.raises(ValueError, match="Data structure cycles"):
        _snake_case_keys_to_camelCase(data)


@pytest.mark.parametrize(
    "arguments",
    [
        None,
        False,
        42,
        3.5,
        "literal_value",
        {"order_id": "snake", "orderId": "camel"},
        [{"postal_code": "12345"}, [[{"line_item_id": 1}]]],
    ],
)
def test_legacy_tool_arguments_preserved(arguments: Any) -> None:
    data: LegacyToolCallDict = {
        "type": "callTool",
        "callId": 1,
        "name": "example_tool",
        "arguments": arguments,
    }
    parsed = LegacyToolCall.from_dict(data)
    assert parsed.to_dict() == data


@pytest.mark.parametrize("arguments", [{"order_id": []}, [{"order_id": []}]])
def test_legacy_tool_arguments_copy_independence(arguments: Any) -> None:
    data: LegacyToolCallDict = {
        "type": "callTool",
        "callId": 1,
        "name": "example_tool",
        "arguments": arguments,
    }
    original = deepcopy(data)
    parsed = LegacyToolCall.from_dict(data)
    source_object = arguments if isinstance(arguments, dict) else arguments[0]
    result_object = (
        parsed.arguments if isinstance(parsed.arguments, dict) else parsed.arguments[0]
    )
    source_object["order_id"].append("source")
    assert parsed.to_dict() == original
    result_object["order_id"].append("result")
    assert source_object["order_id"] == ["source"]


def test_tool_request_arguments_still_require_mapping() -> None:
    data: Any = {"type": "function", "name": "example_tool", "arguments": []}
    with pytest.raises(ValidationError, match="object"):
        ToolCallRequest.from_dict(data)


class ReadOnlyArguments(Mapping[str, Any]):
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


@pytest.mark.parametrize(
    "arguments, expected",
    [
        (MappingProxyType({"order_id": 1}), {"order_id": 1}),
        (
            {"nested_value": MappingProxyType({"order_id": 1})},
            {"nested_value": {"order_id": 1}},
        ),
        (ReadOnlyArguments({"order_id": 1}), {"order_id": 1}),
        (
            {"nested_value": ReadOnlyArguments({"order_id": 1})},
            {"nested_value": {"order_id": 1}},
        ),
    ],
)
def test_tool_arguments_materialize_mappings(
    arguments: Mapping[str, Any], expected: dict[str, Any]
) -> None:
    parsed = ToolCallRequest.from_dict(
        {"type": "function", "name": "example_tool", "arguments": arguments}
    )
    assert parsed.arguments == expected
    assert isinstance(parsed.arguments, dict)
    if "nested_value" in parsed.arguments:
        assert isinstance(parsed.arguments["nested_value"], dict)


@pytest.mark.parametrize(
    "cycle_kind", ["mapping", "proxy", "list", "tuple", "envelope"]
)
def test_tool_arguments_cycles_rejected(cycle_kind: str) -> None:
    arguments: dict[str, Any] = {}
    data: ToolCallRequestDict = {
        "type": "function",
        "name": "example_tool",
        "arguments": arguments,
    }
    if cycle_kind == "mapping":
        arguments["cycle"] = arguments
    elif cycle_kind == "proxy":
        arguments["cycle"] = MappingProxyType(arguments)
    elif cycle_kind == "list":
        items: list[Any] = []
        items.append(items)
        arguments["cycle"] = items
    elif cycle_kind == "tuple":
        nested_items: list[Any] = []
        pair = (nested_items,)
        nested_items.append(pair)
        arguments["cycle"] = pair
    else:
        arguments["cycle"] = data
    with pytest.raises(
        LMStudioValueError, match=r"^Data structure cycles are not supported\.$"
    ):
        ToolCallRequest.from_dict(data)


def test_tool_arguments_copy_nested_sequences_and_shared_values() -> None:
    items = [1]
    original: dict[str, Any] = {
        "order_id": "snake",
        "orderId": "camel",
        "items": ([items, items],),
    }
    parsed = ToolCallRequest.from_dict(
        {"type": "function", "name": "example_tool", "arguments": original}
    )
    assert parsed.arguments == {
        "order_id": "snake",
        "orderId": "camel",
        "items": [[[1], [1]]],
    }
    assert parsed.arguments is not None
    items.append(2)
    assert parsed.arguments["items"] == [[[1], [1]]]
    parsed.arguments["items"][0][0].append(3)
    assert items == [1, 2]
    assert parsed.arguments["items"][0][1] == [1]


class Example(LMStudioStruct[dict[str, str | int]]):
    key1: str
    key2: int


EXPECTED_REPR = "Example(key1='value', key2=42)"
EXPECTED_STR = """\
Example.from_dict({
  "key1": "value",
  "key2": 42
})\
"""


def test_struct_display() -> None:
    struct = Example(key1="value", key2=42)
    assert repr(struct) == EXPECTED_REPR
    assert str(struct) == EXPECTED_STR


EXPECTED_MODEL_QUERY: ModelQueryDict = {"identifier": EXPECTED_LLM_ID}

EXPECTED_MODEL_QUERY_SPECIFIER: ModelSpecifierQueryDict = {
    "type": "query",
    "query": EXPECTED_MODEL_QUERY,
}

MODEL_QUERY_SPECIFIERS: list[AnyModelSpecifier] = [
    EXPECTED_LLM_ID,
    EXPECTED_MODEL_QUERY,
    EXPECTED_MODEL_QUERY_SPECIFIER,
    ModelQuery(identifier=EXPECTED_LLM_ID),
    ModelSpecifierQuery(query=ModelQuery(identifier=EXPECTED_LLM_ID)),
]


@pytest.mark.parametrize("model_spec", MODEL_QUERY_SPECIFIERS)
def test_model_query_specifiers(model_spec: AnyModelSpecifier) -> None:
    parsed_specifier = _model_spec_to_api_dict(model_spec)
    assert parsed_specifier == EXPECTED_MODEL_QUERY_SPECIFIER


EXPECTED_INSTANCE_REF = "ref-placeholder-for-testing"

EXPECTED_INSTANCE_SPECIFIER: ModelSpecifierInstanceReferenceDict = {
    "type": "instanceReference",
    "instanceReference": EXPECTED_INSTANCE_REF,
}

MODEL_INSTANCE_SPECIFIERS: list[AnyModelSpecifier] = [
    EXPECTED_INSTANCE_SPECIFIER,
    ModelSpecifierInstanceReference(instance_reference=EXPECTED_INSTANCE_REF),
]


@pytest.mark.parametrize("model_spec", MODEL_INSTANCE_SPECIFIERS)
def test_model_instance_references(model_spec: AnyModelSpecifier) -> None:
    parsed_specifier = _model_spec_to_api_dict(model_spec)
    assert parsed_specifier == EXPECTED_INSTANCE_SPECIFIER


@pytest.mark.parametrize("api_types", (ModelTypesEmbedding, ModelTypesLlm))
def test_model_session_types(api_types: Type[ModelSessionTypes[Any]]) -> None:
    expected_type_prefix = api_types.__name__.removeprefix("ModelTypes")
    # Check expected types are defined for each model session variant
    expected_attrs = set(ModelSessionTypes.__annotations__)
    assert expected_attrs
    for attr in expected_attrs:
        api_type = getattr(api_types, attr)
        assert isinstance(api_type, type)
        assert api_type.__name__.startswith(expected_type_prefix)
