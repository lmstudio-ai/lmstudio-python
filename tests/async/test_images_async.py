"""Test uploading and predicting with vision models and images."""

import logging

import pytest
from pytest import LogCaptureFixture as LogCap

from io import BytesIO

from lmstudio import AsyncClient, Chat, FileHandle, LMStudioServerError, LocalFileInput

from ..support import (
    EXPECTED_VLM_ID,
    IMAGE_FILEPATH,
    SHORT_PREDICTION_CONFIG,
    VLM_PROMPT,
    check_sdk_error,
)

_IMAGE_DATA = IMAGE_FILEPATH.read_bytes()

_FILE_INPUT_CASES: list[tuple[str, LocalFileInput]] = [
    ("filesystem path", IMAGE_FILEPATH),
    ("bytes IO stream", BytesIO(_IMAGE_DATA)),
    ("raw bytes", _IMAGE_DATA),
    ("mutable buffer", bytearray(_IMAGE_DATA)),
    ("memoryview", memoryview(_IMAGE_DATA)),
]
_FILE_INPUT_CASE_IDS = [case[0] for case in _FILE_INPUT_CASES]


@pytest.mark.asyncio
@pytest.mark.lmstudio
@pytest.mark.parametrize(
    "input_kind,file_input", _FILE_INPUT_CASES, ids=_FILE_INPUT_CASE_IDS
)
async def test_prepare_async(
    caplog: LogCap, input_kind: str, file_input: LocalFileInput
) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.files
        file = await session._prepare_file(file_input)
        assert file
        assert isinstance(file, FileHandle)
        logging.info(f"Uploaded file from {input_kind}: {file}")
        image = await session.prepare_image(file_input)
        assert image
        assert isinstance(image, FileHandle)
        logging.info(f"Uploaded image from {input_kind}: {image}")
        # Even with the same data uploaded, assigned identifiers should differ
        assert image != file


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_prepare_from_file_obj_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        session = client.files
        with open(IMAGE_FILEPATH, "rb") as f:
            file = await session._prepare_file(f)
        assert file
        assert isinstance(file, FileHandle)
        logging.info(f"Uploaded file from file object: {file}")
        with open(IMAGE_FILEPATH, "rb") as f:
            image = await session.prepare_image(f)
        assert image
        assert isinstance(image, FileHandle)
        logging.info(f"Uploaded image from file object: {image}")
        # Even with the same data uploaded, assigned identifiers should differ
        assert image != file


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_vlm_predict_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    async with AsyncClient() as client:
        image_handle = await client.files.prepare_image(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, image_handle))
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
        image_handle = await client.files.prepare_image(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message((prompt, image_handle))
        llm = await client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            await llm.respond(history)
        check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_vlm_predict_image_param_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = EXPECTED_VLM_ID
    async with AsyncClient() as client:
        image_handle = await client.files.prepare_image(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message(prompt, images=[image_handle])
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
async def test_non_vlm_predict_image_param_async(caplog: LogCap) -> None:
    prompt = VLM_PROMPT
    caplog.set_level(logging.DEBUG)
    model_id = "hugging-quants/llama-3.2-1b-instruct"
    async with AsyncClient() as client:
        image_handle = await client.files.prepare_image(IMAGE_FILEPATH)
        history = Chat()
        history.add_user_message(prompt, images=[image_handle])
        llm = await client.llm.model(model_id)
        with pytest.raises(LMStudioServerError) as exc_info:
            await llm.respond(history)
        check_sdk_error(exc_info, __file__)
