"""Sans I/O protocol implementation for the LM Studio remote access API."""

# TODO: Migrate additional protocol details from the [a]sync APIs to the sans I/O API
import copy
import json
import uuid

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    NoReturn,
    Self,
    Sequence,
    Type,
    TypeAlias,
    TypedDict,
    TypeVar,
    assert_never,
    cast,
    get_type_hints,
)


from msgspec import Struct, convert, defstruct, to_builtins

from .sdk_api import (
    LMStudioError,
    LMStudioRuntimeError,
    LMStudioValueError,
    sdk_callback_invocation,
    sdk_public_api,
    sdk_public_type,
    _truncate_traceback,
)
from .history import AssistantResponse, Chat, ToolCallRequest, ToolCallResultData
from .schemas import (
    AnyLMStudioStruct,
    DictObject,
    DictSchema,
    LMStudioStruct,
    ModelSchema,
    TWireFormat,
    _format_json,
    _snake_case_keys_to_camelCase,
    _to_json_schema,
)
from ._kv_config import (
    TLoadConfig,
    TLoadConfigDict,
    dict_from_fields_key,
    load_config_to_kv_config_stack,
    prediction_config_to_kv_config_stack,
)
from ._sdk_models import (
    DownloadProgressUpdate,
    EmbeddingChannelLoadModelCreationParameter,
    EmbeddingChannelLoadModelCreationParameterDict,
    EmbeddingChannelGetOrLoadCreationParameter,
    EmbeddingChannelGetOrLoadCreationParameterDict,
    EmbeddingLoadModelConfig,
    EmbeddingLoadModelConfigDict,
    EmbeddingModelInfo,
    EmbeddingModelInstanceInfo,
    EmbeddingRpcGetLoadConfigParameter,
    EmbeddingRpcGetModelInfoParameter,
    EmbeddingRpcTokenizeParameter,
    EmbeddingRpcUnloadModelParameter,
    KvConfigStack,
    LlmChannelLoadModelCreationParameter,
    LlmChannelLoadModelCreationParameterDict,
    LlmChannelGetOrLoadCreationParameter,
    LlmChannelGetOrLoadCreationParameterDict,
    LlmChannelPredictCreationParameter as PredictionChannelRequest,
    LlmChannelPredictCreationParameterDict as PredictionChannelRequestDict,
    LlmInfo,
    LlmInstanceInfo,
    LlmLoadModelConfig,
    LlmLoadModelConfigDict,
    LlmPredictionConfig,
    LlmPredictionConfigDict,
    LlmPredictionFragment,
    LlmPredictionStats,
    LlmRpcGetLoadConfigParameter,
    LlmRpcGetModelInfoParameter,
    LlmRpcTokenizeParameter,
    LlmRpcUnloadModelParameter,
    LlmTool,
    LlmToolUseSettingToolArray,
    ModelInfo,
    ModelInstanceInfo,
    ModelSearchOptsDict,
    ModelSpecifier,
    ModelSpecifierDict,
    ModelSpecifierInstanceReference,
    ModelSpecifierQuery,
    ModelQuery,
    ModelQueryDict,
    RepositoryChannelDownloadModelCreationParameter as DownloadModelChannelRequest,
    RepositoryChannelDownloadModelCreationParameterDict as DownloadModelChannelRequestDict,
    SerializedLMSExtendedError,
    ModelCompatibilityType,
    ModelSearchResultDownloadOptionData,
    ModelSearchResultEntryData,
    RepositoryRpcGetModelDownloadOptionsParameter,
    RepositoryRpcSearchModelsParameter,
)
from ._logging import get_logger, LogEventContext, StructuredLogger

# The sync and async modules publish the main SDK client API.
# From here, we publish everything that might be needed
# for API type hints, error handling, defining custom
# structured responses, and other expected activities.
# The "sans I/O" API itself is *not* automatically exported.
# If API consumers want to use that, they need to access it
# explicitly via `lmstudio.json_api`, it isn't exported
# implicitly as part of the top-level `lmstudio` API.
__all__ = [
    "ActResult",
    "AnyModelSpecifier",
    "DownloadFinalizedCallback",
    "DownloadProgressCallback",
    "DownloadProgressUpdate",
    "EmbeddingModelInfo",
    "EmbeddingModelInstanceInfo",
    "EmbeddingLoadModelConfig",
    "EmbeddingLoadModelConfigDict",
    "LlmInfo",
    "LlmInstanceInfo",
    "LlmLoadModelConfig",
    "LlmLoadModelConfigDict",
    "LlmPredictionConfig",
    "LlmPredictionConfigDict",
    "LlmPredictionFragment",
    "LlmPredictionStats",
    "LMStudioCancelledError",
    "LMStudioClientError",
    "LMStudioChannelClosedError",
    "LMStudioModelNotFoundError",
    "LMStudioPredictionError",
    "LMStudioServerError",
    "LMStudioUnknownMessageError",
    "LMStudioWebsocketError",
    "ModelInfo",
    "ModelInstanceInfo",
    "ModelLoadResult",
    "ModelSpecifier",
    "ModelSpecifierDict",
    "ModelQuery",
    "ModelQueryDict",
    "PredictionFirstTokenCallback",
    "PredictionFragmentCallback",
    "PredictionMessageCallback",
    "PredictionResult",
    "PredictionRoundResult",
    "PromptProcessingCallback",
    "SerializedLMSExtendedError",
    "ToolDefinition",
    "ToolFunctionDef",
    "ToolFunctionDefDict",
]


T = TypeVar("T")
TStruct = TypeVar("TStruct", bound=AnyLMStudioStruct)
TPrediction = TypeVar("TPrediction", str, DictObject)

DEFAULT_API_HOST = "localhost:1234"
DEFAULT_TTL = 60 * 60  # By default, leaves idle models loaded for an hour

AnyModelSpecifier: TypeAlias = str | ModelSpecifier | ModelQuery | DictObject

GetOrLoadChannelRequest: TypeAlias = (
    EmbeddingChannelGetOrLoadCreationParameter | LlmChannelGetOrLoadCreationParameter
)
GetOrLoadChannelRequestDict: TypeAlias = (
    EmbeddingChannelGetOrLoadCreationParameterDict
    | LlmChannelGetOrLoadCreationParameterDict
)
LoadModelChannelRequest: TypeAlias = (
    EmbeddingChannelLoadModelCreationParameter | LlmChannelLoadModelCreationParameter
)
LoadModelChannelRequestDict: TypeAlias = (
    EmbeddingChannelLoadModelCreationParameterDict
    | LlmChannelLoadModelCreationParameterDict
)

LoadConfigRequest: TypeAlias = (
    EmbeddingRpcGetLoadConfigParameter | LlmRpcGetLoadConfigParameter
)
ModelInfoRequest: TypeAlias = (
    EmbeddingRpcGetModelInfoParameter | LlmRpcGetModelInfoParameter
)
TokenizeRequest: TypeAlias = EmbeddingRpcTokenizeParameter | LlmRpcTokenizeParameter
UnloadModelRequest: TypeAlias = (
    EmbeddingRpcUnloadModelParameter | LlmRpcUnloadModelParameter
)


class ModelSessionTypes(Generic[TLoadConfig]):
    """Helper class to group related types for code sharing across model namespaces."""

    # Prefer union types for simplicity, but declare as generic when beneficial

    MODEL_INFO: Type[ModelInfo]
    MODEL_INSTANCE_INFO: Type[ModelInstanceInfo]
    MODEL_LOAD_CONFIG: Type[TLoadConfig]
    REQUEST_GET_OR_LOAD: Type[GetOrLoadChannelRequest]
    REQUEST_LOAD_CONFIG: Type[LoadConfigRequest]
    REQUEST_MODEL_INFO: Type[ModelInfoRequest]
    REQUEST_NEW_INSTANCE: Type[LoadModelChannelRequest]
    REQUEST_TOKENIZE: Type[TokenizeRequest]
    REQUEST_UNLOAD: Type[UnloadModelRequest]


