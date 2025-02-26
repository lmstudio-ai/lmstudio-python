"""Test chat history management."""

import copy
import json

from typing import Callable, cast

import pytest

from lmstudio.sdk_api import LMStudioOSError, LMStudioRuntimeError
from lmstudio.schemas import DictObject
from lmstudio.history import (
    AnyChatMessageInput,
    Chat,
    AnyChatMessageDict,
    ChatHistoryData,
    ChatHistoryDataDict,
    _FileHandle,
    _FileHandleDict,
    _LocalFileData,
    TextData,
)
from lmstudio.json_api import (
    LlmInfo,
    LlmPredictionStats,
    PredictionResult,
    TPrediction,
)

from .support import IMAGE_FILEPATH, check_sdk_error

INPUT_ENTRIES: list[DictObject] = [
    # Entries with multi-word keys mix snake_case and camelCase
    # to ensure both are accepted and normalized (to camelCase)
    {
        "role": "system",
        "content": [
            {"type": "text", "text": "Initial system messages"},
        ],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Simple text prompt"}],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Structured text prompt"}],
    },
    {
        "role": "user",
        "content": [
            {
                "type": "file",
                "name": "someFile.txt",
                "identifier": "some-file",
                "size_bytes": 100,
                "fileType": "text/plain",
            }
        ],
    },
    {
        "role": "user",
        "content": [
            {
                "type": "file",
                "name": "someOtherFile.txt",
                "identifier": "some-other-file",
                "sizeBytes": 100,
                "file_type": "text/plain",
            }
        ],
    },
    {
        "role": "system",
        "content": [{"type": "text", "text": "Simple text system prompt"}],
    },
    {
        "role": "assistant",
        "content": [{"type": "text", "text": "Simple text response"}],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [{"type": "text", "text": "Structured text response"}],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "file",
                "name": "someFile.txt",
                "identifier": "some-file",
                "size_bytes": 100,
                "fileType": "text/plain",
            }
        ],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "file",
                "name": "someOtherFile.txt",
                "identifier": "some-other-file",
                "sizeBytes": 100,
                "file_type": "text/plain",
            }
        ],
    },
    {
        "role": "system",
        "content": [{"type": "text", "text": "Structured text system prompt"}],
    },
]

INPUT_HISTORY = {"messages": INPUT_ENTRIES}

# Consecutive user and assistant messages should be merged
EXPECTED_MESSAGES: list[AnyChatMessageDict] = [
    {
        "role": "system",
        "content": [
            {"type": "text", "text": "Initial system messages"},
        ],
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Simple text prompt"},
            {"type": "text", "text": "Structured text prompt"},
            {
                "type": "file",
                "name": "someFile.txt",
                "identifier": "some-file",
                "sizeBytes": 100,
                "fileType": "text/plain",
            },
            {
                "type": "file",
                "name": "someOtherFile.txt",
                "identifier": "some-other-file",
                "sizeBytes": 100,
                "fileType": "text/plain",
            },
        ],
    },
    {
        "role": "system",
        "content": [{"type": "text", "text": "Simple text system prompt"}],
    },
    {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Simple text response"},
        ],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Structured text response"},
        ],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "file",
                "name": "someFile.txt",
                "identifier": "some-file",
                "sizeBytes": 100,
                "fileType": "text/plain",
            },
        ],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "Avoid consecutive responses"}],
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "file",
                "name": "someOtherFile.txt",
                "identifier": "some-other-file",
                "sizeBytes": 100,
                "fileType": "text/plain",
            },
        ],
    },
    {
        "role": "system",
        "content": [{"type": "text", "text": "Structured text system prompt"}],
    },
]


EXPECTED_HISTORY: ChatHistoryDataDict = {"messages": EXPECTED_MESSAGES}


def test_from_history() -> None:
    # We *expect* the input to fail static typechecking here,
    # as it's relying on the convenience input transformations
    chat = Chat.from_history(INPUT_HISTORY)  # type: ignore[arg-type]
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY
    cloned_chat = Chat.from_history(chat._history)
    assert cloned_chat._get_history_for_prediction() == EXPECTED_HISTORY


