"""Test embedding strings with the API."""

import asyncio
import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import AsyncClient, LMStudioModelNotFoundError

from ..support import (
    EXPECTED_EMBEDDING,
    EXPECTED_EMBEDDING_CONTEXT_LENGTH,
    EXPECTED_EMBEDDING_ID,
    EXPECTED_EMBEDDING_LENGTH,
    check_sdk_error,
)


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_embedding_async(model_id: str, caplog: LogCap) -> None:
    text = "Hello, world!"

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        response = await session._embed(model_id, input=text)
    logging.info(f"Embedding response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == EXPECTED_EMBEDDING_LENGTH
    # the response should be deterministic if we set constant seed
    # so we can also check the value if desired


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_embedding_list_async(model_id: str, caplog: LogCap) -> None:
    text = ["Hello, world!", "Goodbye, world!"]

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        response = await session._embed(model_id, input=text)
    logging.info(f"Embedding response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == len(text)
    assert all(isinstance(embed, list) for embed in response)
    assert all(len(embed) == EXPECTED_EMBEDDING_LENGTH for embed in response)
    # the response should be deterministic if we set constant seed
    # so we can also check the value if desired


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_tokenize_async(model_id: str, caplog: LogCap) -> None:
    text = "Hello, world!"

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        response = await session._tokenize(model_id, input=text)
    logging.info(f"Tokenization response: {response}")
    assert response
    assert isinstance(response, list)
    # the response should be deterministic if we set constant seed
    # so we can also check the value if desired


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_tokenize_list_async(model_id: str, caplog: LogCap) -> None:
    text = ["Hello, world!", "Goodbye, world!"]

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        response = await session._tokenize(model_id, input=text)
    logging.info(f"Tokenization response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == len(text)
    assert all(isinstance(tokens, list) for tokens in response)
    # the response should be deterministic if we set constant seed
    # so we can also check the value if desired


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_context_length_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        response = await session._get_context_length(model_id)
    logging.info(f"Context length response: {response}")
    assert response
    assert isinstance(response, int)
    assert response == EXPECTED_EMBEDDING_CONTEXT_LENGTH


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_get_load_config_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        response = await client.embedding._get_load_config(model_id)
    logging.info(f"Load config response: {response}")
    assert response
    assert isinstance(response, dict)


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_get_model_info_async(model_id: str, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        response = await client.embedding.get_model_info(model_id)
    logging.info(f"Model config response: {response}")
    assert response


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_model_request_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        # Deliberately create an invalid model handle
        model = client.embedding._create_handle("No such model")
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        async with asyncio.timeout(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.embed("Some text")
            check_sdk_error(exc_info, __file__)
        async with asyncio.timeout(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.tokenize("Some text")
            check_sdk_error(exc_info, __file__)
        async with asyncio.timeout(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await model.get_context_length()
            check_sdk_error(exc_info, __file__)
