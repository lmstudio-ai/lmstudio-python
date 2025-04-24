"""Test the synchronous convenience API intended for interactive use."""

# Note: before testing additional functionality (such as passing configs),
#       this should be migrated to mock-style testing rather than end-to-end

import lmstudio as lms

import pytest

from .support import (
    EXPECTED_EMBEDDING_ID,
    EXPECTED_LLM_ID,
    EXPECTED_VLM_ID,
    IMAGE_FILEPATH,
    TOOL_LLM_ID,
    closed_api_host,
)


@pytest.mark.lmstudio
def test_get_default_client() -> None:
    client = lms.get_default_client()
    assert isinstance(client, lms.Client)
    # Setting the API host after creation is disallowed (even if it is consistent)
    with pytest.raises(lms.LMStudioClientError, match="already created"):
        lms.get_default_client("localhost:1234")
    # Ensure configured API host is used
    lms.sync_api._reset_default_client()
    try:
        with pytest.raises(lms.LMStudioWebsocketError, match="not reachable"):
            # Actually try to use the client in order to force a connection attempt
            lms.get_default_client(closed_api_host()).list_loaded_models()
    finally:
        lms.sync_api._reset_default_client()


@pytest.mark.lmstudio
def test_configure_default_client() -> None:
    # Ensure the default client already exists
    client = lms.get_default_client()
    assert isinstance(client, lms.Client)
    # Setting the API host after creation is disallowed (even if it is consistent)
    with pytest.raises(lms.LMStudioClientError, match="already created"):
        lms.configure_default_client("localhost:1234")
    # Ensure configured API host is used
    lms.sync_api._reset_default_client()
    try:
        lms.configure_default_client(closed_api_host())
        with pytest.raises(lms.LMStudioWebsocketError, match="not reachable"):
            # Actually try to use the client in order to force a connection attempt
            lms.get_default_client().list_loaded_models()
    finally:
        lms.sync_api._reset_default_client()


@pytest.mark.lmstudio
def test_llm_any() -> None:
    model = lms.llm()
    assert model.identifier in (EXPECTED_LLM_ID, EXPECTED_VLM_ID, TOOL_LLM_ID)


@pytest.mark.lmstudio
@pytest.mark.parametrize("model_id", (EXPECTED_LLM_ID, EXPECTED_VLM_ID, TOOL_LLM_ID))
def test_llm_specific(model_id: str) -> None:
    model = lms.llm(model_id)
    assert model.identifier == model_id


@pytest.mark.lmstudio
def test_embedding_any() -> None:
    model = lms.embedding_model()
    assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.lmstudio
def test_embedding_specific() -> None:
    model = lms.embedding_model(EXPECTED_EMBEDDING_ID)
    assert model.identifier == EXPECTED_EMBEDDING_ID


@pytest.mark.lmstudio
def test_prepare_file() -> None:
    name = "example-file.txt"
    raw_data = b"raw data"
    file_handle = lms.sync_api._prepare_file(raw_data, name)
    assert file_handle.name == name
    assert file_handle.size_bytes == len(raw_data)
    assert file_handle.file_type == "text/plain"


@pytest.mark.lmstudio
def test_prepare_image() -> None:
    file_handle = lms.prepare_image(IMAGE_FILEPATH)
    assert file_handle.name == IMAGE_FILEPATH.name
    assert file_handle.size_bytes == len(IMAGE_FILEPATH.read_bytes())
    assert file_handle.file_type == "image"


@pytest.mark.lmstudio
def test_list_downloaded_models() -> None:
    all_models = [m.model_key for m in lms.list_downloaded_models()]
    embedding_models = [m.model_key for m in lms.list_downloaded_models("embedding")]
    llms = [m.model_key for m in lms.list_downloaded_models("llm")]
    assert set(all_models) == (set(embedding_models) | set(llms))


@pytest.mark.lmstudio
def test_list_loaded_models() -> None:
    all_models = [m.identifier for m in lms.list_loaded_models()]
    embedding_models = [m.identifier for m in lms.list_loaded_models("embedding")]
    llms = [m.identifier for m in lms.list_loaded_models("llm")]
    assert set(all_models) == (set(embedding_models) | set(llms))


@pytest.mark.lmstudio
def test_list_loaded_embedding_models() -> None:
    models = [m.identifier for m in lms.list_loaded_models("embedding")]
    assert not (set((EXPECTED_EMBEDDING_ID,)) - set(models))


@pytest.mark.lmstudio
def test_list_loaded_LLMs() -> None:
    models = [m.identifier for m in lms.list_loaded_models("llm")]
    assert not (set((EXPECTED_LLM_ID, EXPECTED_VLM_ID, TOOL_LLM_ID)) - set(models))