def test_from_history_with_simple_text() -> None:
    message = "This is a basic text message"
    # Plain string should be converted to a single user message
    expected_text_content = {"type": "text", "text": message}
    expected_user_message = {
        "role": "user",
        "content": [expected_text_content],
    }
    expected_history = {"messages": [expected_user_message]}
    chat = Chat.from_history(message)
    assert chat._get_history_for_prediction() == expected_history
    # Plain strings should also be accepted as a text content field
    input_history = {
        "messages": [
            {"role": "user", "content": message},
            {"role": "system", "content": message},
        ]
    }
    expected_system_message = {
        "role": "system",
        "content": [expected_text_content],
    }
    expected_history = {"messages": [expected_user_message, expected_system_message]}
    # We *expect* the input to fail static typechecking here,
    # as it's relying on the convenience input transformations
    chat = Chat.from_history(input_history)  # type: ignore[arg-type]
    assert chat._get_history_for_prediction() == expected_history


INPUT_FILE_HANDLE = _FileHandle(
    name="someFile.txt",
    identifier="some-file",
    size_bytes=100,
    file_type="text/plain",
)
INPUT_FILE_HANDLE_DICT: _FileHandleDict = {
    "type": "file",
    "name": "someOtherFile.txt",
    "identifier": "some-other-file",
    "sizeBytes": 100,
    "fileType": "text/plain",
}


def test_get_history() -> None:
    # Also tests the specific message addition methods
    chat = Chat("Initial system messages")
    chat.add_user_message("Simple text prompt")
    chat.add_user_message(TextData(text="Structured text prompt"))
    chat.add_user_message(INPUT_FILE_HANDLE)
    chat.add_user_message(INPUT_FILE_HANDLE_DICT)
    chat.add_system_prompt("Simple text system prompt")
    chat.add_assistant_response("Simple text response")
    chat.add_user_message("Avoid consecutive responses")
    chat.add_assistant_response(TextData(text="Structured text response"))
    chat.add_user_message("Avoid consecutive responses")
    chat.add_assistant_response(INPUT_FILE_HANDLE)
    chat.add_user_message("Avoid consecutive responses")
    chat.add_assistant_response(INPUT_FILE_HANDLE_DICT)
    chat.add_system_prompt(TextData(text="Structured text system prompt"))
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY


def test_add_entry() -> None:
    chat = Chat("Initial system messages")
    chat.add_entry("user", "Simple text prompt")
    chat.add_entry("user", TextData(text="Structured text prompt"))
    chat.add_entry("user", INPUT_FILE_HANDLE)
    chat.add_entry("user", INPUT_FILE_HANDLE_DICT)
    chat.add_entry("system", "Simple text system prompt")
    chat.add_entry("assistant", "Simple text response")
    chat.add_entry("user", "Avoid consecutive responses")
    chat.add_entry("assistant", TextData(text="Structured text response"))
    chat.add_entry("user", "Avoid consecutive responses")
    chat.add_entry("assistant", INPUT_FILE_HANDLE)
    chat.add_entry("user", "Avoid consecutive responses")
    chat.add_entry("assistant", INPUT_FILE_HANDLE_DICT)
    chat.add_entry("system", TextData(text="Structured text system prompt"))
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY


def test_add_entries_dict_content() -> None:
    history_data = EXPECTED_MESSAGES
    chat = Chat()
    chat._add_entries(history_data)
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY


def test_add_entries_tuple_content() -> None:
    history_data: list[tuple[str, AnyChatMessageInput]] = [
        (m["role"], cast(AnyChatMessageInput, m["content"])) for m in EXPECTED_MESSAGES
    ]
    chat = Chat()
    chat._add_entries(history_data)
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY


def test_add_entries_class_content() -> None:
    history_data = ChatHistoryData.from_dict(EXPECTED_HISTORY).messages
    chat = Chat()
    chat._add_entries(history_data)
    assert chat._get_history_for_prediction() == EXPECTED_HISTORY


def _make_prediction_result(data: TPrediction) -> PredictionResult[TPrediction]:
    return PredictionResult(
        content=(data if isinstance(data, str) else json.dumps(data)),
        parsed=data,
        stats=LlmPredictionStats(stop_reason="failed"),
        model_info=LlmInfo(
            model_key="model-id",
            path="model/path",
            format="gguf",
            display_name="Some LLM",
            size_bytes=0,
            vision=False,
            trained_for_tool_use=False,
            max_context_length=32,
        ),
        _load_config={},
        _prediction_config={},
    )


EXPECTED_PREDICTION_RESPONSE_HISTORY = {
    "messages": [
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Unstructured prediction"}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Avoid consecutive responses."}],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": '{"structured": "prediction"}'}],
        },
    ]
}


