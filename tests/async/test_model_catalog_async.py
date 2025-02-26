"""Test listing, downloading, and loading available models."""

import asyncio
import logging

import pytest
from pytest import LogCaptureFixture as LogCap
from pytest_subtests import SubTests

from lmstudio import AsyncClient, LMStudioModelNotFoundError, LMStudioServerError
from lmstudio.json_api import DownloadedModelBase, ModelHandleBase

from ..support import (
    LLM_LOAD_CONFIG,
    EXPECTED_LLM,
    EXPECTED_LLM_DEFAULT_ID,
    EXPECTED_LLM_ID,
    EXPECTED_EMBEDDING,
    EXPECTED_EMBEDDING_DEFAULT_ID,
    EXPECTED_EMBEDDING_ID,
    EXPECTED_VLM_ID,
    TOOL_LLM_ID,
    check_sdk_error,
)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_list_downloaded_llm_async(caplog: LogCap, subtests: SubTests) -> None:
    caplog.set_level(logging.DEBUG)
    subtests_started = subtests_passed = 0
    expected_model: str | None = EXPECTED_LLM
    # Model namespace is omitted so at least one test covers the default value
    async with AsyncClient() as client:
        downloaded_models = await client.llm.list_downloaded()
        assert downloaded_models
        for m in downloaded_models:
            subtests_started += 1
            with subtests.test("Check downloaded model", m=m):
                assert isinstance(m, DownloadedModelBase)
                # Check directly accessible details
                assert m.type == m.info.type
                assert m.path == m.info.path
                assert m.model_key == m.info.model_key
                # Check for expected model
                assert m.type == "llm"
                if expected_model is not None:
                    # Check if this is the expected model
                    if m.path.lower().startswith(expected_model):
                        expected_model = None
                subtests_passed += 1
        # The expected model should be present
        assert expected_model is None

    # Work around pytest-subtests not showing full output when subtests fail
    # https://github.com/pytest-dev/pytest-subtests/issues/76
    assert subtests_passed == subtests_started, "Fail due to failed subtest(s)"


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_list_downloaded_embedding_async(
    caplog: LogCap, subtests: SubTests
) -> None:
    caplog.set_level(logging.DEBUG)
    subtests_started = subtests_passed = 0
    expected_model: str | None = EXPECTED_EMBEDDING
    async with AsyncClient() as client:
        downloaded_models = await client.embedding.list_downloaded()
        assert downloaded_models
        for m in downloaded_models:
            subtests_started += 1
            with subtests.test("Check downloaded model", m=m):
                assert isinstance(m, DownloadedModelBase)
                # Check directly accessible details
                assert m.type == m.info.type
                assert m.path == m.info.path
                assert m.model_key == m.info.model_key
                # Check for expected model
                assert m.type == "embedding"
                if expected_model is not None:
                    # Check if this is the expected model
                    if m.path.lower().startswith(expected_model):
                        expected_model = None
                subtests_passed += 1
        # The expected model should be present
        assert expected_model is None

    # Work around pytest-subtests not failing the test case when subtests fail
    # https://github.com/pytest-dev/pytest-subtests/issues/76
    assert subtests_passed == subtests_started, "Fail due to failed subtest(s)"


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_list_downloaded_models_async(caplog: LogCap, subtests: SubTests) -> None:
    caplog.set_level(logging.DEBUG)
    subtests_started = subtests_passed = 0
    expected_llm: str | None = EXPECTED_LLM
    expected_embedding: str | None = EXPECTED_EMBEDDING
    async with AsyncClient() as client:
        downloaded_models = await client.system.list_downloaded_models()
        assert downloaded_models
        for m in downloaded_models:
            subtests_started += 1
            with subtests.test("Check downloaded model", m=m):
                assert isinstance(m, DownloadedModelBase)
                # Check for expected models
                if m.type == "llm":
                    if expected_llm is not None:
                        # Check if this is the expected LLM
                        if m.path.lower().startswith(expected_llm):
                            expected_llm = None
                elif m.type == "embedding":
                    if expected_embedding is not None:
                        # Check if this is the expected embedding
                        if m.path.lower().startswith(expected_embedding):
                            expected_embedding = None
                subtests_passed += 1
        # The expected models should be present
        assert expected_llm is None
        assert expected_embedding is None


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_list_loaded_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        loaded_models = await client.llm.list_loaded()
        assert loaded_models
        assert all(isinstance(m, ModelHandleBase) for m in loaded_models)
        models = [m.identifier for m in loaded_models]
        assert not (set((EXPECTED_LLM_ID, EXPECTED_VLM_ID, TOOL_LLM_ID)) - set(models))


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_list_loaded_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        loaded_models = await client.embedding.list_loaded()
        assert loaded_models
        assert all(isinstance(m, ModelHandleBase) for m in loaded_models)
        models = [m.identifier for m in loaded_models]
        assert not (set((EXPECTED_EMBEDDING_ID,)) - set(models))


