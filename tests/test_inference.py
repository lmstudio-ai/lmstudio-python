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
    Client,
    LlmPredictionConfig,
    LlmPredictionFragment,
    LMStudioPredictionError,
    LMStudioValueError,
    PredictionResult,
    PredictionRoundResult,
    ToolCallRequest,
    ToolFunctionDef,
    ToolFunctionDefDict,
)
from lmstudio.json_api import ChatResponseEndpoint
from lmstudio._sdk_models import LlmToolParameters

from .support import (
    EXPECTED_LLM_ID,
    MAX_PREDICTED_TOKENS,
    SHORT_PREDICTION_CONFIG,
    TOOL_LLM_ID,
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


def log_adding_two_integers(a: int, b: int) -> int:
    """Log adding two integers together."""
    logging.info(f"Tool call: Adding {a!r} to {b!r} as integers")
    return int(a) + int(b)


ADDITION_TOOL_SPEC: ToolFunctionDefDict = {
    "name": "add",
    "description": "Add two numbers",
    "parameters": {
        "a": int,
        "b": int,
    },
    "implementation": log_adding_two_integers,
}


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


@pytest.mark.lmstudio
def test_tool_using_agent(caplog: LogCap) -> None:
    # This is currently a sync-only API (it will be refactored in a future release)

    caplog.set_level(logging.DEBUG)
    model_id = TOOL_LLM_ID
    with Client() as client:
        llm = client.llm.model(model_id)
        chat = Chat()
        chat.add_user_message("What is the sum of 123 and 3210?")
        tools = [ADDITION_TOOL_SPEC]
        # Ensure ignoring the round index passes static type checks
        predictions: list[PredictionResult] = []

        act_result = llm.act(chat, tools, on_prediction_completed=predictions.append)
        assert len(predictions) > 1
        assert act_result.rounds == len(predictions)
        assert "3333" in predictions[-1].content

    for _logger_name, log_level, message in caplog.record_tuples:
        if log_level != logging.INFO:
            continue
        if message.startswith("Tool call:"):
            break
    else:
        assert False, "Failed to find tool call logging entry"
    assert "123" in message
    assert "3210" in message


@pytest.mark.lmstudio
def test_tool_using_agent_callbacks(caplog: LogCap) -> None:
    # This is currently a sync-only API (it will be refactored in a future release)

    caplog.set_level(logging.DEBUG)
    model_id = TOOL_LLM_ID
    with Client() as client:
        llm = client.llm.model(model_id)
        chat = Chat()
        # Ensure the first response is a combination of text and tool use requests
        chat.add_user_message("First say 'Hi'. Then calculate 1 + 3 with the tool.")
        tools = [ADDITION_TOOL_SPEC]
        round_starts: list[int] = []
        round_ends: list[int] = []
        first_tokens: list[int] = []
        predictions: list[PredictionRoundResult] = []
        fragments: list[LlmPredictionFragment] = []
        fragment_round_indices: set[int] = set()

        def _append_fragment(f: LlmPredictionFragment, round_index: int) -> None:
            last_fragment_round_index = max(fragment_round_indices, default=-1)
            assert round_index >= last_fragment_round_index
            fragments.append(f)
            fragment_round_indices.add(round_index)

        # TODO: Also check on_prompt_processing_progress and handling invalid messages
        # (although it isn't clear how to provoke calls to the latter without mocking)
        act_result = llm.act(
            chat,
            tools,
            on_first_token=first_tokens.append,
            on_prediction_fragment=_append_fragment,
            on_message=chat.append,
            on_round_start=round_starts.append,
            on_round_end=round_ends.append,
            on_prediction_completed=predictions.append,
        )
        num_rounds = act_result.rounds
        sequential_round_indices = list(range(num_rounds))
        assert num_rounds > 1
        assert [p.round_index for p in predictions] == sequential_round_indices
        assert round_starts == sequential_round_indices
        assert round_ends == sequential_round_indices
        expected_token_indices = [p.round_index for p in predictions if p.content]
        assert expected_token_indices == sequential_round_indices
        assert first_tokens == expected_token_indices
        assert fragment_round_indices == set(expected_token_indices)
        assert len(chat._messages) == 2 * num_rounds  # No tool results in last round

        cloned_chat = chat.copy()
        assert cloned_chat._messages == chat._messages


def divide(numerator: float, denominator: float) -> float:
    """Divide the given numerator by the given denominator. Return the result."""
    return numerator / denominator


@pytest.mark.lmstudio
def test_tool_using_agent_error_handling(caplog: LogCap) -> None:
    # This is currently a sync-only API (it will be refactored in a future release)

    caplog.set_level(logging.DEBUG)
    model_id = TOOL_LLM_ID
    with Client() as client:
        llm = client.llm.model(model_id)
        chat = Chat()
        chat.add_user_message(
            "Attempt to divide 1 by 0 using the tool. Explain the result."
        )
        tools = [divide]
        predictions: list[PredictionRoundResult] = []
        request_failures: list[LMStudioPredictionError] = []

        def _handle_invalid_request(
            exc: LMStudioPredictionError, request: ToolCallRequest | None
        ) -> None:
            if request is not None:
                request_failures.append(exc)

        act_result = llm.act(
            chat,
            tools,
            handle_invalid_tool_request=_handle_invalid_request,
            on_prediction_completed=predictions.append,
        )
        assert len(predictions) > 1
        assert act_result.rounds == len(predictions)
        # Ensure the tool call failure was reported to the user callback
        assert len(request_failures) == 1
        tool_failure_exc = request_failures[0]
        assert isinstance(tool_failure_exc, LMStudioPredictionError)
        assert isinstance(tool_failure_exc.__cause__, ZeroDivisionError)
        # If the content checks prove too flaky in practice, they can be dropped
        completed_response = predictions[-1].content.lower()
        assert "divid" in completed_response  # Accepts both "divide" and "dividing"
        assert "zero" in completed_response
