"""LLM chat history management."""

import os
import uuid

from base64 import b64encode
from collections.abc import Mapping
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import (
    Awaitable,
    BinaryIO,
    Callable,
    Iterable,
    MutableSequence,
    Protocol,
    Self,
    Sequence,
    Tuple,
    TypeAlias,
    cast,
    get_args as get_typeform_args,
    runtime_checkable,
)

from msgspec import to_builtins
from typing_extensions import TypeIs

from .sdk_api import (
    LMStudioOSError,
    LMStudioRuntimeError,
    LMStudioValueError,
    sdk_public_api,
)
from .schemas import DictObject, LMStudioStruct, _format_json
from ._sdk_models import (
    ChatHistoryData,
    ChatHistoryDataDict,
    ChatMessageData as AnyChatMessage,
    ChatMessageDataDict as AnyChatMessageDict,
    ChatMessageDataUser as UserMessage,
    ChatMessageDataSystem as SystemPrompt,
    ChatMessageDataAssistant as AssistantResponse,
    ChatMessageDataTool as ToolResultMessage,
    # Private until LM Studio file handle support stabilizes
    ChatMessagePartFileData as _FileHandle,
    ChatMessagePartFileDataDict as _FileHandleDict,
    ChatMessagePartTextData as TextData,
    ChatMessagePartTextDataDict as TextDataDict,
    ChatMessagePartToolCallRequestData as ToolCallRequestData,
    ChatMessagePartToolCallRequestDataDict as ToolCallRequestDataDict,
    ChatMessagePartToolCallResultData as ToolCallResultData,
    ChatMessagePartToolCallResultDataDict as ToolCallResultDataDict,
    # Private until LM Studio file handle support stabilizes
    # FileType,
    FilesRpcUploadFileBase64Parameter,
    ToolCallRequest as ToolCallRequest,
    FunctionToolCallRequestDict as ToolCallRequestDict,
)

__all__ = [
    "AssistantResponseContent",
    "Chat",
    "ChatHistoryData",
    "ChatHistoryDataDict",
    "AnyChatMessage",
    "AnyChatMessageDict",
    "UserMessage",
    "SystemPrompt",
    "AssistantResponse",
    "ToolResultMessage",
    # Private until LM Studio file handle support stabilizes
    "_FileHandle",  # Other modules need this to be exported
    "_FileHandleDict",  # Other modules need this to be exported
    # "FileType",
    # "FileHandle",
    # "FileHandleDict",
    # "FetchFileHandle",
    "SystemPromptContent",
    "TextData",
    "TextDataDict",
    # Private until user level tool call request management is defined
    "ToolCallRequest",
    "ToolCallResultData",
    # "ToolCallRequest",
    # "ToolCallResult",
    "UserMessageContent",
]

# Private until LM Studio file handle support stabilizes
_FileInputType = BinaryIO | bytes | str | os.PathLike[str]

# A note on terminology:
#
# In the chat history API, "prompt" specifically refers to "system prompts",
# which are used to issue behavioral directives to the LLM assistant.
#
# In other parts of the SDK, "prompt" is used in other ways:
#
# * when requesting text completion, the starting text parameter is referred
#   to as the "completion prompt"
# * when applying prompt templates, the entire resulting chat context history
#   is referred to as the "chat prompt"

# Note: ChatMessageDataSystem nominally allows file handles in its content field,
#       but that's only for internal use within the LM Studio plugin system
SystemPromptContent = TextData
SystemPromptContentDict = TextDataDict
UserMessageContent = TextData | _FileHandle
UserMessageContentDict = TextDataDict | _FileHandleDict
AssistantResponseContent = TextData | _FileHandle
AssistantResponseContentDict = TextDataDict | _FileHandleDict
ChatMessageContent = TextData | _FileHandle | ToolCallRequestData | ToolCallResultData
ChatMessageContentDict = (
    TextDataDict | _FileHandleDict | ToolCallRequestData | ToolCallResultDataDict
)


@runtime_checkable
class _ServerAssistantResponse(Protocol):
    """Convert assistant responses from server to history message content."""

    def _to_history_content(self) -> str:
        """Return the history message content for this response."""
        ...