class ModelTypesEmbedding(ModelSessionTypes[EmbeddingLoadModelConfig]):
    """Relevant structs for the embedding model namespace."""

    MODEL_INFO = EmbeddingModelInfo
    MODEL_INSTANCE_INFO = EmbeddingModelInstanceInfo
    MODEL_LOAD_CONFIG = EmbeddingLoadModelConfig
    REQUEST_GET_OR_LOAD = EmbeddingChannelGetOrLoadCreationParameter
    REQUEST_LOAD_CONFIG = EmbeddingRpcGetLoadConfigParameter
    REQUEST_MODEL_INFO = EmbeddingRpcGetModelInfoParameter
    REQUEST_NEW_INSTANCE = EmbeddingChannelLoadModelCreationParameter
    REQUEST_TOKENIZE = EmbeddingRpcTokenizeParameter
    REQUEST_UNLOAD = EmbeddingRpcUnloadModelParameter


class ModelTypesLlm(ModelSessionTypes[LlmLoadModelConfig]):
    """Relevant structs for the LLM namespace."""

    MODEL_INFO = LlmInfo
    MODEL_INSTANCE_INFO = LlmInstanceInfo
    MODEL_LOAD_CONFIG = LlmLoadModelConfig
    REQUEST_GET_OR_LOAD = LlmChannelGetOrLoadCreationParameter
    REQUEST_LOAD_CONFIG = LlmRpcGetLoadConfigParameter
    REQUEST_MODEL_INFO = LlmRpcGetModelInfoParameter
    REQUEST_NEW_INSTANCE = LlmChannelLoadModelCreationParameter
    REQUEST_TOKENIZE = LlmRpcTokenizeParameter
    REQUEST_UNLOAD = LlmRpcUnloadModelParameter


def _model_spec_to_api_dict(model_spec: AnyModelSpecifier) -> ModelSpecifierDict:
    spec: ModelSpecifier
    query: ModelQuery | None = None
    if isinstance(model_spec, dict):
        # Ensure snake case keys pattern match correctly
        model_spec = cast(
            ModelSpecifierDict | ModelQueryDict,
            _snake_case_keys_to_camelCase(model_spec),
        )
    match model_spec:
        case str():
            # Accept a plain string as a shorthand for an identifier query
            query = ModelQuery(identifier=model_spec)
        case ModelSpecifierQuery() | ModelSpecifierInstanceReference():
            # Accept full typed model specifications as structs
            spec = model_spec
        case ModelQuery():
            # Accept an instance reference as a dict
            query = model_spec
        case {"type": "query"}:
            # Accept a full query specifier as a dict
            spec = ModelSpecifierQuery._from_any_api_dict(model_spec)
        case {"type": "instanceReference"}:
            # Accept an instance reference as a dict
            spec = ModelSpecifierInstanceReference._from_any_api_dict(model_spec)
        case {}:
            # Accept an instance reference as a dict
            query = ModelQuery._from_any_api_dict(model_spec)
        case _:
            raise LMStudioValueError(f"Unable to parse model specifier: {model_spec}")
    if query is not None:
        spec = ModelSpecifierQuery(query=query)
    return spec.to_dict()


def load_struct(raw_data: DictObject, data_model: Type[TStruct]) -> TStruct:
    """Convert a builtin dictionary to a LMStudioStruct (msgspec.Struct) instance."""
    return convert(raw_data, data_model)


def _get_data_lines(data: DictObject, prefix: str = "") -> Sequence[str]:
    return [f"{prefix}{line}" for line in _format_json(data).splitlines()]


@sdk_public_type
class LMStudioServerError(LMStudioError):
    """Problems reported by the LM Studio instance."""

    _raw_error: DictObject | None
    server_error: SerializedLMSExtendedError | None

    def __init__(self, message: str, details: DictObject | None = None) -> None:
        """Initialize with SDK message and remote error details."""
        if details is None:
            self._raw_error = self.server_error = None
            formatted_message = message
        else:
            raw_details = dict(details)
            raw_details.pop("stack", None)
            self._raw_error = raw_details
            try:
                parsed_details = SerializedLMSExtendedError._from_any_api_dict(
                    raw_details
                )
                text_details = self._format_server_error(parsed_details)
            except Exception:
                parsed_details = SerializedLMSExtendedError()
                text_details = _format_json(raw_details)
            self.server_error = parsed_details
            formatted_message = f"{message}: {text_details}"
        super().__init__(formatted_message)

    @staticmethod
    def _format_server_error(details: SerializedLMSExtendedError) -> str:
        if details.title:
            if details.root_title and details.root_title != details.title:
                header = f"{details.root_title}: {details.title}"
            else:
                header = details.title
        elif details.root_title:
            header = details.root_title
        else:
            header = "Unknown remote error"
        lines: list[str] = []
        if details.display_data is not None:
            lines.extend(("", "  Additional information from server:"))
            lines.extend(_get_data_lines(details.display_data, "    "))
        if details.error_data is not None:
            lines.extend(("", "  Error details from server:"))
            lines.extend(_get_data_lines(details.error_data, "    "))
        if details.cause is not None:
            lines.extend(("", "  Reported cause:"))
            lines.extend(f"    {details.cause}")
        if details.suggestion is not None:
            lines.extend(("", "  Suggested potential remedy:"))
            lines.extend(f"    {details.suggestion}")
        # Only use the multi-line format if at least one
        # of the extended error fields is populated
        if lines:
            additional_text = "\n".join(lines)
            return f"\n\n  {header}\n{additional_text}"
        return header

    @staticmethod
    def from_details(message: str, details: DictObject) -> "LMStudioServerError":
        """Return appropriate class with SDK message and server error details."""
        default_error = LMStudioServerError(message, details)
        parsed_details = default_error.server_error
        if parsed_details is None:
            return default_error
        display_data = parsed_details.display_data
        if display_data:
            specific_error: LMStudioServerError | None = None
            match display_data:
                case {"code": "generic.noModelMatchingQuery"}:
                    specific_error = LMStudioModelNotFoundError(str(default_error))
            if specific_error is not None:
                specific_error._raw_error = default_error._raw_error
                specific_error.server_error = default_error.server_error
                return specific_error
        return default_error


@sdk_public_type
class LMStudioModelNotFoundError(LMStudioServerError):
    """No model matching the given specifier could be located on the server."""


@sdk_public_type
class LMStudioChannelClosedError(LMStudioServerError):
    """Streaming channel unexpectedly closed by the LM Studio instance."""

    def __init__(self, message: str) -> None:
        """Initialize with SDK message."""
        super().__init__(message, None)


@sdk_public_type
class LMStudioPredictionError(LMStudioServerError):
    """Problems reported by the LM Studio instance during a model prediction."""


@sdk_public_type
class LMStudioClientError(LMStudioError):
    """Problems identified locally in the SDK client."""


@sdk_public_type
class LMStudioUnknownMessageError(LMStudioClientError):
    """Client has received a message in a format it wasn't expecting."""


@sdk_public_type
class LMStudioCancelledError(LMStudioClientError):
    """Requested operation was cancelled via the SDK client session."""


@sdk_public_type
class LMStudioWebsocketError(LMStudioClientError):
    """Client websocket sessiqqon has terminated (or was never opened)."""


# dataclass vs LMStudioStruct:
#
# LMStudioStruct is specifically designed to handle serialisation
# to and from JSON-compatible dicts with camelCase keys.
#
# For SDK-only record types that are never serialised to or
# from JSON-compatible dicts, use data classes instead.


@dataclass(kw_only=True, frozen=True, slots=True)
class ModelLoadResult:
    """Details of a loaded LM Studio model."""

    identifier: str
    instance_reference: str
    path: str


@dataclass(kw_only=True, frozen=True, slots=True)
class PredictionResult(Generic[TPrediction]):
    """The final result of a prediction."""

    # fmt: off
    content: str                   # The text content of the prediction
    parsed: TPrediction            # dict for structured predictions, str otherwise
    stats: LlmPredictionStats      # Statistics about the prediction process
    model_info: LlmInfo            # Information about the model used
    structured: bool = field(init=False)  # Whether the result is structured or not
    # Note that the configuration reported here uses the *server* config names,
    # not the attributes used to set the configuration in the client SDK
    # Private until these attributes store the client config types
    _load_config: DictObject        # The configuration used to load the model
    _prediction_config: DictObject  # The configuration used for the prediction
    # fmt: on

    def __post_init__(self) -> None:
        # Instances are frozen, so `self.structured` can't be set directly
        object.__setattr__(self, "structured", self.parsed is not self.content)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(content={self.content!r})"

    def __str__(self) -> str:
        if self.structured:
            return _format_json(self.parsed)
        return self.content

    def _to_history_content(self) -> str:
        return self.content


