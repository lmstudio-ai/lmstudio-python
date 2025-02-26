"""Test model handles (AsyncLLM, AsyncEmbeddingModel) with the API.

Because these methods are defined specifically such that ALL THEY DO
is pass in a `self.identifier` parameter to the parent functions,
any errors in here are likely to be in the parent functions.
"""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import AsyncClient, PredictionResult

from ..support import (
    EXPECTED_EMBEDDING,
    EXPECTED_EMBEDDING_ID,
    EXPECTED_EMBEDDING_LENGTH,
    EXPECTED_LLM,
    EXPECTED_LLM_ID,
    SHORT_PREDICTION_CONFIG,
)

# TODO: include several mock-based test cases here, as the important
#       functionality is actually in ensuring that the model wrappers
#       call the underlying session APIs with the model identifier
#       filled in appropriately. These cases can also then be executed
#       in CI without needing a live LM Studio instance.


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
async def test_completion_llm_handle_async(model_id: str, caplog: LogCap) -> None:
    prompt = "Hello"

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.llm
        lm = await session.model(model_id)
        response = await lm.complete(prompt=prompt, config=SHORT_PREDICTION_CONFIG)
    # The continuation from the LLM will change, but it won't be an empty string
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response, PredictionResult)
    assert response.content


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
async def test_embedding_handle_async(model_id: str, caplog: LogCap) -> None:
    text = "Hello, world!"

    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.embedding
        embedding = await session.model(model_id)
        response = await embedding.embed(input=text)
    logging.info(f"Embedding response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == EXPECTED_EMBEDDING_LENGTH
