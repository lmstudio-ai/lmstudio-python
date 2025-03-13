"""Test listing, downloading, and loading available models."""

import logging

from contextlib import suppress

import anyio
import pytest
from pytest import LogCaptureFixture as LogCap
from pytest_subtests import SubTests

from lmstudio import AsyncClient, LMStudioModelNotFoundError, LMStudioServerError
from lmstudio.json_api import DownloadedModelBase, ModelHandleBase

from ..support import (
    LLM_LOAD_CONFIG,
    EXPECTED_LLM,
    EXPECTED_LLM_ID,
    EXPECTED_EMBEDDING,
    EXPECTED_EMBEDDING_ID,
    EXPECTED_VLM_ID,
    SMALL_LLM_ID,
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
        with anyio.fail_after(30):
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
        with anyio.fail_after(30):
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
        with suppress(LMStudioModelNotFoundError):
            await llm.unload(EXPECTED_LLM_ID)
        model = await llm.model(EXPECTED_LLM_ID, config=LLM_LOAD_CONFIG)
        assert model.identifier == EXPECTED_LLM_ID
        # LM Studio may default to JIT handling for models loaded with `getOrLoad`,
        # so ensure we restore a regular non-JIT instance with no TTL set
        await model.unload()
        model = await llm.load_new_instance(
            EXPECTED_LLM_ID, config=LLM_LOAD_CONFIG, ttl=None
        )
        assert model.identifier == EXPECTED_LLM_ID


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_get_or_load_when_unloaded_embedding_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        embedding = client.embedding
        with suppress(LMStudioModelNotFoundError):
            await embedding.unload(EXPECTED_EMBEDDING_ID)
        model = await embedding.model(EXPECTED_EMBEDDING_ID)
        assert model.identifier == EXPECTED_EMBEDDING_ID
        # LM Studio may default to JIT handling for models loaded with `getOrLoad`,
        # so ensure we restore a regular non-JIT instance with no TTL set
        await model.unload()
        model = await embedding.load_new_instance(EXPECTED_EMBEDDING_ID, ttl=None)
        assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_jit_unloading_async(caplog: LogCap) -> None:
    # For the time being, only test the embedding vs LLM cross-namespace
    # JIT unloading (since that ensures the info type mixing is handled).
    # Assuming LM Studio eventually switches to per-namespace JIT unloading,
    # this can be split into separate LLM and embedding test cases at that time.
    caplog.set_level(logging.DEBUG)
    async with AsyncClient() as client:
        # Unload the non-JIT instance of the embedding model
        with suppress(LMStudioModelNotFoundError):
            await client.embedding.unload(EXPECTED_EMBEDDING_ID)
        # Load a JIT instance of the embedding model
        model1 = await client.embedding.model(EXPECTED_EMBEDDING_ID, ttl=300)
        assert model1.identifier == EXPECTED_EMBEDDING_ID
        model1_info = await model1.get_info()
        assert model1_info.identifier == model1.identifier
        # Load a JIT instance of the small testing LLM
        # This will unload the JIT instance of the testing embedding model
        model2 = await client.llm.model(SMALL_LLM_ID, ttl=300)
        assert model2.identifier == SMALL_LLM_ID
        model2_info = await model2.get_info()
        assert model2_info.identifier == model2.identifier
        # Attempting to query the now unloaded JIT embedding model will fail
        with pytest.raises(LMStudioModelNotFoundError):
            await model1.get_info()
        # Restore things to the way other test cases expect them to be
        await model2.unload()
        model = await client.embedding.load_new_instance(
            EXPECTED_EMBEDDING_ID, ttl=None
        )
        assert model.identifier == EXPECTED_EMBEDDING_ID

    # Check for expected log messages
    jit_unload_event = "Unloading other JIT model"
    jit_unload_messages_debug: list[str] = []
    jit_unload_messages_info: list[str] = []
    jit_unload_messages = {
        logging.DEBUG: jit_unload_messages_debug,
        logging.INFO: jit_unload_messages_info,
    }
    for _logger_name, log_level, message in caplog.record_tuples:
        if jit_unload_event not in message:
            continue
        jit_unload_messages[log_level].append(message)

    assert len(jit_unload_messages_info) == 1
    assert len(jit_unload_messages_debug) == 1

    info_message = jit_unload_messages_info[0]
    debug_message = jit_unload_messages_debug[0]
    # Ensure info message omits model info, but includes config guidance
    unload_notice = f'"event": "{jit_unload_event}"'
    assert unload_notice in info_message
    loading_model_notice = f'"model_key": "{SMALL_LLM_ID}"'
    assert loading_model_notice in info_message
    unloaded_model_notice = f'"unloaded_model_key": "{EXPECTED_EMBEDDING_ID}"'
    assert unloaded_model_notice in info_message
    assert '"suggestion": ' in info_message
    assert "disable this behavior" in info_message
    assert '"unloaded_model": ' not in info_message
    # Ensure debug message includes model info, but omits config guidance
    assert unload_notice in debug_message
    assert loading_model_notice in info_message
    assert unloaded_model_notice in debug_message
    assert '"suggestion": ' not in debug_message
    assert "disable this behavior" not in debug_message
    assert '"unloaded_model": ' in debug_message
