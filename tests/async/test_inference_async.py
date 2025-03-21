"""Test making simple predictions with the API."""

import json
import logging

import anyio
import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import (
    AssistantResponse,
    AsyncClient,
    AsyncPredictionStream,
    Chat,
    LlmInfo,
    LlmLoadModelConfig,
    LlmPredictionConfig,
    LlmPredictionConfigDict,
    LlmPredictionFragment,
    LlmPredictionStats,
    LMStudioModelNotFoundError,
    LMStudioPresetNotFoundError,
    PredictionResult,
    ResponseSchema,
    TextData,
)

from ..support import (
    EXPECTED_LLM_ID,
    GBNF_GRAMMAR,
    PROMPT,
    RESPONSE_FORMATS,
    RESPONSE_SCHEMA,
    SCHEMA_FIELDS,
    SHORT_PREDICTION_CONFIG,
    check_sdk_error,
)


# respond and complete are the same under the hood so we only test respond once
@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_respond_past_history_async(caplog: LogCap) -> None:
    history = Chat("You are an obedient assistant.")
    history.add_user_message("Say something.")
    history.add_assistant_response("Hello, world!")
    history.add_user_message("Respond with exactly what you just said.")
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        response = await llm.respond(history, config=SHORT_PREDICTION_CONFIG)
    logging.info(f"LLM response: {response!r}")
    assert response.content == "Hello, world!"


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_complete_nostream_async(caplog: LogCap) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        response = await llm.complete(prompt, config=SHORT_PREDICTION_CONFIG)
    # The continuation from the LLM will change, but it won't be an empty string
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response, PredictionResult)
    assert response.content


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_complete_stream_async(caplog: LogCap) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        session = client.llm
        prediction_stream = await session._complete_stream(
            model_id, prompt, config=SHORT_PREDICTION_CONFIG
        )
        assert isinstance(prediction_stream, AsyncPredictionStream)
        # Also exercise the explicit context management interface
        async with prediction_stream:
            async for fragment in prediction_stream:
                logging.info(f"Fragment: {fragment}")
                assert fragment.content
                assert isinstance(fragment.content, str)
            response = prediction_stream.result()
    # The continuation from the LLM will change, but it won't be an empty string
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response, PredictionResult)
    assert response.content
    assert response.parsed is response.content


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("format_type", RESPONSE_FORMATS)
async def test_complete_structured_response_format_async(
    format_type: ResponseSchema, caplog: LogCap
) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        response = await llm.complete(prompt, response_format=format_type)
    assert isinstance(response, PredictionResult)
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response.content, str)
    assert isinstance(response.parsed, dict)
    assert response.parsed == json.loads(response.content)
    assert SCHEMA_FIELDS.keys() == response.parsed.keys()


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_complete_structured_config_json_async(caplog: LogCap) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        config: LlmPredictionConfigDict = {
            # snake_case keys are accepted at runtime,
            # but the type hinted spelling is the camelCase names
            # This test case checks the schema field name is converted,
            # but *not* the snake_case and camelCase field names in the
            # schema itself
            "structured": {
                "type": "json",
                "json_schema": RESPONSE_SCHEMA,
            }  # type: ignore[typeddict-item]
        }
        response = await llm.complete(prompt, config=config)
    assert isinstance(response, PredictionResult)
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response.content, str)
    assert isinstance(response.parsed, dict)
    assert response.parsed == json.loads(response.content)
    assert SCHEMA_FIELDS.keys() == response.parsed.keys()


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_complete_structured_config_gbnf_async(caplog: LogCap) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        config: LlmPredictionConfigDict = {
            # snake_case keys are accepted at runtime,
            # but the type hinted spelling is the camelCase names
            # This test case checks the schema field name is converted,
            # but *not* the snake_case and camelCase field names in the
            # schema itself
            "structured": {
                "type": "gbnf",
                "gbnf_grammar": GBNF_GRAMMAR,
            }  # type: ignore[typeddict-item]
        }
        response = await llm.complete(prompt, config=config)
    assert isinstance(response, PredictionResult)
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response.content, str)
    assert isinstance(response.parsed, dict)
    assert response.parsed == json.loads(response.content)
    assert SCHEMA_FIELDS.keys() == response.parsed.keys()


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_callbacks_text_completion_async(caplog: LogCap) -> None:
    messages: list[AssistantResponse] = []
    progress_reports: list[float] = []

    def progress_update(progress: float) -> None:
        assert progress >= 0.0
        assert progress <= 1.0
        if progress_reports:
            assert progress > progress_reports[-1]
        progress_reports.append(progress)

    num_first_token_notifications = 0

    def count_first_token_notification() -> None:
        nonlocal num_first_token_notifications
        num_first_token_notifications += 1

    callback_content: list[str] = []

    def record_fragment(fragment: LlmPredictionFragment) -> None:
        callback_content.append(fragment.content)

    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        # SDK ensures 0.0 and 1.0 prompt processing callbacks are emitted,
        # even if the server doesn't send any prompt processing events
        llm = await client.llm.model(model_id)
        prediction_stream = await llm.complete_stream(
            PROMPT,
            config=SHORT_PREDICTION_CONFIG,
            on_message=messages.append,
            on_first_token=count_first_token_notification,
            on_prediction_fragment=record_fragment,
            on_prompt_processing_progress=progress_update,
        )
        # This test case also covers the explicit context management interface
        iteration_content: list[str] = []
        async with prediction_stream:
            iteration_content = [
                fragment.content async for fragment in prediction_stream
            ]
    assert len(messages) == 1
    message = messages[0]
    assert message.role == "assistant"
    assert len(message.content) == 1
    message_data = message.content[0]
    assert isinstance(message_data, TextData)
    assert message_data.text == "".join(iteration_content)
    assert num_first_token_notifications == 1
    assert callback_content == iteration_content
    assert progress_reports[0] == 0.0
    assert progress_reports[-1] == 1.0


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_callbacks_chat_response_async(caplog: LogCap) -> None:
    messages: list[AssistantResponse] = []
    progress_reports: list[float] = []

    def progress_update(progress: float) -> None:
        assert progress >= 0.0
        assert progress <= 1.0
        if progress_reports:
            assert progress > progress_reports[-1]
        progress_reports.append(progress)

    num_first_token_notifications = 0

    def count_first_token_notification() -> None:
        nonlocal num_first_token_notifications
        num_first_token_notifications += 1

    callback_content: list[str] = []

    def record_fragment(fragment: LlmPredictionFragment) -> None:
        callback_content.append(fragment.content)

    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        # SDK ensures 0.0 and 1.0 prompt processing callbacks are emitted,
        # even if the server doesn't send any prompt processing events
        llm = await client.llm.model(model_id)
        prediction_stream = await llm.respond_stream(
            PROMPT,
            config=SHORT_PREDICTION_CONFIG,
            on_message=messages.append,
            on_first_token=count_first_token_notification,
            on_prediction_fragment=record_fragment,
            on_prompt_processing_progress=progress_update,
        )
        # This test case also covers the explicit context management interface
        iteration_content: list[str] = []
        async with prediction_stream:
            iteration_content = [
                fragment.content async for fragment in prediction_stream
            ]
    assert len(messages) == 1
    message = messages[0]
    assert message.role == "assistant"
    assert len(message.content) == 1
    message_data = message.content[0]
    assert isinstance(message_data, TextData)
    assert message_data.text == "".join(iteration_content)
    assert num_first_token_notifications == 1
    assert callback_content == iteration_content
    assert progress_reports[0] == 0.0
    assert progress_reports[-1] == 1.0


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_complete_prediction_metadata_async(caplog: LogCap) -> None:
    prompt = PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_LLM_ID
    async with AsyncClient() as client:
        llm = await client.llm.model(model_id)
        response = await llm.complete(prompt, config=SHORT_PREDICTION_CONFIG)
    assert isinstance(response, PredictionResult)
    # The initial query from the LLM will change, but we expect it to be a question
    logging.info(f"LLM response: {response.content!r}")
    assert response.stats
    assert response.model_info
    assert response.load_config
    assert response.prediction_config
    assert isinstance(response.stats, LlmPredictionStats)
    assert isinstance(response.model_info, LlmInfo)
    assert isinstance(response.load_config, LlmLoadModelConfig)
    assert isinstance(response.prediction_config, LlmPredictionConfig)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_model_request_nostream_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        # Deliberately create an invalid model handle
        model = client.llm._create_handle("No such model")
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        with anyio.fail_after(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.complete("Some text")
            check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_model_request_stream_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        # Deliberately create an invalid model handle
        model = client.llm._create_handle("No such model")
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        with anyio.fail_after(30):
            prediction_stream = await model.complete_stream("Some text")
            async with prediction_stream:
                with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                    await prediction_stream.wait_for_result()
                check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_preset_request_nostream_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model()
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        with anyio.fail_after(30):
            with pytest.raises(LMStudioPresetNotFoundError) as exc_info:
                await model.complete("Some text", preset="No such preset")
            check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_preset_request_stream_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model()
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        with anyio.fail_after(30):
            prediction_stream = await model.complete_stream(
                "Some text", preset="No such preset"
            )
            async with prediction_stream:
                with pytest.raises(LMStudioPresetNotFoundError) as exc_info:
                    await prediction_stream.wait_for_result()
                check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_cancel_prediction_async(caplog: LogCap) -> None:
    prompt = "This is a test prompt."
    model_id = EXPECTED_LLM_ID
    num_times = 0
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.llm
        stream = await session._complete_stream(model_id, prompt=prompt)
        async for _ in stream:
            await stream.cancel()
            num_times += 1
        assert stream.stats
        assert stream.stats.stop_reason == "userStopped"
        # ensure __aiter__ closes correctly
        assert num_times == 1