@dataclass(kw_only=True, frozen=True, slots=True)
class PredictionRoundResult(PredictionResult[str]):
    """The result of a prediction within a multi-round tool using action."""

    round_index: int  # The round within the action that produced this result

    @classmethod
    def from_result(cls, result: PredictionResult[str], round_index: int) -> Self:
        """Create a prediction round result from its underlying prediction result."""
        copied_keys = {
            k: getattr(result, k)
            for k, v in result.__dataclass_fields__.items()
            if v.init
        }
        return cls(round_index=round_index, **copied_keys)


@dataclass(kw_only=True, frozen=True, slots=True)
class ActResult:
    """Summary of a completed multi-round tool using action."""

    # Detailed action results are reported via callbacks (for now)

    # fmt: off
    rounds: int
    total_time_seconds: float
    # fmt: on


def _redact_json(data: DictObject | None) -> DictObject | None:
    """Show top level structure without any substructure details."""
    if data is None:
        return None
    redacted: dict[str, Any] = {}
    for k, v in data.items():
        match v:
            case {}:
                redacted[k] = {"...": "..."}
            case [*_]:
                redacted[k] = ["..."]
            case _:
                redacted[k] = v
    return redacted


TQueue = TypeVar("TQueue")


class MultiplexingManager(Generic[TQueue]):
    """Helper class to allocate distinct protocol multiplexing IDs."""

    def __init__(self, logger: StructuredLogger) -> None:
        """Initialize ID multiplexer."""
        self._open_channels: dict[int, TQueue] = {}
        self._last_channel_id = 0
        self._pending_calls: dict[int, TQueue] = {}
        self._last_call_id = 0
        # `_active_subscriptions` (if we add signal support)
        # `_last_subscriber_id` (if we add signal support)
        self._logger = logger

    def all_queues(self) -> Iterator[TQueue]:
        """Iterate over all queues (for example, to send a shutdown message)."""
        yield from self._open_channels.values()
        yield from self._pending_calls.values()
        # yield from self._active_subscriptions.values()

    def _get_next_channel_id(self) -> int:
        """Get next distinct channel ID."""
        next_id = self._last_channel_id + 1
        self._last_channel_id = next_id
        return next_id

    @contextmanager
    def assign_channel_id(self, rx_queue: TQueue) -> Generator[int, None, None]:
        """Assign distinct streaming channel ID to given queue."""
        channel_id = self._get_next_channel_id()
        self._open_channels[channel_id] = rx_queue
        try:
            yield channel_id
        finally:
            dropped_queue = self._open_channels.pop(channel_id, None)
            assert dropped_queue is rx_queue, (
                f"Unexpected change to reply queue for channel ({channel_id} in {self!r})"
            )

    def _get_next_call_id(self) -> int:
        """Get next distinct RPC ID."""
        next_id = self._last_call_id + 1
        self._last_call_id = next_id
        return next_id

    @contextmanager
    def assign_call_id(self, rx_queue: TQueue) -> Generator[int, None, None]:
        """Assign distinct remote call ID to given queue."""
        call_id = self._get_next_call_id()
        self._pending_calls[call_id] = rx_queue
        try:
            yield call_id
        finally:
            dropped_queue = self._pending_calls.pop(call_id, None)
            assert dropped_queue is rx_queue, (
                f"Unexpected change to reply queue for remote call ({call_id} in {self!r})"
            )

    def map_rx_message(self, message: DictObject) -> TQueue | None:
        """Map received message to the relevant demultiplexing queue."""
        # TODO: Define an even-spammier-than-debug trace logging level for this
        # self._logger.trace("Incoming websocket message", json=message)
        rx_queue: TQueue | None = None
        match message:
            case {"channelId": channel_id}:
                rx_queue = self._open_channels.get(channel_id, None)
                if rx_queue is None:
                    if channel_id <= self._last_channel_id:
                        if message.get("type") == "channelClose":
                            # Ignore close messages for channels that were already closed
                            pass
                        else:
                            self._logger.warn(
                                f"Received unhandled message {message} for already closed channel",
                                channel_id=channel_id,
                            )
                    else:
                        self._logger.warn(
                            f"Received message {message} for not yet used channel",
                            channel_id=channel_id,
                        )
            case {"callId": call_id}:
                rx_queue = self._pending_calls.get(call_id, None)
                if rx_queue is None:
                    self._logger.warn(
                        "Received response to unknown call", call_id=call_id
                    )
            case {"type": "communicationWarning", "warning": warning}:
                # The SDK should NOT be causing protocol warnings, so log this as an error
                self._logger.error("SDK communication warning", warning=warning)
                return None
            case unmatched:
                raise LMStudioClientError(f"Unexpected message: {unmatched}")
        return rx_queue


# Channel events are processed via structural pattern matching, so it would be nice
# to define them as tuples to make them as lightweight as possible at runtime.
# Unfortunately, mypy doesn't cleanly support exhaustiveness checking if we define
# them that way: https://github.com/python/mypy/issues/16650
# Instead, we define our own generic base type and define subclasses for each event


@dataclass(frozen=True, slots=True)
class ChannelRxEvent(Generic[T]):
    arg: T


class ChannelFinishedEvent(ChannelRxEvent[None]):
    pass


ChannelCommonRxEvent: TypeAlias = ChannelFinishedEvent
TRxEvent = TypeVar("TRxEvent", bound=ChannelRxEvent[Any], contravariant=True)


class ChannelEndpoint(Generic[T, TRxEvent, TWireFormat], ABC):
    """Base class for defining API channel endpoints."""

    # Overridden in concrete subclasses
    _API_ENDPOINT = ""
    _NOTICE_PREFIX = ""

    def __init__(
        self, creation_params: LMStudioStruct[TWireFormat] | DictObject
    ) -> None:
        """Initialize API channel endpoint handler."""
        if not isinstance(creation_params, LMStudioStruct):
            creation_params = LMStudioStruct._from_any_api_dict(creation_params)
        self._creation_params = creation_params.to_dict()
        # Channel processing state tracking
        self._is_finished = False
        self._result: T | None = None
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(endpoint=self._API_ENDPOINT)

    @property
    def api_endpoint(self) -> str:
        """Get the API endpoint for this channel."""
        return self._API_ENDPOINT

    @property
    def creation_params(self) -> TWireFormat:
        """Get the creation parameters for this channel."""
        return self._creation_params

    @property
    def notice_prefix(self) -> str:
        """Get the logging notification prefix for this channel."""
        return self._NOTICE_PREFIX

    @property
    def is_finished(self) -> bool:
        """Indicate whether further message reception on the channel is needed."""
        return self._is_finished

    def _set_result(self, result: T) -> ChannelFinishedEvent:
        # Note: errors are raised immediately when handling the relevant message
        #       rather than only being reported when the result is accessed
        self._is_finished = True
        self._result = result
        return ChannelFinishedEvent(None)

    def result(self) -> T:
        """Read the result from a finished channel."""
        if not self._is_finished:
            raise LMStudioRuntimeError(
                "Attempted to read result from an active channel."
            )
        assert self._result is not None
        return self._result

    def raise_unknown_message_error(self, unknown_message: Any) -> NoReturn:
        raise LMStudioUnknownMessageError(
            f"{self._NOTICE_PREFIX} unexpected message contents: {unknown_message!r}"
        )

    # See ChannelHandler below for more details on the routing of received messages
    # from the API namespace websocket to the corresponding channel instances

    # Called in the foreground channel event processing context
    # to convert server messages to Rx events for further processing
    # Defined as an iterable, since one server message may trigger multiple Rx events
    @abstractmethod
    def iter_message_events(self, contents: DictObject | None) -> Iterable[TRxEvent]:
        raise NotImplementedError

    # Called in the foreground channel event processing context
    # to process Rx events and invoke any registered callbacks
    @abstractmethod
    def handle_rx_event(self, event: TRxEvent) -> None:
        raise NotImplementedError

    # Convenience API to simply process all received events
    # without inspecting them individually
    def handle_message_events(self, contents: DictObject | None) -> None:
        for event in self.iter_message_events(contents):
            self.handle_rx_event(event)


class ModelDownloadProgressEvent(ChannelRxEvent[DownloadProgressUpdate]):
    pass


class ModelDownloadFinalizeEvent(ChannelRxEvent[None]):
    pass


ModelDownloadRxEvent: TypeAlias = (
    ModelDownloadProgressEvent | ModelDownloadFinalizeEvent | ChannelCommonRxEvent
)