def test_add_prediction_results() -> None:
    chat = Chat()
    chat.add_assistant_response(_make_prediction_result("Unstructured prediction"))
    chat.add_user_message("Avoid consecutive responses.")
    chat.add_assistant_response(_make_prediction_result({"structured": "prediction"}))
    # Note: file handles are not yet supported in prediction responses
    assert chat._get_history_for_prediction() == EXPECTED_PREDICTION_RESPONSE_HISTORY


EXPECTED_LOCAL_FILE_MESSAGES = [
    {
        "content": [
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "raw-binary.txt",
                "sizeBytes": -1,
                "type": "file",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "raw-binary.txt",
                "sizeBytes": -1,
                "type": "file",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "lemmy.png",
                "sizeBytes": -1,
                "type": "file",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "also-lemmy.png",
                "sizeBytes": -1,
                "type": "file",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "lemmy.png",
                "sizeBytes": -1,
                "type": "file",
            },
        ],
        "role": "user",
    },
]


EXPECTED_FILE_HANDLE_MESSAGES: list[DictObject] = [
    {
        "content": [
            {
                "fileType": "text/plain",
                "identifier": "file-1",
                "name": "raw-binary.txt",
                "sizeBytes": 20,
                "type": "file",
            },
            {
                "fileType": "text/plain",
                "identifier": "file-1",
                "name": "raw-binary.txt",
                "sizeBytes": 20,
                "type": "file",
            },
            {
                "fileType": "image",
                "identifier": "file-2",
                "name": "lemmy.png",
                "sizeBytes": 41812,
                "type": "file",
            },
            {
                "fileType": "image",
                "identifier": "file-3",
                "name": "also-lemmy.png",
                "sizeBytes": 41812,
                "type": "file",
            },
            {
                "fileType": "image",
                "identifier": "file-2",
                "name": "lemmy.png",
                "sizeBytes": 41812,
                "type": "file",
            },
        ],
        "role": "user",
    },
]


def _add_file(file_data: _LocalFileData, identifier: str) -> _FileHandle:
    name = file_data.name
    fetch_param = file_data._as_fetch_param()
    return _FileHandle(
        name=name,
        identifier=identifier,
        size_bytes=len(fetch_param.content_base64),
        file_type="image" if name.endswith(".png") else "text/plain",
    )


def _check_pending_file(file_handle_dict: DictObject, name: str) -> None:
    assert file_handle_dict["type"] == "file"
    assert file_handle_dict["name"] == name
    assert file_handle_dict["identifier"] == "<file addition pending>"
    assert file_handle_dict["sizeBytes"] == -1
    assert file_handle_dict["fileType"] == "unknown"


def _check_fetched_text_file(
    file_handle_dict: DictObject, name: str, identifier: str
) -> None:
    assert file_handle_dict["type"] == "file"
    assert file_handle_dict["name"] == name
    assert file_handle_dict["identifier"] == identifier
    assert file_handle_dict["sizeBytes"] > 0
    assert file_handle_dict["fileType"] == "text/plain"


def _make_local_file_context() -> tuple[Chat, int]:
    # File context for fetching handles that ensures
    # * duplicate files are only looked up once
    # * files with different names are looked up under both names
    chat = Chat()
    num_unique_files = 3
    chat._add_file(b"raw binary data", "raw-binary.txt")
    chat._add_file(b"raw binary data", "raw-binary.txt")
    chat._add_file(IMAGE_FILEPATH)
    chat._add_file(IMAGE_FILEPATH, "also-lemmy.png")
    chat._add_file(IMAGE_FILEPATH)
    with pytest.raises(RuntimeError, match="Pending file handles must be fetched"):
        chat._get_history_for_prediction()
    history = chat._get_history_unchecked()
    assert history["messages"] == EXPECTED_LOCAL_FILE_MESSAGES
    return chat, num_unique_files