SystemPromptInput = str | SystemPromptContent | SystemPromptContentDict
UserMessageInput = str | UserMessageContent | UserMessageContentDict
UserMessageMultiPartInput = Iterable[UserMessageInput]
AnyUserMessageInput = UserMessageInput | UserMessageMultiPartInput
AssistantResponseInput = str | AssistantResponseContent | AssistantResponseContentDict
AnyAssistantResponseInput = AssistantResponseInput | _ServerAssistantResponse
ToolCallRequestInput = (
    ToolCallRequest
    | ToolCallRequestDict
    | ToolCallRequestData
    | ToolCallRequestDataDict
)
ToolCallResultInput = ToolCallResultData | ToolCallResultDataDict
ChatMessageInput = str | ChatMessageContent | ChatMessageContentDict
ChatMessageMultiPartInput = UserMessageMultiPartInput
AnyChatMessageInput = ChatMessageInput | ChatMessageMultiPartInput


def _is_user_message_input(value: AnyUserMessageInput) -> TypeIs[UserMessageInput]:
    return isinstance(value, (str, Mapping)) or not isinstance(value, Iterable)


def _is_chat_message_input(value: AnyChatMessageInput) -> TypeIs[ChatMessageInput]:
    return isinstance(value, (str, Mapping)) or not isinstance(value, Iterable)


def _get_file_details(src: _FileInputType) -> Tuple[str, bytes]:
    """Read file contents as binary data and generate a suitable default name."""
    if isinstance(src, bytes):
        # We interpreter bytes as raw data, not a bytes filesystem path
        data = src
        name = str(uuid.uuid4())
    elif hasattr(src, "read"):
        try:
            data = src.read()
        except OSError as exc:
            err_msg = f"Error while reading {src!r} ({exc!r})"
            raise LMStudioOSError(err_msg) from None
        name = getattr(src, "name", str(uuid.uuid4()))
    else:
        try:
            src_path = Path(src)
        except Exception as exc:
            err_msg = f"Expected file-like object, filesystem path, or bytes ({exc!r})"
            raise LMStudioValueError(err_msg) from None
        try:
            data = src_path.read_bytes()
        except OSError as exc:
            err_msg = f"Error while reading {str(src_path)!r} ({exc!r})"
            raise LMStudioOSError(err_msg) from None
        name = str(src_path.name)
    return name, data


_ContentHash: TypeAlias = bytes
_FileHandleCacheKey: TypeAlias = tuple[str, _ContentHash]


# Private until LM Studio file handle support stabilizes
class _LocalFileData:
    """Local file data to be added to a chat session."""

    name: str
    raw_data: bytes

    def __init__(self, src: _FileInputType, name: str | None = None) -> None:
        default_name, raw_data = _get_file_details(src)
        self.name = name or default_name
        self.raw_data = raw_data

    def _get_cache_key(self) -> _FileHandleCacheKey:
        return (self.name, sha256(self.raw_data).digest())

    def _as_fetch_param(self) -> FilesRpcUploadFileBase64Parameter:
        content_base64 = b64encode(self.raw_data).decode("ascii")
        return FilesRpcUploadFileBase64Parameter(
            name=self.name, content_base64=content_base64
        )


_PendingFile: TypeAlias = tuple[_LocalFileData, _FileHandle]

_FetchFileHandle: TypeAlias = Callable[[_LocalFileData], _FileHandle]
_AsyncFetchFileHandle: TypeAlias = Callable[[_LocalFileData], Awaitable[_FileHandle]]