DownloadProgressCallback: TypeAlias = Callable[[DownloadProgressUpdate], Any]
DownloadFinalizedCallback: TypeAlias = Callable[[], Any]


class ModelDownloadEndpoint(
    ChannelEndpoint[str, ModelDownloadRxEvent, DownloadModelChannelRequestDict]
):
    """API channel endpoint for downloading available models."""

    _API_ENDPOINT = "downloadModel"
    _NOTICE_PREFIX = "Model download"

    def __init__(
        self,
        download_identifier: str,
        on_progress: DownloadProgressCallback | None = None,
        on_finalize: DownloadFinalizedCallback | None = None,
    ) -> None:
        params = DownloadModelChannelRequest._from_api_dict(
            {"downloadIdentifier": download_identifier}
        )
        super().__init__(params)
        self._download_identifier = download_identifier
        self._on_progress = on_progress
        self._on_finalize = on_finalize

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[ModelDownloadRxEvent]:
        match contents:
            case None:
                raise LMStudioChannelClosedError(
                    "Server failed to complete model download."
                )
            case {
                "type": "downloadProgress",
                "update": {
                    "downloadedBytes": downloaded_bytes,
                    "totalBytes": total_bytes,
                    "speedBytesPerSecond": speed_bytes_per_second,
                },
            }:
                if self._on_progress is not None:
                    yield ModelDownloadProgressEvent(
                        DownloadProgressUpdate(
                            downloaded_bytes=downloaded_bytes,
                            total_bytes=total_bytes,
                            speed_bytes_per_second=speed_bytes_per_second,
                        ),
                    )
            case {"type": "startFinalizing"}:
                if self._on_finalize is not None:
                    yield ModelDownloadFinalizeEvent(None)
            case {"type": "success", "defaultIdentifier": str(default_identifier)}:
                yield self._set_result(default_identifier)
            case unmatched:
                self.raise_unknown_message_error(unmatched)

    def handle_rx_event(self, event: ModelDownloadRxEvent) -> None:
        match event:
            case ModelDownloadProgressEvent(update):
                self._report_progress(update)
            case ModelDownloadFinalizeEvent(_):
                self._finalize_download()
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)

    def _report_progress(self, progress: DownloadProgressUpdate) -> None:
        # This event is only emitted if a callback is registered
        assert self._on_progress is not None
        err_msg = (
            f"Progress callback failed when downloading {self._download_identifier!r}"
        )
        with sdk_callback_invocation(err_msg, self._logger):
            self._on_progress(progress)

    def _finalize_download(self) -> None:
        # This event is only emitted if a callback is registered
        assert self._on_finalize is not None
        err_msg = (
            f"Download finalization callback failed for {self._download_identifier!r}"
        )
        with sdk_callback_invocation(err_msg, self._logger):
            self._on_finalize()


class ModelLoadingProgressEvent(ChannelRxEvent[float]):
    pass


ModelLoadingRxEvent: TypeAlias = ModelLoadingProgressEvent | ChannelCommonRxEvent

ModelLoadingCallback: TypeAlias = Callable[[float], Any]


class _ModelLoadingEndpoint(
    ChannelEndpoint[ModelLoadResult, ModelLoadingRxEvent, TWireFormat]
):
    def __init__(
        self,
        model_key: str,
        creation_params: LMStudioStruct[TWireFormat] | DictObject,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> None:
        super().__init__(creation_params)
        self._logger.update_context(model_key=model_key)
        self._model_key = model_key
        self._on_load_progress = on_load_progress
        self._last_progress_event = -1.0

    def _update_progress(self, progress: float) -> Iterable[ModelLoadingProgressEvent]:
        if progress <= self._last_progress_event:
            # Disallow going backwards or repeating values
            return
        self._last_progress_event = progress
        if self._on_load_progress is not None:
            yield ModelLoadingProgressEvent(progress)

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[ModelLoadingRxEvent]:
        if self._is_finished:
            raise LMStudioClientError("Attempted to update a completed channel.")
        match contents:
            case None:
                raise LMStudioChannelClosedError(
                    "Server failed to load requested model."
                )
            case {"type": "resolved"}:
                # log warning for ambiguous load resolution
                if contents and "ambiguous" in contents.keys():
                    self._logger.warn(
                        "Ambiguous model load request",
                        ambiguous=contents.get("ambiguous", None),
                    )
            case {"type": "startLoading"}:
                self._logger.debug(f"{self._NOTICE_PREFIX} started")
                yield from self._update_progress(0.0)
            case {"type": "loadProgress" | "progress", "progress": progress}:
                yield from self._update_progress(progress)
            case {"type": "unloadingOtherJITModel", "info": other_model_info} if (
                "modelKey" in other_model_info
            ):
                jit_unload_event = "Unloading other JIT model"
                unloaded_model_key = other_model_info["modelKey"]
                suggestion = (
                    "You can disable this behavior by going to "
                    "LM Studio -> Settings -> Developer -> Turn OFF JIT models auto-evict"
                )
                # Report the JIT unload
                self._logger.info(
                    jit_unload_event,
                    unloaded_model_key=unloaded_model_key,
                    suggestion=suggestion,
                )
                # Report further details on the unloaded model if debug messages are enabled
                self._logger.debug(
                    jit_unload_event,
                    unloaded_model_key=unloaded_model_key,
                    unloaded_model=other_model_info,
                )
            case {
                "type": "success" | "alreadyLoaded" | "loadSuccess",
                "info": {
                    "identifier": instance_identifier,
                    "instanceReference": instance_reference,
                    "path": model_path,
                },
            }:
                if self._last_progress_event < 1.0:
                    yield from self._update_progress(1.0)
                result = ModelLoadResult(
                    identifier=instance_identifier,
                    instance_reference=instance_reference,
                    path=model_path,
                )
                yield self._set_result(result)
            case unmatched:
                self.raise_unknown_message_error(unmatched)

    def handle_rx_event(self, event: ModelLoadingRxEvent) -> None:
        match event:
            case ModelLoadingProgressEvent(progress):
                self._report_progress(progress)
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)

    def _report_progress(self, progress: float) -> None:
        # This event is only emitted if a callback is registered
        assert self._on_load_progress is not None
        err_msg = f"Progress callback failed when loading {self._model_key!r}"
        with sdk_callback_invocation(err_msg, self._logger):
            self._on_load_progress(progress)


class LoadModelEndpoint(
    _ModelLoadingEndpoint[LoadModelChannelRequestDict],
    Generic[TLoadConfig, TLoadConfigDict],
):
    """API channel endpoint for loading downloaded models."""

    _API_ENDPOINT = "loadModel"
    _NOTICE_PREFIX = "Model load"

    def __init__(
        self,
        model_key: str,
        instance_identifier: str | None,
        ttl: int | None,
        creation_param_type: Type[LoadModelChannelRequest],
        config_type: Type[TLoadConfig],
        config: TLoadConfig | TLoadConfigDict | None,
        on_load_progress: ModelLoadingCallback | None,
    ) -> None:
        """Load the specified model with the given identifier and configuration."""
        kv_config = load_config_to_kv_config_stack(config, config_type)
        params = creation_param_type._from_api_dict(
            {
                "modelKey": model_key,
                "identifier": instance_identifier,
                "loadConfigStack": kv_config.to_dict(),
            }
        )
        if ttl is not None:
            params.ttl_ms = ttl * 1000
        super().__init__(model_key, params, on_load_progress)


