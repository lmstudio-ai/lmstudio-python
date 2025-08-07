"""Test making simple predictions with the API."""

import asyncio
import logging

from typing import Any

import pytest
from pytest import LogCaptureFixture as LogCap
from pytest_subtests import SubTests

from lmstudio import (
    AsyncClient,
    Chat,
    LlmPredictionConfig,
    LMStudioValueError,
    PredictionResult,
    ToolFunctionDef,
)
from lmstudio.json_api import ChatResponseEndpoint
from lmstudio._sdk_models import LlmToolParameters

from .support import (
    ADDITION_TOOL_SPEC,
    EXPECTED_LLM_ID,
    MAX_PREDICTED_TOKENS,
    SHORT_PREDICTION_CONFIG,
    log_adding_two_integers,
)

SC_PREDICTION_CONFIG = {
    "max_tokens": MAX_PREDICTED_TOKENS,
    "temperature": 0,
}


def test_prediction_config_translation() -> None:
    # Ensure prediction config with snake_case keys is translated
    assert SC_PREDICTION_CONFIG != SHORT_PREDICTION_CONFIG
    # We expect this to fail static type checking
    struct_config = LlmPredictionConfig.from_dict(SC_PREDICTION_CONFIG)  # type: ignore[arg-type]
    expected_struct_config = LlmPredictionConfig(
        max_tokens=MAX_PREDICTED_TOKENS, temperature=0
    )
    assert struct_config == expected_struct_config
    assert struct_config.to_dict() == SHORT_PREDICTION_CONFIG


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_concurrent_predictions(caplog: LogCap, subtests: SubTests) -> None:
    phrase = "I am a robot"
    refusal = "I cannot repeat"
    request = f"Repeat the phrase '{phrase}' ten times."
    history = Chat(
        "You are a very obedient automatic assistant that always behaves as requested. "
        "You give terse responses."
    )
    history.add_user_message(request)

    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        session = client.llm

        async def _request_response() -> PredictionResult:
            llm = await session.model(model_id)
            return await llm.respond(
                history=history,
                config=SHORT_PREDICTION_CONFIG,
            )

        # Note: too many parallel requests risks overloading the local API server
        requests = [_request_response() for i in range(5)]
        responses = await asyncio.gather(*requests)
    subtests_passed = 0
    for i, response in enumerate(responses):
        with subtests.test("Check prediction response", i=i):
            # The responses are variable enough that not much can be checked here
            assert phrase in response.content or refusal in response.content
            subtests_passed += 1

    # Work around pytest-subtests not showing full output when subtests fail
    # https://github.com/pytest-dev/pytest-subtests/issues/76
    assert subtests_passed == len(responses), "Fail due to failed subtest(s)"


# TODO: write sync concurrent predictions test with external locking and concurrent.futures


def test_tool_def_from_callable() -> None:
    default_def = ToolFunctionDef.from_callable(log_adding_two_integers)
    assert default_def == ToolFunctionDef(
        name=log_adding_two_integers.__name__,
        description="Log adding two integers together.",
        parameters=ADDITION_TOOL_SPEC["parameters"],
        implementation=log_adding_two_integers,
    )
    custom_def = ToolFunctionDef.from_callable(
        log_adding_two_integers, name="add", description="Add two numbers"
    )
    assert custom_def == ToolFunctionDef(**ADDITION_TOOL_SPEC)


def test_parse_tools() -> None:
    addition_def = ToolFunctionDef.from_callable(
        log_adding_two_integers, name="add_as_tool_def"
    )
    tools: list[Any] = [ADDITION_TOOL_SPEC, addition_def, log_adding_two_integers]
    expected_implementations = {
        "add": log_adding_two_integers,
        "add_as_tool_def": log_adding_two_integers,
        "log_adding_two_integers": log_adding_two_integers,
    }
    expected_names = list(expected_implementations.keys())
    expected_param_schemas = 3 * [
        LlmToolParameters(
            type="object",
            properties={"a": {"type": "integer"}, "b": {"type": "integer"}},
            required=["a", "b"],
            additional_properties=None,
        )
    ]
    llm_tools, client_map = ChatResponseEndpoint.parse_tools(tools)
    assert llm_tools.tools is not None
    assert [t.function.name for t in llm_tools.tools] == expected_names
    assert [t.function.parameters for t in llm_tools.tools] == expected_param_schemas
    assert client_map.keys() == set(expected_names)
    client_tools = {k: v[1] for k, v in client_map.items()}
    assert client_tools == expected_implementations


def test_duplicate_tool_names_rejected() -> None:
    addition_def = ToolFunctionDef.from_callable(log_adding_two_integers, name="add")
    tools: list[Any] = [ADDITION_TOOL_SPEC, addition_def]
    with pytest.raises(
        LMStudioValueError, match="Duplicate tool names are not permitted"
    ):
        ChatResponseEndpoint.parse_tools(tools)


async def example_async_tool() -> int:
    """Example asynchronous tool definition"""
    return 42


def test_async_tool_rejected() -> None:
    tools: list[Any] = [example_async_tool]
    with pytest.raises(LMStudioValueError, match=".*example_async_tool.*not supported"):
        ChatResponseEndpoint.parse_tools(tools)


def test_async_tool_accepted() -> None:
    tools: list[Any] = [example_async_tool]
    llm_tools, client_map = ChatResponseEndpoint.parse_tools(tools, allow_async=True)
    assert llm_tools.tools is not None
    assert len(llm_tools.tools) == 1
    assert len(client_map) == 1
