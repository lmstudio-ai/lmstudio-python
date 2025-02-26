#####################################################################
# This files has been automatically generated from:
#   ../async/test_model_handles_async.py
#
# DO NOT EDIT THIS FILE! Edit the async test case listed above,
# and regenerate the synchronous test cases with async2sync.py
#####################################################################
"""Test model handles (LLM, EmbeddingModel) with the API.

Because these methods are defined specifically such that ALL THEY DO
is pass in a `self.identifier` parameter to the parent functions,
any errors in here are likely to be in the parent functions.
"""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import Client, PredictionResult

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


@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM, EXPECTED_LLM_ID))
def test_completion_llm_handle_sync(model_id: str, caplog: LogCap) -> None:
    prompt = "Hello"

    caplog.set_level(logging.DEBUG)
    with Client() as client:
        session = client.llm
        lm = session.model(model_id)
        response = lm.complete(prompt=prompt, config=SHORT_PREDICTION_CONFIG)
    # The continuation from the LLM will change, but it won't be an empty string
    logging.info(f"LLM response: {response!r}")
    assert isinstance(response, PredictionResult)
    assert response.content


@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID))
def test_embedding_handle_sync(model_id: str, caplog: LogCap) -> None:
    text = "Hello, world!"

    caplog.set_level(logging.DEBUG)
    with Client() as client:
        session = client.embedding
        embedding = session.model(model_id)
        response = embedding.embed(input=text)
    logging.info(f"Embedding response: {response}")
    assert response
    assert isinstance(response, list)
    assert len(response) == EXPECTED_EMBEDDING_LENGTH