class GetOrLoadEndpoint(
    _ModelLoadingEndpoint[GetOrLoadChannelRequestDict],
    Generic[TLoadConfig, TLoadConfigDict],
):
    """API channel endpoint for ensuring models have been loaded."""

    _API_ENDPOINT = "getOrLoad"
    _NOTICE_PREFIX = "Model get/load"

    def __init__(
        self,
        model_key: str,
        ttl: int | None,
        creation_param_type: Type[GetOrLoadChannelRequest],
        config_type: Type[TLoadConfig],
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> None:
        """Get the specified model, loading with given configuration if necessary."""
        kv_config = load_config_to_kv_config_stack(config, config_type)
        params = creation_param_type._from_api_dict(
            {
                "identifier": model_key,  # Model paths are also accepted
                "loadConfigStack": kv_config.to_dict(),
            }
        )
        if ttl is not None:
            params.load_ttl_ms = ttl * 1000
        super().__init__(model_key, params, on_load_progress)


class ToolFunctionDefDict(TypedDict):
    """SDK input format to specify an LLM tool call and its implementation (as a dict)."""

    name: str
    description: str
    parameters: Mapping[str, Any]
    implementation: Callable[..., Any]


@dataclass(kw_only=True, frozen=True, slots=True)
class ToolFunctionDef:
    """SDK input format to specify an LLM tool call and its implementation."""

    name: str
    description: str
    parameters: Mapping[str, Any]
    implementation: Callable[..., Any]

    def _to_llm_tool_def(self) -> tuple[type[Struct], LlmTool]:
        params_struct_name = f"{self.name.capitalize()}Parameters"
        params_struct = defstruct(params_struct_name, self.parameters.items())
        return params_struct, LlmTool._from_api_dict(
            {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    # LM Studio expects a JSON schema here, but specifies the expected keys,
                    # while the schema conversion annotation just indicates it returns a dict
                    "parameters": cast(
                        Any, _to_json_schema(params_struct, omit=("title",))
                    ),
                },
            }
        )

    @classmethod
    def from_callable(
        cls,
        f: Callable[..., Any],
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Self:
        """Derive a tool function definition from the given callable."""
        if name is None:
            try:
                name = f.__name__
            except Exception as exc:
                raise LMStudioValueError(
                    f"Could not extract tool name from {f!r}"
                ) from exc
        if description is None:
            try:
                description = f.__doc__
            except Exception as exc:
                raise LMStudioValueError(
                    f"Could not extract tool description from {f!r}"
                ) from exc
            if not description:
                raise LMStudioValueError(
                    f"Could not extract tool description from {f!r} (no docstring set)"
                )
        try:
            parameters = get_type_hints(f, include_extras=True)
        except Exception as exc:
            raise LMStudioValueError(
                f"Could not extract tool parameter info from {f!r}"
            ) from exc
        # Tool definitions only annotate the input parameters, not the return type
        parameters.pop("return", None)
        return cls(
            name=name, description=description, parameters=parameters, implementation=f
        )


class PredictionPrepProgressEvent(ChannelRxEvent[float]):
    pass


class PredictionFragmentEvent(ChannelRxEvent[LlmPredictionFragment]):
    pass


class PredictionToolCallEvent(ChannelRxEvent[ToolCallRequest]):
    pass


class PredictionToolCallAbortedEvent(ChannelRxEvent[None]):
    pass


PredictionRxEvent: TypeAlias = (
    PredictionPrepProgressEvent
    | PredictionFragmentEvent
    | PredictionToolCallEvent
    | PredictionToolCallAbortedEvent
    | ChannelCommonRxEvent
)

ClientToolSpec: TypeAlias = tuple[type[Struct], Callable[..., Any]]
ClientToolMap: TypeAlias = Mapping[str, ClientToolSpec]

PredictionMessageCallback: TypeAlias = Callable[[AssistantResponse], Any]
PredictionFirstTokenCallback: TypeAlias = Callable[[], Any]
PredictionFragmentCallback: TypeAlias = Callable[[LlmPredictionFragment], Any]
PromptProcessingCallback: TypeAlias = Callable[[float], Any]


class PredictionEndpoint(
    Generic[TPrediction],
    ChannelEndpoint[
        PredictionResult[TPrediction], PredictionRxEvent, PredictionChannelRequestDict
    ],
):
    """Helper class for prediction endpoint message handling."""

    _API_ENDPOINT = "predict"

    def __init__(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
        # The remaining options are only relevant for multi-round tool actions
        handle_invalid_tool_request: Callable[
            [LMStudioPredictionError, ToolCallRequest | None], str
        ]
        | None = None,
        llm_tools: LlmToolUseSettingToolArray | None = None,
        client_tool_map: ClientToolMap | None = None,
    ) -> None:
        if llm_tools is None:
            client_tool_map = {}
        else:
            # Caller is responsible for ensuring tool config is consistent
            # (e.g., by creating them with `ChatResponseEndpoint.parse_tools`)
            assert client_tool_map is not None
            assert llm_tools.tools is not None
            assert len(llm_tools.tools) == len(client_tool_map)
            if config is None:
                config = LlmPredictionConfig(raw_tools=llm_tools)
            else:
                config = copy.copy(config)
                if isinstance(config, dict):
                    config["rawTools"] = llm_tools.to_dict()
                else:
                    config.raw_tools = llm_tools
        config_stack = self._make_config_override(response_format, config)
        params = PredictionChannelRequest._from_api_dict(
            {
                "modelSpecifier": _model_spec_to_api_dict(model_specifier),
                "history": history._get_history_for_prediction(),
                "predictionConfigStack": config_stack.to_dict(),
            }
        )
        super().__init__(params)
        # Status tracking for the prediction progress and result reporting
        self._is_cancelled = False
        self._structured = response_format is not None
        self._on_message = on_message
        self._prompt_processing_progress = -1.0
        self._on_prompt_processing_progress = on_prompt_processing_progress
        self._on_first_token = on_first_token
        self._on_prediction_fragment = on_prediction_fragment
        self._on_handle_invalid_tool_request = handle_invalid_tool_request
        # Fragment content is always text, even for structured responses
        self._fragment_content: list[str] = []
        # Track available tools for multi-response processing
        self._client_tools = client_tool_map

    @classmethod
    def _make_config_override(
        cls,
        response_format: Type[ModelSchema] | DictSchema | None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None,
    ) -> KvConfigStack:
        return prediction_config_to_kv_config_stack(
            response_format, config, **cls._additional_config_options()
        )

    @classmethod
    def _additional_config_options(cls) -> DictObject:
        return {}

    def _update_prompt_processing_progress(
        self, progress: float
    ) -> Iterable[PredictionPrepProgressEvent]:
        last_progress_update = self._prompt_processing_progress
        if progress <= last_progress_update:
            # Disallow going backwards or repeating values
            return
        self._prompt_processing_progress = progress
        if self._on_prompt_processing_progress:
            if last_progress_update < 0 < progress:
                # Ensure a 0.0 progress event is emitted
                yield PredictionPrepProgressEvent(0.0)
            yield PredictionPrepProgressEvent(progress)

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[PredictionRxEvent]:
        match contents:
            case None:
                # Server closed the channel without completing the prediction
                raise LMStudioChannelClosedError(
                    "Server failed to complete prediction."
                )
            case {
                "type": "fragment",
                "fragment": {} as fragment,
            }:
                if self._is_cancelled:
                    # Ignore fragments received after cancellation (avoids race condition)
                    return
                if self._prompt_processing_progress < 1.0:
                    # The server only starts emitting tokens after prompt processing
                    # is complete, but may skip actually sending the completion event
                    yield from self._update_prompt_processing_progress(1.0)
                parsed_fragment = LlmPredictionFragment._from_any_api_dict(fragment)
                self._fragment_content.append(parsed_fragment.content)
                yield PredictionFragmentEvent(parsed_fragment)
            case {"type": "promptProcessingProgress", "progress": progress}:
                if self._is_cancelled:
                    # Ignore status updates after cancellation (avoids race condition)
                    return
                yield from self._update_prompt_processing_progress(progress)
            case {
                "type": "toolCallGenerationStart",
            }:
                self._logger.debug("Notified of pending tool call request generation.")
            case {
                "type": "toolCallGenerationEnd",
                "toolCallRequest": tool_call_request,
            }:
                yield PredictionToolCallEvent(
                    ToolCallRequest._from_api_dict(tool_call_request)
                )
            case {
                "type": "toolCallGenerationFailed",
            }:
                self._logger.warn("Tool call processing generation failed.")
                yield PredictionToolCallAbortedEvent(None)
            case {"type": "error", "error": {} as error}:
                raise LMStudioPredictionError("Prediction error", error)
            case {
                "type": "success",
                "stats": stats,
                "modelInfo": model_info,
                "loadModelConfig": load_kvconfig,
                "predictionConfig": prediction_kvconfig,
            }:
                # Prediction has either completed successfully
                # or has been successfully cancelled. Don't try
                # to parse the received content in the latter case.
                result_content = "".join(self._fragment_content)
                if self._structured and not self._is_cancelled:
                    parsed_content = json.loads(result_content)
                else:
                    parsed_content = result_content
                yield self._set_result(
                    PredictionResult(
                        content=result_content,
                        parsed=parsed_content,
                        stats=LlmPredictionStats._from_any_api_dict(stats),
                        model_info=LlmInfo._from_any_api_dict(model_info),
                        _load_config=dict_from_fields_key(load_kvconfig),
                        _prediction_config=dict_from_fields_key(prediction_kvconfig),
                    )
                )
            case unmatched:
                self.raise_unknown_message_error(unmatched)

    def handle_rx_event(self, event: PredictionRxEvent) -> None:
        match event:
            case PredictionPrepProgressEvent(progress):
                self._report_prompt_processing_progress(progress)
            case PredictionFragmentEvent(_fragment):
                if self._on_first_token is not None:
                    self._logger.debug("Invoking on_first_token callback")
                    err_msg = f"First token callback failed for {self!r}"
                    with sdk_callback_invocation(err_msg, self._logger):
                        self._on_first_token()
                    self._on_first_token = None
                if self._on_prediction_fragment is not None:
                    # TODO: Define an even-spammier-than-debug trace logging level for this
                    # self._logger.trace("Invoking on_prediction_fragment callback")
                    err_msg = f"Prediction fragment callback failed for {self!r}"
                    with sdk_callback_invocation(err_msg, self._logger):
                        self._on_prediction_fragment(_fragment)
                pass
            case PredictionToolCallEvent(_tool_call_request):
                # Handled externally when iterating over events
                pass
            case PredictionToolCallAbortedEvent(_):
                self._handle_invalid_tool_request("Failed to parse tool call request.")
            case ChannelFinishedEvent(_):
                if self._on_message is not None:
                    result = self._result
                    assert result is not None
                    response = AssistantResponse(
                        content=[Chat._parse_assistant_response(result)]
                    )
                    self._on_message(response)

            case _:
                assert_never(event)

    def _report_prompt_processing_progress(self, progress: float) -> None:
        # This event is only emitted if a callback is registered
        assert self._on_prompt_processing_progress is not None
        err_msg = f"Prediction progress callback failed for {self!r}"
        with sdk_callback_invocation(err_msg, self._logger):
            self._logger.debug("Invoking on_prompt_processing_progress callback")
            self._on_prompt_processing_progress(progress)

    def _handle_invalid_tool_request(
        self, err_msg: str, request: ToolCallRequest | None = None
    ) -> str:
        exc = LMStudioPredictionError(err_msg)
        _on_handle_invalid_tool_request = self._on_handle_invalid_tool_request
        if _on_handle_invalid_tool_request is not None:
            # Allow users to override the error message, or force an exception
            self._logger.debug("Invoking on_handle_invalid_tool_request callback")
            err_msg = _on_handle_invalid_tool_request(exc, request)
        if request is not None:
            return err_msg
        # We don't allow users to prevent the exception when there's no request
        raise LMStudioPredictionError(err_msg)

    def request_tool_call(
        self, request: ToolCallRequest
    ) -> Callable[[], ToolCallResultData]:
        tool_name = request.name
        tool_call_id = request.id
        client_tool = self._client_tools.get(tool_name, None)
        if client_tool is None:
            err_msg = self._handle_invalid_tool_request(
                f"Cannot find tool with name {tool_name}.", request
            )
            result = ToolCallResultData(content=err_msg, tool_call_id=tool_call_id)
            return lambda: result
        # Validate parameters against their specification
        params_struct, implementation = client_tool
        raw_kwds = request.arguments
        try:
            parsed_kwds = convert(raw_kwds, params_struct)
        except Exception as exc:
            err_msg = self._handle_invalid_tool_request(
                f"Failed to parse arguments for tool {tool_name}: {exc}", request
            )
            result = ToolCallResultData(content=err_msg, tool_call_id=tool_call_id)
            return lambda: result
        kwds = to_builtins(parsed_kwds)

        # Allow caller to schedule the tool call request for background execution
        def _call_requested_tool() -> ToolCallResultData:
            call_result = implementation(**kwds)
            return ToolCallResultData(
                content=json.dumps(call_result), tool_call_id=tool_call_id
            )

        return _call_requested_tool

    def mark_cancelled(self) -> None:
        """Mark the prediction as cancelled and quietly drop incoming tokens."""
        self._is_cancelled = True


class CompletionEndpoint(PredictionEndpoint[TPrediction]):
    """API channel endpoint for requesting text completion from a model."""

    _NOTICE_PREFIX = "Completion"

    def __init__(
        self,
        model_specifier: AnyModelSpecifier,
        prompt: str,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> None:
        """Load the specified model with the given identifier and configuration."""
        history = Chat()
        history.add_user_message(prompt)
        super().__init__(
            model_specifier,
            history,
            response_format,
            config,
            on_message,
            on_first_token,
            on_prediction_fragment,
            on_prompt_processing_progress,
        )

    @classmethod
    def _additional_config_options(cls) -> DictObject:
        return {"for_text_completion": True}


ToolDefinition: TypeAlias = ToolFunctionDef | ToolFunctionDefDict | Callable[..., Any]


class ChatResponseEndpoint(PredictionEndpoint[TPrediction]):
    """API channel endpoint for requesting a chat response from a model."""

    _NOTICE_PREFIX = "Chat response"

    # Tool parsing is implemented as a static method so multi-round predictions
    # don't need to recreate the client tool details on each iteration
    # TODO: Consider implementing this conversion in _kv_config.py
    @staticmethod
    def parse_tools(
        tools: Iterable[ToolDefinition],
    ) -> tuple[LlmToolUseSettingToolArray, ClientToolMap]:
        """Split tool function definitions into server and client details."""
        if not tools:
            raise LMStudioValueError(
                "Tool using actions require at least one tool to be defined."
            )
        llm_tool_defs: list[LlmTool] = []
        client_tool_map: dict[str, ClientToolSpec] = {}
        for tool in tools:
            if isinstance(tool, ToolFunctionDef):
                tool_def = tool
            elif callable(tool):
                tool_def = ToolFunctionDef.from_callable(tool)
            else:
                tool_def = ToolFunctionDef(**tool)
            if tool_def.name in client_tool_map:
                raise LMStudioValueError(
                    f"Duplicate tool names are not permitted ({tool_def.name!r} repeated)"
                )
            params_struct, llm_tool_def = tool_def._to_llm_tool_def()
            client_tool_map[tool_def.name] = (params_struct, tool_def.implementation)
            llm_tool_defs.append(llm_tool_def)
        return LlmToolUseSettingToolArray(tools=llm_tool_defs), client_tool_map


class PredictionStreamBase(Generic[TPrediction]):
    """Common base class for sync and async prediction streams."""

    def __init__(
        self,
        endpoint: PredictionEndpoint[TPrediction],
    ) -> None:
        """Initialize a prediction process representation."""
        # Split initialisation out to a separate helper function that plays nice with bound generic type vars
        # To avoid type errors in mypy, subclasses may call this directly (instead of `super().__init__(endpoint)`)
        # https://discuss.python.org/t/how-to-share-type-variables-when-inheriting-from-generic-base-classes/78839
        self._init_prediction(endpoint)

    def _init_prediction(self, endpoint: PredictionEndpoint[TPrediction]) -> None:
        self._endpoint: PredictionEndpoint[TPrediction] = endpoint

        # Final result reporting
        self._is_started = False
        self._is_finished = False
        self._final_result: PredictionResult[TPrediction] | None = None
        self._error: BaseException | None = None

    @property
    def stats(self) -> LlmPredictionStats | None:
        """Get the current prediction statistics if available."""
        if self._final_result is None:
            return None
        return self._final_result.stats

    @property
    def model_info(self) -> LlmInfo | None:
        """Get the model descriptor for the current prediction if available."""
        if self._final_result is None:
            return None
        return self._final_result.model_info

    # Private until this API can emit the client config types
    @property
    def _load_config(self) -> DictObject | None:
        """Get the load configuration used for the current prediction if available."""
        if self._final_result is None:
            return None
        return self._final_result._load_config

    # Private until this API can emit the client config types
    @property
    def _prediction_config(self) -> DictObject | None:
        """Get the prediction configuration used for the current prediction if available."""
        if self._final_result is None:
            return None
        return self._final_result._prediction_config

    @sdk_public_api()
    def result(self) -> PredictionResult[TPrediction]:
        """Get the result of a completed prediction.

        This API raises an exception if the result is not available,
        or if an error occurred while processing the prediction request.

        Use ``wait_for_result()`` to wait for the result to be available.
        Iterate over the prediction to process tokens as they are received.
        """
        # Note: this is a non-blocking API like `asyncio.Future.result()`
        # The awaitable (async) and blocking (sync) behaviour is provided
        # via the `wait_for_result()` methods in the respective subclasses
        # (those methods internally iterate over the received events).
        if not self._is_started:
            raise LMStudioRuntimeError("Prediction processing has not been initiated.")
        if self._error is not None:
            raise self._error
        if self._final_result is None:
            raise LMStudioRuntimeError(
                "Prediction processing has not yet been completed."
            )
        return self._final_result

    def _set_error(self, error: BaseException) -> None:
        """Mark the prediction as failed with an error."""
        if self._is_finished:
            return
        self._is_finished = True
        _truncate_traceback(error)
        self._error = error

    def _mark_started(self) -> None:
        """Mark the prediction as started."""
        self._is_started = True

    def _mark_finished(self) -> None:
        """Mark the prediction as complete and set final metadata."""
        if self._is_finished:
            return

        self._is_finished = True
        self._final_result = self._endpoint.result()

    def _mark_cancelled(self) -> None:
        """Mark the prediction as cancelled and quietly drop incoming tokens."""
        # we can maybe do something with the cancelled state if we want
        self._endpoint.mark_cancelled()


TEndpoint = TypeVar("TEndpoint", bound=ChannelEndpoint[Any, Any, Any])


class ChannelHandler(Generic[TEndpoint]):
    """Bidirectional subchannel message handling."""

    def __init__(
        self,
        channel_id: int,
        endpoint: TEndpoint,
        log_context: LogEventContext,
    ) -> None:
        """Initialize websocket streaming channel."""
        self._is_finished = False
        self._channel_id = channel_id
        self._endpoint = endpoint
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, channel_id=channel_id)

    @property
    def endpoint(self) -> TEndpoint:
        """Get the underlying endpoint definition for this channel."""
        return self._endpoint

    def get_creation_message(self) -> DictObject:
        """Get the message to send to create this channel."""
        endpoint = self._endpoint
        return {
            "type": "channelCreate",
            "endpoint": endpoint.api_endpoint,
            "channelId": self._channel_id,
            "creationParameter": endpoint.creation_params,
        }

    def get_cancel_message(self) -> DictObject:
        """Get the message to send to cancel this channel."""
        return {
            "type": "channelSend",
            "channelId": self._channel_id,
            "message": {"type": "cancel"},
        }

    # This runs in the context of the background demultiplexing task
    # The return value is sent to the foreground task/thread via
    # an asynchronous or synchronous queue (as appropriate)
    # The foreground task/thread continues processing the queue until
    # `None` is received, or until the received message indicates
    # no further processing is required.
    def handle_rx_message(
        self,
        message: DictObject,
    ) -> DictObject | None:
        """Stream received channel messages until channel is closed by server."""
        notice_prefix = self._endpoint.notice_prefix
        # TODO: Define an even-spammier-than-debug trace logging level for this
        # self._logger.trace("Received channel message", json=_redact_json(message))

        match message:
            case {
                "type": "channelSend",
                "channelId": self._channel_id,
                "message": dict(contents),
            }:
                return contents
            case {
                "type": "channelClose",
                "channelId": self._channel_id,
            }:
                # We're done here
                return None
            case {
                "type": "channelError",
                "channelId": self._channel_id,
                "error": {} as error,
            }:
                raise LMStudioServerError.from_details(f"{notice_prefix} error", error)
            case {"type": "communicationWarning", "warning": warning}:
                # The SDK should NOT be causing protocol warnings, so log this as an error
                self._logger.error(
                    f"{notice_prefix} SDK channel warning", warning=warning
                )
        raise LMStudioClientError(f"{notice_prefix} unexpected message: {message}")


class RemoteCallHandler:
    """Remote procedure call message handling."""

    def __init__(
        self,
        call_id: int,
        log_context: LogEventContext,
        notice_prefix: str = "RPC",
    ) -> None:
        """Initialize websocket remote procedure call."""
        self._call_id = call_id
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, call_id=call_id)
        self._notice_prefix = notice_prefix

    def get_rpc_message(
        self, endpoint: str, params: AnyLMStudioStruct | None
    ) -> DictObject:
        """Get the message to send to initiate this remote procedure call."""
        message = {
            "type": "rpcCall",
            "endpoint": endpoint,
            "callId": self._call_id,
        }
        if params is not None:
            message["parameter"] = params.to_dict()
        return message

    # This runs in the context of the background demultiplexing task
    # The return value is sent to the foreground task/thread via
    # an asynchronous or synchronous queue (as appropriate).
    # The foreground task/thread stops processing the queue
    # as soon as it receives a response
    def handle_rx_message(self, message: DictObject) -> Any:
        """Handle received call response."""
        notice_prefix = self._notice_prefix
        self._logger.debug("Received RPC result", json=_redact_json(message))

        match message:
            case {"type": "rpcResult", "callId": self._call_id, "result": result}:
                # This is the expected result
                return result
            case {"type": "rpcResult", "callId": self._call_id}:
                # Some APIs have a "void" return and don't send a result at all
                return None
            case {"type": "rpcError", "callId": self._call_id, "error": {} as error}:
                raise LMStudioServerError.from_details(f"{notice_prefix} error", error)
        raise LMStudioClientError(f"{notice_prefix} unexpected message: {message}")


