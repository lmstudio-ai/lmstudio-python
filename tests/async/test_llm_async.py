"""Test non-inference methods on LLMs."""

import logging

import anyio
import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import (
    AsyncClient,
    LlmLoadModelConfig,
    LMStudioModelNotFoundError,
    history,
)

from ..support import EXPECTED_LLM, EXPECTED_LLM_ID, check_sdk_error


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_apply_prompt_template_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    file_data = history.FileHandle(
        name="someFile.txt",
        identifier="some-file",
        size_bytes=100,
        file_type="text/plain",
    )
    other_file_data = {
        "name": "someOtherFile.txt",
        "identifier": "some-other-file",
        "sizeBytes": 100,
        # Ensure snake_case field is normalised before sending
        "file_type": "text/plain",
    }
    context = history.Chat("Initial system messages")
    context.add_user_message("Simple text prompt")
    context.add_user_message(history.TextData(text="Structured text prompt"))
    context.add_user_message(file_data)
    context.add_user_message(other_file_data)
    context.add_system_prompt("Simple text prompt")
    context.add_assistant_response("Simple text response")
    accumulated_history = context._get_history_for_prediction()
    async with AsyncClient() as client:
        templated = await client.llm._apply_prompt_template(
            model_id, accumulated_history
        )
    logging.info(f"Prompt template: {templated}")
    assert templated


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_tokenize_async(model_id: str, caplog: LogCap) -> None:
    text = "Hello, world!"

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model(model_id)
        num_tokens = await model.count_tokens(text)
        response = await model.tokenize(text)
    logging.info(f"Tokenization response: {response}")
    assert response
    assert isinstance(response, list)
    # Ensure token count and tokenization are consistent
    assert len(response) == num_tokens


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_tokenize_list_async(model_id: str, caplog: LogCap) -> None:
    text = ["Hello, world!", "Goodbye, world!"]

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model(model_id)
        response = await model.tokenize(text)
    logging.info(f"Tokenization response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == len(text)
    assert all(isinstance(tokens, list) for tokens in response)


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_context_length_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        response = await client.llm._get_context_length(model_id)
    logging.info(f"Context length response: {response}")
    assert response
    assert isinstance(response, int)
    assert response > 0


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_get_load_config_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model(model_id)
        response = await model.get_load_config()
    logging.info(f"Load config response: {response}")
    assert response
    assert isinstance(response, LlmLoadModelConfig)


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_get_model_info_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        response = await client.llm.get_model_info(model_id)
    logging.info(f"Model config response: {response}")
    assert response


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_model_request_async(caplog: LogCap) -> None:
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
        with anyio.fail_after(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.respond("Some text")
            check_sdk_error(exc_info, __file__)
        with anyio.fail_after(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.count_tokens("Some text")
        with anyio.fail_after(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.tokenize("Some text")
            check_sdk_error(exc_info, __file__)
        with anyio.fail_after(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.get_context_length()
            check_sdk_error(exc_info, __file__)
