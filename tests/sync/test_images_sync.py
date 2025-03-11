#####################################################################
# This files has been automatically generated from:
#   ../async/test_images_async.py
#
# DO NOT EDIT THIS FILE! Edit the async test case listed above,
# and regenerate the synchronous test cases with async2sync.py
#####################################################################
"""Test uploading and predicting with vision models and images."""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from io import BytesIO

from lmstudio import Client, Chat, FileHandle, LMStudioServerError

from ..support import (
    EXPECTED_VLM_ID,
    IMAGE_FILEPATH,
    SHORT_PREDICTION_CONFIG,
    VLM_PROMPT,
    check_sdk_error,
)


@pytest.mark.lmstudio
def test_upload_from_pathlike_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        session = client._files
        file = session.prepare_file(IMAGE_FILEPATH)
        assert file
        assert isinstance(file, FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.lmstudio
def test_upload_from_file_obj_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        session = client._files
        with open(IMAGE_FILEPATH, "rb") as f:
            file = session.prepare_file(f)
        assert file
        assert isinstance(file, FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.lmstudio
def test_upload_from_bytesio_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with Client() as client:
        session = client._files
        with open(IMAGE_FILEPATH, "rb") as f:
            file = session.prepare_file(BytesIO(f.read()))
        assert file
        assert isinstance(file, FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.slow
@pytest.mark.lmstudio
def test_vlm_predict_sync(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    with Client() as client:
        file_handle = client._files.prepare_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, file_handle))
        vlm = client.llm.model(model_id)
        response = vlm.respond(history, config=SHORT_PREDICTION_CONFIG)
    logging.info(f"VLM response: {response!r}")
    assert response
    assert response.content
    assert isinstance(response.content, str)
    # Sometimes the VLM fails to call out the main color in the image
    assert "purple" in response.content or "image" in response.content


@pytest.mark.lmstudio
def test_non_vlm_predict_sync(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = "hugging-quants/llama-3.2-1b-instruct"
    with Client() as client:
        file_handle = client._files.prepare_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, file_handle))
        llm = client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            llm.respond(history)
        check_sdk_error(exc_info, __file__)


@pytest.mark.slow
@pytest.mark.lmstudio
def test_vlm_predict_image_param_sync(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    with Client() as client:
        file_handle = client._files.prepare_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message(prompt, images=[file_handle])
        vlm = client.llm.model(model_id)
        response = vlm.respond(history, config=SHORT_PREDICTION_CONFIG)
    logging.info(f"VLM response: {response!r}")
    assert response
    assert response.content
    assert isinstance(response.content, str)
    # Sometimes the VLM fails to call out the main color in the image
    assert "purple" in response.content or "image" in response.content


@pytest.mark.lmstudio
def test_non_vlm_predict_image_param_sync(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = "hugging-quants/llama-3.2-1b-instruct"
    with Client() as client:
        file_handle = client._files.prepare_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message(prompt, images=[file_handle])
        llm = client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            llm.respond(history)
        check_sdk_error(exc_info, __file__)
