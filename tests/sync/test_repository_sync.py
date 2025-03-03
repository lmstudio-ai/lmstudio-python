#####################################################################
# This files has been automatically generated from:
#   ../async/test_repository_async.py
#
# DO NOT EDIT THIS FILE! Edit the async test case listed above,
# and regenerate the synchronous test cases with async2sync.py
#####################################################################
"""Test downloading models through the repository namespace."""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import Client, LMStudioClientError

from ..support import SMALL_LLM_SEARCH_TERM


# N.B. We can maybe provide a reference list for what should be available
# if we narrow down the query enough, since it shouldn't really change.
# These also have to be tested in tandem because the model identifiers
# passed between methods are session-specific.
# You also need to delete the downloaded file after every test.
@pytest.mark.slow
@pytest.mark.lmstudio
def test_download_model_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        models = client.repository.search_models(SMALL_LLM_SEARCH_TERM)
        logging.info(f"Models: {models}")
        assert models
        assert isinstance(models, list)
        assert len(models) > 0

        options = models[0].get_download_options()
        logging.info(f"Download options: {options}")
        assert options
        assert isinstance(options, list)
        assert len(options) > 0

        model_path = options[0].download()
        logging.info(f"Downloaded model identifier: {model_path}")
        assert model_path
        assert isinstance(model_path, str)


@pytest.mark.slow
@pytest.mark.lmstudio
def test_get_options_out_of_session_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        models = client.repository.search_models(SMALL_LLM_SEARCH_TERM)
        assert models
        assert isinstance(models, list)
        assert len(models) > 0

    with pytest.raises(LMStudioClientError):
        models[0].get_download_options()


@pytest.mark.slow
@pytest.mark.lmstudio
def test_download_out_of_session_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        models = client.repository.search_models(SMALL_LLM_SEARCH_TERM)
        logging.info(f"Models: {models}")
        assert models
        assert isinstance(models, list)
        assert len(models) > 0

        options = models[0].get_download_options()
        assert options
        assert isinstance(options, list)
        assert len(options) > 0

    with pytest.raises(LMStudioClientError):
        options[0].download()