# TODO: Improve code sharing between this test case and its async counterpart
#       (potentially by moving the async version to `async/test_history_async.py`)
def test_implicit_file_handles() -> None:
    local_files: list[_LocalFileData] = []
    file_handles: list[_FileHandle] = []

    def add_file(file_data: _LocalFileData) -> _FileHandle:
        local_files.append(file_data)
        result = _add_file(file_data, f"file-{len(local_files)}")
        file_handles.append(result)
        return result

    context, num_unique_files = _make_local_file_context()
    context._fetch_file_handles(add_file)
    assert len(local_files) == num_unique_files
    assert len(file_handles) == num_unique_files
    messages = context._get_history_for_prediction()["messages"]
    assert messages == EXPECTED_FILE_HANDLE_MESSAGES
    expected_num_message_parts = len(messages[0]["content"])
    # Adding the same file again should immediately populate the handle
    expected_num_message_parts += 1
    context._add_file(IMAGE_FILEPATH)
    messages = context._get_history_for_prediction()["messages"]
    assert len(messages) == 1
    assert len(messages[0]["content"]) == expected_num_message_parts
    assert messages[0]["content"][-1] == messages[0]["content"][-2]
    # Fetching again should not perform any lookups
    context._fetch_file_handles(add_file)
    assert len(local_files) == num_unique_files
    assert len(file_handles) == num_unique_files
    # Adding a different file should require a new lookup
    expected_num_message_parts += 1
    context._add_file(__file__)
    with pytest.raises(RuntimeError, match="Pending file handles must be fetched"):
        context._get_history_for_prediction()
    messages = context._get_history_unchecked()["messages"]
    assert len(messages) == 1
    assert len(messages[0]["content"]) == expected_num_message_parts
    expected_name = f"{__name__.rpartition('.')[2]}.py"
    added_file_handle = messages[-1]["content"][-1]
    _check_pending_file(added_file_handle, expected_name)
    context._fetch_file_handles(add_file)
    messages = context._get_history_for_prediction()["messages"]
    assert len(local_files) == num_unique_files + 1
    assert len(file_handles) == num_unique_files + 1
    # While the pending file handle should be updated in place,
    # retrieving the history takes a snapshot of the internal state
    added_file_handle = messages[-1]["content"][-1]
    expected_identifier = f"file-{num_unique_files + 1}"
    _check_fetched_text_file(added_file_handle, expected_name, expected_identifier)


@pytest.mark.asyncio
async def test_implicit_file_handles_async() -> None:
    local_files: list[_LocalFileData] = []
    file_handles: list[_FileHandle] = []

    async def add_file(file_data: _LocalFileData) -> _FileHandle:
        local_files.append(file_data)
        result = _add_file(file_data, f"file-{len(local_files)}")
        file_handles.append(result)
        return result

    context, num_unique_files = _make_local_file_context()
    await context._fetch_file_handles_async(add_file)
    assert len(local_files) == num_unique_files
    assert len(file_handles) == num_unique_files
    messages = context._get_history_for_prediction()["messages"]
    assert messages == EXPECTED_FILE_HANDLE_MESSAGES
    expected_num_message_parts = len(messages[0]["content"])
    # Adding the same file again should immediately populate the handle
    expected_num_message_parts += 1
    context._add_file(IMAGE_FILEPATH)
    messages = context._get_history_for_prediction()["messages"]
    assert len(messages) == 1
    assert len(messages[0]["content"]) == expected_num_message_parts
    assert messages[0]["content"][-1] == messages[0]["content"][-2]
    # Fetching again should not perform any lookups
    await context._fetch_file_handles_async(add_file)
    assert len(local_files) == num_unique_files
    assert len(file_handles) == num_unique_files
    # Adding a different file should require a new lookup
    expected_num_message_parts += 1
    context._add_file(__file__)
    with pytest.raises(RuntimeError, match="Pending file handles must be fetched"):
        context._get_history_for_prediction()
    messages = context._get_history_unchecked()["messages"]
    assert len(messages) == 1
    assert len(messages[0]["content"]) == expected_num_message_parts
    expected_name = f"{__name__.rpartition('.')[2]}.py"
    added_file_handle = messages[-1]["content"][-1]
    _check_pending_file(added_file_handle, expected_name)
    await context._fetch_file_handles_async(add_file)
    messages = context._get_history_for_prediction()["messages"]
    assert len(local_files) == num_unique_files + 1
    assert len(file_handles) == num_unique_files + 1
    # While the pending file handle should be updated in place,
    # retrieving the history takes a snapshot of the internal state
    added_file_handle = messages[-1]["content"][-1]
    expected_identifier = f"file-{num_unique_files + 1}"
    _check_fetched_text_file(added_file_handle, expected_name, expected_identifier)


EXPECTED_PENDING_ATTACHMENT_MESSAGES = [
    {
        "content": [
            {
                "text": "What do you make of this?",
                "type": "text",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "lemmy.png",
                "sizeBytes": -1,
                "type": "file",
            },
            {
                "fileType": "unknown",
                "identifier": "<file addition pending>",
                "name": "test_history.py",
                "sizeBytes": -1,
                "type": "file",
            },
        ],
        "role": "user",
    },
]