DUPLICATE_MODEL_ERROR = "Model load error.*already exists"


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_load_duplicate_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        llm = client.llm
        initially_loaded_models = sorted(await llm.list_loaded(), key=str)
        with pytest.raises(LMStudioServerError, match=DUPLICATE_MODEL_ERROR):
            # Server will reject an explicitly duplicated model ID
            await llm.load_new_instance(
                EXPECTED_LLM, EXPECTED_LLM_ID, config=LLM_LOAD_CONFIG
            )
        # Let the server assign a new instance identifier
        new_instance = await llm.load_new_instance(EXPECTED_LLM, config=LLM_LOAD_CONFIG)
        assigned_model_id = new_instance.identifier
        with_model_duplicated = sorted(await llm.list_loaded(), key=str)
        await llm.unload(assigned_model_id)
        # Check behaviour now the duplicated model has been unloaded
        assert len(with_model_duplicated) == len(initially_loaded_models) + 1
        model_id_prefix, _, model_id_suffix = assigned_model_id.partition(":")
        assert model_id_prefix == EXPECTED_LLM_ID
        assert model_id_suffix.isascii(), assigned_model_id
        assert model_id_suffix.isdecimal(), assigned_model_id
        with_model_removed = sorted(await llm.list_loaded(), key=str)
        assert with_model_removed == initially_loaded_models


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_load_duplicate_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        embedding = client.embedding
        initially_loaded_models = sorted(await embedding.list_loaded(), key=str)
        with pytest.raises(LMStudioServerError, match=DUPLICATE_MODEL_ERROR):
            # Server will reject an explicitly duplicated model ID
            await embedding.load_new_instance(EXPECTED_EMBEDDING, EXPECTED_EMBEDDING_ID)
        # Let the server assign a new instance identifier
        new_instance = await embedding.load_new_instance(EXPECTED_EMBEDDING)
        assigned_model_id = new_instance.identifier
        with_model_duplicated = sorted(await embedding.list_loaded(), key=str)
        await embedding.unload(assigned_model_id)
        # Check behaviour now the duplicated model has been unloaded
        assert len(with_model_duplicated) == len(initially_loaded_models) + 1
        model_id_prefix, _, model_id_suffix = assigned_model_id.partition(":")
        assert model_id_prefix == EXPECTED_EMBEDDING_ID
        assert model_id_suffix.isascii(), assigned_model_id
        assert model_id_suffix.isdecimal(), assigned_model_id
        with_model_removed = sorted(await embedding.list_loaded(), key=str)
        assert with_model_removed == initially_loaded_models


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_model_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model(EXPECTED_LLM_ID)
        assert model.identifier == EXPECTED_LLM_ID


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_model_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.embedding.model(EXPECTED_EMBEDDING_ID)
        assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_any_model_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model()
        assert model.identifier in (EXPECTED_LLM_ID, EXPECTED_VLM_ID, TOOL_LLM_ID)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_any_model_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.embedding.model()
        assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_unload_request_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        llm = client.llm
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        async with asyncio.timeout(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await llm.unload("No such model")
            check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_invalid_unload_request_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        # This should error rather than timing out,
        # but avoid any risk of the client hanging...
        async with asyncio.timeout(30):
            with pytest.raises(LMStudioModelNotFoundError) as exc_info:
                await client.embedding.unload("No such model")
            check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_or_load_when_loaded_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.llm.model(EXPECTED_LLM)
        assert model.identifier == EXPECTED_LLM_ID


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_get_or_load_when_loaded_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        model = await client.embedding.model(EXPECTED_EMBEDDING)
        assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_get_or_load_when_unloaded_llm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        llm = client.llm
        await llm.unload(EXPECTED_LLM_ID)
        model = await llm.model(EXPECTED_LLM_DEFAULT_ID, config=LLM_LOAD_CONFIG)
        assert model.identifier == EXPECTED_LLM_DEFAULT_ID
        # LM Studio may default to JIT handling for models loaded with `getOrLoad`,
        # so ensure we restore a regular non-JIT instance with no TTL set
        await llm.unload(EXPECTED_LLM_ID)
        model = await llm.load_new_instance(
            EXPECTED_LLM_DEFAULT_ID, config=LLM_LOAD_CONFIG, ttl=None
        )
        assert model.identifier == EXPECTED_LLM_DEFAULT_ID


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_get_or_load_when_unloaded_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        embedding = client.embedding
        await embedding.unload(EXPECTED_EMBEDDING_ID)
        model = await embedding.model(EXPECTED_EMBEDDING_DEFAULT_ID)
        assert model.identifier == EXPECTED_EMBEDDING_DEFAULT_ID
        # LM Studio may default to JIT handling for models loaded with `getOrLoad`,
        # so ensure we restore a regular non-JIT instance with no TTL set
        await embedding.unload(EXPECTED_EMBEDDING_ID)
        model = await embedding.load_new_instance(
            EXPECTED_EMBEDDING_DEFAULT_ID, ttl=None
        )
        assert model.identifier == EXPECTED_EMBEDDING_DEFAULT_ID
