"""Test schema processing support."""

from typing import Any, Type

import pytest

from lmstudio import AnyModelSpecifier, ModelQuery, ModelQueryDict
from lmstudio.schemas import _snake_case_keys_to_camelCase, LMStudioStruct
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
)

from .support import EXPECTED_LLM_ID


def test_lists_of_lists_rejected() -> None:
    with pytest.raises(ValueError, match="Lists of lists"):
        _snake_case_keys_to_camelCase({"key": [[]]})


def test_data_cycles_rejected() -> None:
    data: dict[str, Any] = {"key": None}
    data["key"] = data
    with pytest.raises(ValueError, match="Data structure cycles"):
        _snake_case_keys_to_camelCase(data)


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
