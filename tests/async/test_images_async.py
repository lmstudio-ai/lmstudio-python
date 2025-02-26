"""Test uploading and predicting with vision models and images."""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from io import BytesIO

from lmstudio import AsyncClient, Chat, _FileHandle, LMStudioServerError

from ..support import (
    EXPECTED_VLM_ID,
    IMAGE_FILEPATH,
    SHORT_PREDICTION_CONFIG,
    VLM_PROMPT,
    check_sdk_error,
)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_upload_from_pathlike_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client._files
        file = await session._add_temp_file(IMAGE_FILEPATH)
        assert file
        assert isinstance(file, _FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_upload_from_file_obj_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client._files
        with open(IMAGE_FILEPATH, "rb") as f:
            file = await session._add_temp_file(f)
        assert file
        assert isinstance(file, _FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_upload_from_bytesio_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client._files
        with open(IMAGE_FILEPATH, "rb") as f:
            file = await session._add_temp_file(BytesIO(f.read()))
        assert file
        assert isinstance(file, _FileHandle)
        logging.info(f"Uploaded file: {file}")


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_vlm_predict_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    async with AsyncClient() as client:
        file_handle = await client._files._add_temp_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, file_handle))
        vlm = await client.llm.model(model_id)
        response = await vlm.respond(history, config=SHORT_PREDICTION_CONFIG)
    logging.info(f"VLM response: {response!r}")
    assert response
    assert response.content
    assert isinstance(response.content, str)
    # Sometimes the VLM fails to call out the main color in the image
    assert "purple" in response.content or "image" in response.content


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_non_vlm_predict_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = "hugging-quants/llama-3.2-1b-instruct"
    async with AsyncClient() as client:
        file_handle = await client._files._add_temp_file(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, file_handle))
        llm = await client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            await llm.respond(history)
        check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_vlm_predict_implicit_file_handles_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    async with AsyncClient() as client:
        history = Chat()
        history.add_user_message(prompt)
        # File handles will be implicitly acquired when preparing the prediction request
        history._add_file(IMAGE_FILEPATH)
        vlm = await client.llm.model(model_id)
        response = await vlm.respond(history, config=SHORT_PREDICTION_CONFIG)
    logging.info(f"VLM response: {response!r}")
    assert response
    assert response.content
    assert isinstance(response.content, str)
    # Sometimes the VLM fails to call out the main color in the image
    assert "purple" in response.content or "image" in response.content


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_non_vlm_predict_implicit_file_handles_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = "hugging-quants/llama-3.2-1b-instruct"
    async with AsyncClient() as client:
        history = Chat()
        history.add_user_message(prompt)
        # File handles will be implicitly acquired when preparing the prediction request
        history._add_file(IMAGE_FILEPATH)
        llm = await client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            await llm.respond(history)
        check_sdk_error(exc_info, __file__)