def test_user_message_attachments() -> None:
    chat = Chat()
    chat.add_user_message(
        "What do you make of this?", _images=[IMAGE_FILEPATH], _files=[__file__]
    )
    history = chat._get_history_unchecked()
    assert history["messages"] == EXPECTED_PENDING_ATTACHMENT_MESSAGES


def test_assistant_responses_cannot_be_multipart_or_consecutive() -> None:
    chat = Chat()
    chat.add_assistant_response("First response")
    with pytest.raises(RuntimeError, match="Multi-part or consecutive"):
        chat.add_assistant_response("Consecutive response")
    chat.add_user_message("Separator")
    with pytest.raises(ValueError, match="Unable to parse"):
        # MyPy picks up that this is not allowed, but we want to test it anyway
        chat.add_assistant_response(("Multi-part", "response"))  # type: ignore[arg-type]
    chat.add_assistant_response("Second response")


def test_system_prompts_cannot_be_multipart_or_consecutive() -> None:
    chat = Chat("First prompt")
    with pytest.raises(RuntimeError, match="Multi-part or consecutive"):
        chat.add_system_prompt("Consecutive prompt")
    chat.add_user_message("Separator")
    with pytest.raises(ValueError, match="Unable to parse"):
        # MyPy picks up that this is not allowed, but we want to test it anyway
        chat.add_system_prompt(("Multi-part", "prompt"))  # type: ignore[arg-type]
    chat.add_system_prompt("Second prompt")


def test_system_prompts_cannot_be_file_handles() -> None:
    chat = Chat()
    with pytest.raises(ValueError, match="Unable to parse system prompt"):
        # MyPy picks up that this is not allowed, but we want to test it anyway
        chat.add_system_prompt(INPUT_FILE_HANDLE)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unable to parse system prompt"):
        chat.add_entry("system", INPUT_FILE_HANDLE)
    with pytest.raises(ValueError, match="Unable to parse system prompt"):
        # MyPy picks up that this is not allowed, but we want to test it anyway
        chat.add_system_prompt(INPUT_FILE_HANDLE_DICT)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unable to parse system prompt"):
        chat.add_entry("system", INPUT_FILE_HANDLE_DICT)


def test_initial_history_with_prompt_is_disallowed() -> None:
    chat = Chat()
    with pytest.raises(ValueError, match="initial history or a system prompt"):
        Chat("Initial prompt", _initial_history=chat._history)


def test_invalid_local_file() -> None:
    chat = Chat()
    with pytest.raises(LMStudioOSError) as exc_info:
        chat._add_file("No such file")
    check_sdk_error(exc_info, __file__)


EXPECTED_CHAT_STR = """\
Chat.from_history({
  "messages": [
    {
      "content": [
        {
          "text": "Initial system prompt",
          "type": "text"
        }
      ],
      "role": "system"
    },
    {
      "content": [
        {
          "text": "Simple text message",
          "type": "text"
        }
      ],
      "role": "user"
    }
  ]
})\
"""


def test_chat_display() -> None:
    chat = Chat("Initial system prompt")
    chat.add_user_message("Simple text message")
    # Chats use the standard identity based repr
    assert repr(chat) == object.__repr__(chat)
    # But print the history
    print(chat)
    assert str(chat) == EXPECTED_CHAT_STR


CLONING_MECHANISMS: list[Callable[[Chat], Chat]] = [
    Chat.from_history,
    Chat.copy,
    copy.copy,
    copy.deepcopy,
]


@pytest.mark.parametrize("clone", CLONING_MECHANISMS)
def test_chat_duplication(clone: Callable[[Chat], Chat]) -> None:
    chat = Chat("Initial system prompt")
    chat.add_user_message("Simple text message")
    cloned_chat = clone(chat)
    assert cloned_chat is not chat
    for attr, source_value in chat.__dict__.items():
        assert getattr(cloned_chat, attr) is not source_value
    chat_messages = chat._history.messages
    cloned_messages = cloned_chat._history.messages
    for source_message, cloned_message in zip(chat_messages, cloned_messages):
        assert cloned_message is not source_message
        assert cloned_message == source_message


@pytest.mark.parametrize("clone", CLONING_MECHANISMS)
def test_cannot_clone_with_pending_files(clone: Callable[[Chat], Chat]) -> None:
    chat = Chat("Initial system prompt")
    chat._add_file(__file__)
    with pytest.raises(LMStudioRuntimeError, match="Cannot copy chat history"):
        clone(chat)