class Chat:
    """Helper class to track LLM interactions."""

    # TODO: Provide tools to help manage the amount of context retained
    #       (that may not be feasible at this level, since doing it right
    #       requires calculating token counts for the serialised history)
    def __init__(
        self,
        initial_prompt: SystemPromptInput | None = None,
        *,
        # Public API is to call `from_history` rather than supplying this directly
        _initial_history: ChatHistoryData | None = None,
    ):
        """Initialize LLM interaction history tracking."""
        if _initial_history is not None:
            if initial_prompt is not None:
                raise LMStudioValueError(
                    "Chat context accepts an initial history or a system prompt, not both"
                )
            self._history = _initial_history
        else:
            self._history = ChatHistoryData(messages=[])
        self._pending_files: dict[_FileHandleCacheKey, _PendingFile] = {}
        self._cached_file_handles: dict[_FileHandleCacheKey, _FileHandle] = {}
        if initial_prompt is not None:
            self.add_system_prompt(initial_prompt)

    @property
    def _messages(self) -> MutableSequence[AnyChatMessage]:
        return cast(MutableSequence[AnyChatMessage], self._history.messages)

    def __str__(self) -> str:
        type_name = type(self).__name__
        formatted_data = _format_json(self._get_history_unchecked())
        return f"{type_name}.from_history({formatted_data})"

    def _get_history_unchecked(self) -> ChatHistoryDataDict:
        # Convert the history without checking for pending files
        return cast(ChatHistoryDataDict, to_builtins(self._history))

    def _get_history_for_prediction(self) -> ChatHistoryDataDict:
        """Convert the current history to a format suitable for an LLM prediction."""
        if self._pending_files:
            # If this happens, something elsewhere in the SDK messed up
            # Raise a standard exception so the traceback doesn't get truncated
            raise RuntimeError(
                "Pending file handles must be fetched before requesting an LLM prediction"
            )
        return self._get_history_unchecked()

    def _get_history_for_copy(self) -> ChatHistoryData:
        """Convert the current history to a format suitable for initializing a new instance."""
        if self._pending_files:
            # Users can trigger this without the SDK doing anything wrong,
            # so truncate the reported traceback at the SDK boundary
            raise LMStudioRuntimeError(
                "Cannot copy chat history with pending file handles"
            )
        return ChatHistoryData._from_api_dict(self._get_history_unchecked())

    def _get_pending_files_to_fetch(self) -> Mapping[_FileHandleCacheKey, _PendingFile]:
        pending_files = self._pending_files
        self._pending_files = {}
        return pending_files

    @staticmethod
    def _update_pending_handle(
        pending_handle: _FileHandle, fetched_handle: _FileHandle
    ) -> None:
        # Mutate the pending handle so it keeps its place in the history
        for attr in pending_handle.__struct_fields__:
            setattr(pending_handle, attr, getattr(fetched_handle, attr))

    def _fetch_file_handles(self, fetch_file_handle: _FetchFileHandle) -> None:
        """Synchronously fetch all currently pending file handles from the LM Studio API."""
        pending_files = self._get_pending_files_to_fetch()
        for cache_key, (file_data, pending_handle) in pending_files.items():
            fetched_handle = fetch_file_handle(file_data)
            self._update_pending_handle(pending_handle, fetched_handle)
            self._cached_file_handles[cache_key] = fetched_handle

    async def _fetch_file_handles_async(
        self, fetch_file_handle: _AsyncFetchFileHandle
    ) -> None:
        """Asynchronously fetch all currently pending file handles from the LM Studio API."""
        pending_files = self._get_pending_files_to_fetch()
        for cache_key, (file_data, pending_handle) in pending_files.items():
            fetched_handle = await fetch_file_handle(file_data)
            self._update_pending_handle(pending_handle, fetched_handle)
            self._cached_file_handles[cache_key] = fetched_handle

    @classmethod
    @sdk_public_api()
    def from_history(
        cls, history: str | Self | ChatHistoryData | ChatHistoryDataDict
    ) -> Self:
        """Create a new chat context from the given chat history data.

        * Single string -> a single user message with that text
        * ChatHistoryData -> msgspec struct for the chat history wire format
        * Dictionary -> expected to match the chat history wire format,
          except that simple strings are accepted as text content fields
        """
        if isinstance(history, cls):
            # Create a new `cls` instance with the same history as the given chat
            self = cls(_initial_history=history._get_history_for_copy())
            # Retrieving the history would fail if there were pending file handles
            self._cached_file_handles.update(history._cached_file_handles)
            return self
        if isinstance(history, ChatHistoryData):
            # Ensure the chat is not affected by future mutation of the given history
            return cls(_initial_history=deepcopy(history))
        self = cls()
        if isinstance(history, str):
            self.add_user_message(history)
        else:
            messages = history.get("messages") if isinstance(history, Mapping) else None
            if messages is None:
                self_name = type(cls).__name__
                data_struct_name = ChatHistoryData.__name__
                raise LMStudioValueError(
                    f"Expected {self_name}, {data_struct_name}, or a dict with a 'messages' key"
                )
            self._add_entries(messages)
        return self

    @sdk_public_api()
    def copy(self) -> Self:
        """Make a copy of this chat (future updates to either chat will not affect the other)."""
        # Use the Chat -> dict -> Chat transformation to avoid sharing mutable state
        # This is effectively a deep copy, but shallow chat copies are a recipe for problems
        return type(self).from_history(self)

    __copy__ = copy

    @sdk_public_api()
    def __deepcopy__(self, _memo: object) -> Self:
        # The default copy operation is already a sufficiently deep copy of the instance
        return self.copy()

    @sdk_public_api()
    def add_entry(self, role: str, content: AnyChatMessageInput) -> AnyChatMessage:
        """Add a new history entry for the given role name (user/system/assistant/tool)."""
        # This method handles data driven input, so rather than defining overloads,
        # it just downcasts and relies on the structural checks in each method
        # User messages accept multi-part content, so just forward it to that method
        if role == "user":
            messages = cast(AnyUserMessageInput, content)
            return self.add_user_message(messages)
        # Assistant responses consist of a text response with zero or more tool requests
        if role == "assistant":
            if _is_chat_message_input(content):
                response = cast(AssistantResponseInput, content)
                return self.add_assistant_response(response)
            try:
                (response_content, *tool_request_contents) = content
            except ValueError:
                raise LMStudioValueError(
                    f"Unable to parse assistant response content: {content}"
                ) from None
            response = cast(AssistantResponseInput, response_content)
            tool_requests = cast(Iterable[ToolCallRequest], tool_request_contents)
            return self.add_assistant_response(response, tool_requests)

        # Other roles do not accept multi-part messages, so ensure there
        # is exactly one content item given. We still accept iterables because
        # that's how the wire format is defined and we want to accept that.
        content_item: ChatMessageInput
        result: AnyChatMessage | None
        if _is_chat_message_input(content):
            content_item = content
        else:
            try:
                (content_item,) = content
            except ValueError:
                err_msg = f"{role!r} role does not support multi-part message content."
                raise LMStudioValueError(err_msg) from None
        match role:
            case "system":
                prompt = cast(SystemPromptInput, content_item)
                result = self.add_system_prompt(prompt)
            case "tool":
                tool_result = cast(ToolCallResultInput, content_item)
                result = self.add_tool_result(tool_result)
            case _:
                raise LMStudioValueError(f"Unknown history role: {role}")
        return result

    @sdk_public_api()
    def append(self, message: AnyChatMessage | AnyChatMessageDict) -> AnyChatMessage:
        """Append a copy of an already formatted message to the chat history."""
        if isinstance(message, dict):
            return self.add_entry(**message)
        elif not isinstance(message, get_typeform_args(AnyChatMessage)):
            raise LMStudioValueError(f"{message!r} is not a valid chat entry")
        return self.add_entry(**message.to_dict())

    def _add_entries(
        self,
        entries: Iterable[
            AnyChatMessage | DictObject | tuple[str, AnyChatMessageInput]
        ],
    ) -> Sequence[AnyChatMessage]:
        """Add history entries for the given (role, content) pairs."""
        result: list[AnyChatMessage] = []
        for entry_data in entries:
            role: str
            content: AnyChatMessageInput
            match entry_data:
                case LMStudioStruct(role=role, content=raw_content):
                    # MyPy gets confused here, as the fields on the specific
                    # structs produce iterables with narrower union types
                    # than the fully general union that `add_entry` accepts
                    # (This still happens even after the structs were changed
                    # to report array fields as sequences rather than as lists)
                    content = cast(AnyChatMessageInput, raw_content)
                case {"role": role, "content": content}:
                    pass
                case (str() as role, content):
                    pass
                case _:
                    raise LMStudioValueError(
                        f"Could not parse history entry: {entry_data}"
                    )
            entry = self.add_entry(role, content)
            if entry is not None:
                result.append(entry)
        return result

    def _get_last_message(self, role: str) -> AnyChatMessage | None:
        """Return the most recent message, but only if it has the given role."""
        messages = self._history.messages
        if not messages:
            return None
        last_message = messages[-1]
        if role != last_message.role:
            return None
        return last_message

    def _raise_if_consecutive(self, role: str, description: str) -> None:
        if self._get_last_message(role) is not None:
            # The wording here reflects the fact that if multi-part responses
            # *were* permitted, we could implicitly merge the two messages
            raise LMStudioRuntimeError(
                f"Multi-part or consecutive {description} are not supported."
            )

    @sdk_public_api()
    def add_system_prompt(self, prompt: SystemPromptInput) -> SystemPrompt:
        """Add a new system prompt to the chat history."""
        self._raise_if_consecutive(SystemPrompt.role, "system prompts")
        message_data: SystemPromptContent
        match prompt:
            # Sadly, we can't use the union type aliases for matching,
            # since the compiler needs visibility into every match target
            case TextData():
                message_data = prompt
            case str():
                message_data = TextData(text=prompt)
            case {"text": text}:
                message_data = TextData(text=text)
            case _:
                raise LMStudioValueError(f"Unable to parse system prompt: {prompt}")
        message = SystemPrompt(content=[message_data])
        self._messages.append(message)
        return message

    def _get_file_handle(
        self, src: _FileInputType, name: str | None = None
    ) -> _FileHandle:
        file_data = _LocalFileData(src, name)
        cache_key = file_data._get_cache_key()
        try:
            # Check if file handle has already been fetched
            return self._cached_file_handles[cache_key]
        except KeyError:
            pass
        try:
            # Check if file handle already has a fetch pending
            pending_file = self._pending_files[cache_key]
            return pending_file[1]
        except KeyError:
            pass
        # Create a new pending file handle
        to_be_populated = _FileHandle(
            name=file_data.name,
            identifier="<file addition pending>",
            size_bytes=-1,  # Let the fetch operation set this later
            file_type="unknown",
        )
        self._pending_files[cache_key] = (file_data, to_be_populated)
        return to_be_populated

    @sdk_public_api()
    def _add_file(self, src: _FileInputType, name: str | None = None) -> UserMessage:
        """Add a local file (or raw binary data) to the chat history."""
        # Private until LM Studio file handle support stabilizes
        file_handle = self._get_file_handle(src, name)
        return self.add_user_message(file_handle)

    @sdk_public_api()
    def add_user_message(
        self,
        content: UserMessageInput | Iterable[UserMessageInput],
        *,
        # Mark file parameters as private until LM Studio
        # file handle support stabilizes
        _images: Sequence[_FileInputType] = (),
        _files: Sequence[_FileInputType] = (),
    ) -> UserMessage:
        """Add a new user message to the chat history."""
        # Accept both singular and multi-part user messages
        content_items: list[UserMessageInput]
        if _is_user_message_input(content):
            content_items = [content]
        else:
            content_items = list(content)
        # Convert given local file information to file handles
        if _images:
            content_items.extend(self._get_file_handle(f) for f in _images)
        if _files:
            content_items.extend(self._get_file_handle(f) for f in _files)
        # Consecutive messages with the same role are not supported,
        # but multi-part user messages are valid (to allow for file
        # attachments), so just merge them
        last_message = self._get_last_message(UserMessage.role)
        if last_message is not None:
            message = cast(UserMessage, last_message)
        else:
            message = UserMessage(content=[])
        _content = cast(MutableSequence[UserMessageContent], message.content)
        for item in content_items:
            match item:
                # Sadly, we can't use the union type aliases for matching,
                # since the compiler needs visibility into every match target
                case TextData() | _FileHandle():
                    _content.append(item)
                case str():
                    _content.append(TextData(text=item))
                case {"text": str() as text}:
                    _content.append(TextData(text=text))
                case {"name": str(), "identifier": str(), "fileType": _} | {
                    "name": str(),
                    "identifier": str(),
                    "file_type": _,
                }:
                    # We accept snake_case here for consistency, but don't really expect it
                    _content.append(_FileHandle._from_any_dict(item))
                case _:
                    raise LMStudioValueError(
                        f"Unable to parse user message content: {item}"
                    )
        if not _content:
            raise LMStudioValueError("Empty user messages are not supported.")
        if message is not last_message:
            self._messages.append(message)
        return message

    @classmethod
    def _parse_assistant_response(
        cls, response: AnyAssistantResponseInput
    ) -> TextData | _FileHandle:
        # Note: tool call requests are NOT accepted here, as they're expected
        # to follow an initial text response
        # It's not clear if file handles should be accepted as it's not obvious
        # how client applications should process those (even though the API
        # format nominally permits them here)
        match response:
            case TextData() | _FileHandle():
                return response
            case str():
                return TextData(text=response)
            case _ServerAssistantResponse():
                return TextData(text=response._to_history_content())
            case {"text": str() as text}:
                return TextData(text=text)
            case {"name": str(), "identifier": str(), "fileType": _} | {
                "name": str(),
                "identifier": str(),
                "file_type": _,
            }:
                # We accept snake_case here for consistency, but don't really expect it
                return _FileHandle._from_any_dict(response)
            case _:
                raise LMStudioValueError(
                    f"Unable to parse assistant response content: {response}"
                )

    @classmethod
    def _parse_tool_call_request(
        cls, request: ToolCallRequestInput
    ) -> ToolCallRequestData:
        match request:
            case ToolCallRequestData():
                return request
            case ToolCallRequest():
                return ToolCallRequestData(tool_call_request=request)
            case {"type": "toolCallRequest"}:
                return ToolCallRequestData._from_any_dict(request)
            case {"toolCallRequest": [*_]} | {"tool_call_request": [*_]}:
                request_details = ToolCallRequest._from_any_dict(request)
                return ToolCallRequestData(tool_call_request=request_details)
            case _:
                raise LMStudioValueError(
                    f"Unable to parse tool call request content: {request}"
                )

    @sdk_public_api()
    def add_assistant_response(
        self,
        response: AnyAssistantResponseInput,
        tool_call_requests: Iterable[ToolCallRequestInput] = (),
    ) -> AssistantResponse:
        """Add a new 'assistant' response to the chat history."""
        self._raise_if_consecutive(AssistantResponse.role, "assistant responses")
        message_text = self._parse_assistant_response(response)
        request_parts = [
            self._parse_tool_call_request(req) for req in tool_call_requests
        ]
        message = AssistantResponse(content=[message_text, *request_parts])
        self._messages.append(message)
        return message

    @classmethod
    def _parse_tool_result(cls, result: ToolCallResultInput) -> ToolCallResultData:
        match result:
            case ToolCallResultData():
                return result
            case {"toolCallId": _, "content": _} | {"tool_call_id": _, "content": _}:
                # We accept snake_case here for consistency, but don't really expect it
                return ToolCallResultData.from_dict(result)
            case _:
                raise LMStudioValueError(f"Unable to parse tool result: {result}")

    def add_tool_results(
        self, results: Iterable[ToolCallResultInput]
    ) -> ToolResultMessage:
        """Add multiple tool results to the chat history as a single message."""
        message_content = [self._parse_tool_result(result) for result in results]
        message = ToolResultMessage(content=message_content)
        self._messages.append(message)
        return message

    def add_tool_result(self, result: ToolCallResultInput) -> ToolResultMessage:
        """Add a new tool result to the chat history."""
        # Consecutive tool result messages are allowed,
        # so skip checking if the last message was a tool result
        # (use add_tool_results if a multi-part message is desired)
        message_data = self._parse_tool_result(result)
        message = ToolResultMessage(content=[message_data])
        self._messages.append(message)
        return message