# TODO: Add remote call endpoint types (technical details TBD)
#         * RemoteCallEndpoint (abstract base class)
#         * RemoteCallBase (generic on TSchema parameter and result types)
#         * RemoteCallVoidBase (generic on TSchema parameter, always returns None)
#         * RemoteCallSequenceBase (generic on TSchema parameter and result element types)
#         * RemoteCallOptionalBase (returns named field if it exists, default value otherwise)
#         * concrete remote call types specialising the above for each endpoint
#
#       Change RPC `endpoint` parameters from strings to `Type[RemoteCallEndpoint]`
#       This is necessary as the different endpoints will have different parameters.
#       It may prove useful to have an RPC_ENDPOINTS registry that allows the I/O bound
#       API implementations to look up the endpoint details based on the API namespace
#       and endpoint names instead of directly importing the relevant classes
#
#       The incentive to actually do this is relatively low, since the RPC methods are
#       *already* pretty low boilerplate, so the pay-off in overall code reduction isn't
#       as high as it is for centralising the channel endpoint receive message processing.
#
#       One potential alternative approach would be to instead define a ModelSessionBase
#       class that handles all of the interactions with self._API_TYPES for model
#       sessions, with the concrete session implementations calling base class methods
#       to generate the call requests for RPC endpoints and the endpoint instances for
#       streaming channels.

