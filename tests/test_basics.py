"""Basic tests for lmstudio Python SDK components."""

import builtins
import sys

from importlib.metadata import version as pkg_version
from typing import Any, FrozenSet, Iterator, Set, Type

import pytest

from msgspec import Struct

import lmstudio
import lmstudio.json_api


def test_python_api_version() -> None:
    # Ensure dist package version and import API version are consistent
    assert pkg_version("lmstudio") == lmstudio.__version__


_ALLOWED_NUMBER_SCHEMA_SUFFIXES = (
    # Commonly used schema suffixes that end with a number
    "Base64",
)
_KNOWN_NUMBERED_SCHEMAS = frozenset(
    (
        # Names that legitimately end with numbers
        "RetrievalChunkingMethodRecursiveV1",
    )
)


def _find_unknown_numbered_schemas(schema_names: Set[str]) -> FrozenSet[str]:
    unknown_schemas = schema_names - _KNOWN_NUMBERED_SCHEMAS
    return frozenset(
        sch
        for sch in unknown_schemas
        if not sch.endswith(_ALLOWED_NUMBER_SCHEMA_SUFFIXES)
    )


def test_no_automatic_schema_numbering() -> None:
    # Ensure the schema conversion only produces named types
    numbered_schemas: set[str] = set()
    for name, obj in lmstudio._sdk_models.__dict__.items():
        if isinstance(obj, type) and issubclass(obj, Struct) and name[-1].isdigit():
            numbered_schemas.add(name)
    unknown_numbered_schemas = _find_unknown_numbered_schemas(numbered_schemas)
    if unknown_numbered_schemas:
        print(unknown_numbered_schemas)
    assert not unknown_numbered_schemas
    # Ensure the known schema list is kept updated
    missing_known_schemas = _KNOWN_NUMBERED_SCHEMAS - numbered_schemas
    if missing_known_schemas:
        print(missing_known_schemas)
    assert not missing_known_schemas


def _get_public_exceptions() -> Iterator[Type[BaseException]]:
    for v in lmstudio.json_api.__dict__.values():
        if isinstance(v, type) and issubclass(v, BaseException):
            yield v


@pytest.mark.parametrize("exc_type", _get_public_exceptions())
def test_public_exceptions(exc_type: Type[BaseException]) -> None:
    # Ensure defined exceptions are published, prefixed,
    # inherit from the expected base class,
    # and report the top level module name
    assert issubclass(exc_type, lmstudio.LMStudioError)
    assert getattr(lmstudio, exc_type.__name__) is exc_type
    exc_name = exc_type.__name__
    name_suffix = exc_name.removeprefix("LMStudio")
    assert name_suffix != exc_name
    assert exc_type.__module__ == "lmstudio"
    builtin_exc = getattr(builtins, name_suffix, None)
    if builtin_exc is not None:
        assert issubclass(exc_type, builtin_exc)


def _get_public_callables() -> Iterator[Any]:
    for k, v in lmstudio.__dict__.items():
        if (
            not isinstance(v, type)  # Ignore class definitions
            and not hasattr(v, "__origin__")  # Ignore type aliases
            and callable(v)
            and hasattr((m := sys.modules[v.__module__]), "__all__")
            and k in m.__all__
        ):
            yield v


@pytest.mark.parametrize("api_call", _get_public_callables())
def test_public_callables(api_call: Any) -> None:
    # Ensure published callables are wrapped with
    # the public_sdk_api decorator
    assert hasattr(api_call, "__wrapped__")