TWebsocket = TypeVar("TWebsocket")


def _format_exc(exc: Exception) -> str:
    exc_type = type(exc)
    exc_name = f"{exc_type.__module__}.{exc_type.__qualname__}"
    exc_msg = str(exc)
    if exc_msg:
        return f"{exc_name}: {exc_msg}"
    return exc_name


class LMStudioWebsocket(Generic[TWebsocket, TQueue]):
    """Common base class for LM Studio websocket clients."""

    # The common websocket API is narrow due to the sync/async split,
    # as only interfaces that don't perform I/O can be shared.

    # Subclasses will declare a specific underlying websocket type
    _ws: TWebsocket | None
    # Subclasses will declare a specific receive queue type
    _mux: MultiplexingManager[TQueue]

    def __init__(
        self,
        ws_url: str,
        auth_details: DictObject,
        log_context: LogEventContext | None = None,
    ) -> None:
        """Initialize I/O independent websocket details."""
        self._ws_url = ws_url
        self._auth_details = auth_details
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, ws_url=ws_url)
        self._mux = MultiplexingManager(logger)
        # Subclasses handle actually creating a websocket instance
        self._ws = None

    @property
    def connected(self) -> bool:
        return self._ws is not None

    def _get_connection_failure_error(
        self, exc: Exception | None = None
    ) -> LMStudioWebsocketError:
        problem = f"LM Studio is not reachable at {self._ws_url}"
        suggestion = "Is LM Studio running?"
        if exc is None:
            err_msg = f"{problem}. {suggestion}"
        else:
            err_msg = f"\n    {problem} (due to {_format_exc(exc)}).\n    {suggestion}"
        return LMStudioWebsocketError(err_msg)

    def _get_auth_failure_error(self, details: Any) -> LMStudioServerError:
        return LMStudioServerError("Authentication failed", details)

    @staticmethod
    def _get_tx_error(message: Any, exc: Exception) -> LMStudioWebsocketError:
        return LMStudioWebsocketError(
            f"Failed to send websocket message ({message}): {_format_exc(exc)}"
        )

    @staticmethod
    def _get_rx_error(exc: Exception) -> LMStudioWebsocketError:
        return LMStudioWebsocketError(
            f"Failure while waiting for websocket message: {_format_exc(exc)}"
        )

    def _fail_if_connected(self, err_msg: str) -> None | NoReturn:
        """Raise exception with given message if websocket is connected."""
        if self._ws is not None:
            raise LMStudioWebsocketError(err_msg)
        return None

    def _ensure_connected(self, usage: str) -> None | NoReturn:
        """Raise exception with given expected usage if websocket is not connected."""
        if self._ws is None:
            err_msg = f"Websocket must be connected to {usage}"
            raise LMStudioWebsocketError(err_msg)
        return None


TLMStudioWebsocket = TypeVar("TLMStudioWebsocket", bound=LMStudioWebsocket[Any, Any])


class ClientBase:
    """Common base class for SDK client interfaces."""

    def __init__(self, api_host: str | None = None) -> None:
        """Initialize API client."""
        self.api_host = api_host if api_host else DEFAULT_API_HOST
        self._auth_details = self._create_auth_message()

    @staticmethod
    def _create_auth_message() -> DictObject:
        """Create an LM Studio websocket authentication message."""
        # Note: authentication (in its current form) is primarily a cooperative
        # resource management mechanism that allows the server to appropriately
        # manage client-scoped resources (such as temporary file handles).
        # As such, the client ID and client passkey are currently more a two part
        # client identifier than they are an adversarial security measure. This is
        # sufficient to prevent accidential conflicts and, in combination with secure
        # websocket support, would be sufficient to ensure that access to the running
        # client was required to extract the auth details.
        client_identifier = str(uuid.uuid4())
        client_passkey = str(uuid.uuid4())
        return {
            "authVersion": 1,
            "clientIdentifier": client_identifier,
            "clientPasskey": client_passkey,
        }


TClient = TypeVar("TClient", bound=ClientBase)


class ClientSession(Generic[TClient, TLMStudioWebsocket]):
    """Common base class for LM Studio client sessions."""

    # The common session API is narrow due to the sync/async split,
    # as only interfaces that don't perform I/O can be shared.

    # Subclasses will declare a specific corresponding client type
    _client: TClient

    # Subclasses will specify which LM Studio API namespace they cover
    API_NAMESPACE: str | None = None

    # Subclasses will declare a specific underlying websocket type
    _lmsws: TLMStudioWebsocket | None

    def __init__(self, client: TClient) -> None:
        """Initialize API client session."""
        self._lmsws = None
        self._client = client

    @property
    def client(self) -> TClient:
        """The client instance that created this session."""
        return self._client

    @property
    def connected(self) -> bool:
        return self._lmsws is not None

    def _fail_if_connected(self, err_msg: str) -> None | NoReturn:
        """Raise given error if websocket is connected."""
        if self._lmsws is not None:
            raise LMStudioWebsocketError(err_msg)
        return None

    def _get_lmsws(self, usage: str) -> TLMStudioWebsocket | NoReturn:
        """Return websocket, raising given error if websocket is not connected."""
        lmsws = self._lmsws
        if lmsws is None:
            err_msg = f"Session must be connected to {usage}"
            raise LMStudioWebsocketError(err_msg)
        return lmsws

    # RPC helpers for formatting request parameters
    def _get_model_search_params(
        self,
        search_term: str | None = None,
        limit: int | None = None,
        compatibility_types: list[ModelCompatibilityType] | None = None,
    ) -> RepositoryRpcSearchModelsParameter:
        if not any([search_term, limit, compatibility_types]):
            raise LMStudioValueError("At least one search parameter must be specified.")
        opts: ModelSearchOptsDict = {}
        if search_term:
            opts["searchTerm"] = search_term
        if limit:
            opts["limit"] = limit
        if compatibility_types:
            opts["compatibilityTypes"] = compatibility_types
        return RepositoryRpcSearchModelsParameter._from_api_dict({"opts": opts})


TSession = TypeVar("TSession", bound=ClientSession[Any, Any])


class SessionData(Generic[TStruct, TSession]):
    """API data linked to a session to allow making further requests."""

    def __init__(
        self, wrapped_cls: Type[TStruct], raw_data: DictObject, session: TSession
    ) -> None:
        self._data = wrapped_cls._from_api_dict(raw_data)
        self._session = session

    @property
    def _repr_fields(self) -> Sequence[str]:
        return self._data.__struct_fields__

    def __repr__(self) -> str:
        data = self._data
        fields = [f"{attr}={getattr(data, attr)!r}" for attr in self._repr_fields]
        return f"{type(self).__name__}({', '.join(fields)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SessionData):
            return NotImplemented
        # To be equal, session data must be for the same session with the same values
        return self._session is other._session and self._data == other._data


class AvailableModelBase(SessionData[ModelSearchResultEntryData, TSession]):
    def __init__(self, search_result: DictObject, session: TSession) -> None:
        super().__init__(ModelSearchResultEntryData, search_result, session)

    @property
    def search_result(self) -> ModelSearchResultEntryData:
        return self._data

    def _get_download_query_params(
        self,
    ) -> RepositoryRpcGetModelDownloadOptionsParameter:
        # Throw a more specific exception than the one thrown by remote_call
        data = self._data
        self._session._get_lmsws(f"retrieve model download options for {data.name!r}")
        return RepositoryRpcGetModelDownloadOptionsParameter(
            model_search_result_identifier=data.identifier
        )


class ModelDownloadOptionBase(
    SessionData[ModelSearchResultDownloadOptionData, TSession]
):
    def __init__(self, download_info: DictObject, session: TSession) -> None:
        super().__init__(ModelSearchResultDownloadOptionData, download_info, session)

    @property
    def _repr_fields(self) -> Sequence[str]:
        # Limit the fields included in the wrapper representation
        # Note: This is NOT statically typechecked!
        return (
            "name",
            "download_identifier",
            "indexed_model_identifier",
            "recommended",
        )

    @property
    def info(self) -> ModelSearchResultDownloadOptionData:
        return self._data

    def _get_download_endpoint(
        self,
        on_progress: DownloadProgressCallback | None = None,
        on_finalize: DownloadFinalizedCallback | None = None,
    ) -> ModelDownloadEndpoint:
        # Throw a more specific exception than the one thrown by remote_call
        data = self._data
        self._session._get_lmsws(f"download {data.name!r}")
        return ModelDownloadEndpoint(data.download_identifier, on_progress, on_finalize)


TModelInfo = TypeVar("TModelInfo", bound=ModelInfo)


class DownloadedModelBase(SessionData[TModelInfo, TSession]):
    """Details of a model downloaded to the LM Studio server instance."""

    @property
    def _repr_fields(self) -> Sequence[str]:
        # Limit the fields included in the wrapper representation
        # Note: This is NOT statically typechecked!
        keys = ["model_key", "display_name", "architecture"]
        if self._data.type == "llm":
            # This should really be defined via the type hierarchy, but the
            # sync/async and embedding/LLM combinations make that painful
            keys.append("vision")
        return keys

    @property
    def info(self) -> TModelInfo:
        return self._data

    @property
    def type(self) -> str:
        return self._data.type

    @property
    def path(self) -> str:
        return self._data.path

    @property
    def model_key(self) -> str:
        return self._data.model_key


class ModelHandleBase(Generic[TSession]):
    """Client handle for a loaded model instance in the LM Studio server instance."""

    def __init__(self, model_identifier: str, session: TSession) -> None:
        """Initialize the LM Studio model reference."""
        self.identifier = model_identifier
        self._session = session
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(model_identifier=model_identifier)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(identifier={self.identifier!r})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ModelHandleBase):
            return NotImplemented
        # To be equal, handle must be for the same session with the same model ID
        return self._session is other._session and self.identifier == other.identifier


_MODEL_NAMESPACES = set(("llm", "embedding"))


def check_model_namespace(namespace: str | None) -> str | None:
    if namespace is None:
        return None
    if namespace not in _MODEL_NAMESPACES:
        raise LMStudioValueError(f"Unknown model namespace: {namespace!r}")
    return namespace
