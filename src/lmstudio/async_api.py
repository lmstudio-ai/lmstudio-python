"""Async I/O protocol implementation for the LM Studio remote access API."""

import asyncio
import itertools
import time

from abc import abstractmethod
from contextlib import AsyncExitStack, asynccontextmanager
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    Sequence,
    Type,
    TypeAlias,
    TypeVar,
)
from typing_extensions import (
    # Native in 3.11+
    Self,
    # Native in 3.13+
    TypeIs,
)

import httpx

from httpx_ws import AsyncWebSocketSession

from .sdk_api import (
    LMStudioRuntimeError,
    LMStudioValueError,
    sdk_callback_invocation,
    sdk_public_api,
    sdk_public_api_async,
)
from .schemas import AnyLMStudioStruct, DictObject
from .history import (
    AssistantResponse,
    Chat,
    ChatHistoryDataDict,
    FileHandle,
    LocalFileInput,
    _LocalFileData,
    ToolCallResultData,
    ToolCallRequest,
    ToolResultMessage,
)
from .json_api import (
    ActResult,
    AnyLoadConfig,
    AnyModelSpecifier,
    AsyncToolCall,
    AvailableModelBase,
    ChannelEndpoint,
    ChannelHandler,
    ChatResponseEndpoint,
    ClientBase,
    ClientSession,
    CompletionEndpoint,
    DEFAULT_TTL,
    DownloadedModelBase,
    DownloadFinalizedCallback,
    DownloadProgressCallback,
    EmbeddingLoadModelConfig,
    EmbeddingLoadModelConfigDict,
    EmbeddingModelInfo,
    GetOrLoadEndpoint,
    LlmInfo,
    LlmLoadModelConfig,
    LlmLoadModelConfigDict,
    LlmPredictionConfig,
    LlmPredictionConfigDict,
    LlmPredictionFragment,
    LMStudioCancelledError,
    LMStudioClientError,
    LMStudioPredictionError,
    LMStudioWebsocket,
    LMStudioWebsocketError,
    LoadModelEndpoint,
    ModelDownloadOptionBase,
    ModelHandleBase,
    ModelInstanceInfo,
    ModelLoadingCallback,
    ModelSessionTypes,
    ModelTypesEmbedding,
    ModelTypesLlm,
    PredictionStreamBase,
    PredictionEndpoint,
    PredictionFirstTokenCallback,
    PredictionFragmentCallback,
    PredictionFragmentEvent,
    PredictionMessageCallback,
    PredictionResult,
    PredictionRoundResult,
    PredictionRxEvent,
    PredictionToolCallEvent,
    PromptProcessingCallback,
    RemoteCallHandler,
    ResponseSchema,
    SendMessageAsync,
    TModelInfo,
    ToolDefinition,
    check_model_namespace,
    load_struct,
    _model_spec_to_api_dict,
    _redact_json,
)
from ._kv_config import TLoadConfig, TLoadConfigDict, parse_server_config
from ._sdk_models import (
    EmbeddingRpcCountTokensParameter,
    EmbeddingRpcEmbedStringParameter,
    EmbeddingRpcTokenizeParameter,
    LlmApplyPromptTemplateOpts,
    LlmApplyPromptTemplateOptsDict,
    LlmRpcApplyPromptTemplateParameter,
    ModelCompatibilityType,
)
from ._ws_impl import AsyncTaskManager, AsyncWebsocketHandler

from ._logging import new_logger, LogEventContext

# Only the async API itself is published from
# this module. Anything needed for type hints
# and similar tasks is published from `json_api`.
# Bypassing the high level API, and working more
# directly with the underlying websocket(s) is
# not supported due to the complexity of the task
# management details (hence the private names).
__all__ = [
    "AnyAsyncDownloadedModel",
    "AsyncClient",
    "AsyncDownloadedEmbeddingModel",
    "AsyncDownloadedLlm",
    "AsyncEmbeddingModel",
    "AsyncLLM",
    "AsyncPredictionStream",
]


T = TypeVar("T")


class AsyncChannel(Generic[T]):
    """Communication subchannel over multiplexed async websocket."""

    def __init__(
        self,
        channel_id: int,
        get_message: Callable[[], Awaitable[Any]],
        endpoint: ChannelEndpoint[T, Any, Any],
        send_json: SendMessageAsync,
        log_context: LogEventContext,
    ) -> None:
        """Initialize asynchronous websocket streaming channel."""
        self._is_finished = False
        self._get_message = get_message
        self._api_channel = ChannelHandler(channel_id, endpoint, log_context)
        self._send_json = send_json

    def get_creation_message(self) -> DictObject:
        """Get the message to send to create this channel."""
        return self._api_channel.get_creation_message()

    async def send_message(self, message: DictObject) -> None:
        """Send given message on this channel."""
        wrapped_message = self._api_channel.wrap_message(message)
        await self._send_json(wrapped_message)

    async def cancel(self) -> None:
        """Cancel the channel."""
        if self._is_finished:
            return
        cancel_message = self._api_channel.get_cancel_message()
        await self._send_json(cancel_message)

    async def rx_stream(
        self,
    ) -> AsyncIterator[DictObject | None]:
        """Stream received channel messages until channel is closed by server."""
        while not self._is_finished:
            with sdk_public_api():
                # Avoid emitting tracebacks that delve into supporting libraries
                # (we can't easily suppress the SDK's own frames for iterators)
                message = await self._get_message()
                if message is None:
                    raise LMStudioWebsocketError("Client unexpectedly disconnected.")
                contents = self._api_channel.handle_rx_message(message)
            if contents is None:
                self._is_finished = True
                break
            yield contents

    async def wait_for_result(self) -> T:
        """Wait for the channel to finish and return the result."""
        endpoint = self._api_channel.endpoint
        async for contents in self.rx_stream():
            endpoint.handle_message_events(contents)
            if endpoint.is_finished:
                break
        return endpoint.result()


class AsyncRemoteCall:
    """Remote procedure call over multiplexed async websocket."""

    def __init__(
        self,
        call_id: int,
        get_message: Callable[[], Awaitable[Any]],
        log_context: LogEventContext,
        notice_prefix: str = "RPC",
    ) -> None:
        """Initialize asynchronous remote procedure call."""
        self._get_message = get_message
        self._rpc = RemoteCallHandler(call_id, log_context, notice_prefix)
        self._logger = logger = new_logger(type(self).__name__)
        logger.update_context(log_context, call_id=call_id)

    def get_rpc_message(
        self, endpoint: str, params: AnyLMStudioStruct | None
    ) -> DictObject:
        """Get the message to send to initiate this remote procedure call."""
        return self._rpc.get_rpc_message(endpoint, params)

    async def receive_result(self) -> Any:
        """Receive call response on the receive queue."""
        message = await self._get_message()
        if message is None:
            raise LMStudioWebsocketError("Client unexpectedly disconnected.")
        return self._rpc.handle_rx_message(message)


class _AsyncLMStudioWebsocket(LMStudioWebsocket[AsyncWebSocketSession]):
    """Asynchronous websocket client that handles demultiplexing of reply messages."""

    def __init__(
        self,
        task_manager: AsyncTaskManager,
        ws_url: str,
        auth_details: DictObject,
        log_context: LogEventContext | None = None,
    ) -> None:
        """Initialize asynchronous websocket client."""
        super().__init__(ws_url, auth_details, log_context)
        self._ws_handler = AsyncWebsocketHandler(
            task_manager, ws_url, auth_details, log_context
        )

    @property
    def _httpx_ws(self) -> AsyncWebSocketSession | None:
        # Underlying HTTPX session is accessible for testing purposes
        return self._ws

    async def __aenter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        if self._ws is None:
            await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()

    async def connect(self) -> Self:
        """Connect to and authenticate with the LM Studio API."""
        self._fail_if_connected("Attempted to connect already connected websocket")
        self._logger.info("Connecting websocket session")
        ws_handler = self._ws_handler
        if not await self._ws_handler.connect():
            if ws_handler._connection_failure is not None:
                raise self._get_connection_failure_error(ws_handler._connection_failure)
            if ws_handler._auth_failure is not None:
                raise self._get_auth_failure_error(ws_handler._auth_failure)
            self._logger.error("Connection failed, but no failure reason reported.")
            raise self._get_connection_failure_error()
        self._ws = ws_handler._ws
        return self

    async def disconnect(self) -> None:
        """Drop the LM Studio API connection."""
        self._ws = None
        await self._ws_handler.disconnect()
        self._logger.info("Websocket session disconnected")

    aclose = disconnect

    async def _send_json(self, message: DictObject) -> None:
        # Callers are expected to call `_ensure_connected` before this method
        await self._ws_handler.send_json(message)

    async def _connect_to_endpoint(self, channel: AsyncChannel[Any]) -> None:
        """Connect channel to specified endpoint."""
        self._ensure_connected("open channel endpoints")
        create_message = channel.get_creation_message()
        self._logger.debug("Connecting channel endpoint", json=create_message)
        await self._send_json(create_message)

    @asynccontextmanager
    async def open_channel(
        self,
        endpoint: ChannelEndpoint[T, Any, Any],
    ) -> AsyncGenerator[AsyncChannel[T], None]:
        """Open a streaming channel over the websocket."""
        with self._ws_handler.open_channel() as (channel_id, getter):
            channel = AsyncChannel(
                channel_id,
                getter,
                endpoint,
                self._send_json,
                self._logger.event_context,
            )
            await self._connect_to_endpoint(channel)
            yield channel

    async def _send_call(
        self,
        rpc: AsyncRemoteCall,
        endpoint: str,
        params: AnyLMStudioStruct | None = None,
    ) -> None:
        """Initiate remote call to specified endpoint."""
        self._ensure_connected("send remote procedure call")
        call_message = rpc.get_rpc_message(endpoint, params)
        # TODO: Improve logging for large requests (such as file uploads)
        #       without requiring explicit special casing here
        logged_message: DictObject
        if call_message.get("endpoint") == "uploadFileBase64":
            logged_message = _redact_json(call_message)
        else:
            logged_message = call_message
        self._logger.debug("Sending RPC request", json=logged_message)
        await self._send_json(call_message)

    async def remote_call(
        self,
        endpoint: str,
        params: AnyLMStudioStruct | None,
        notice_prefix: str = "RPC",
    ) -> Any:
        """Make a remote procedure call over the websocket."""
        with self._ws_handler.start_call() as (call_id, getter):
            rpc = AsyncRemoteCall(
                call_id, getter, self._logger.event_context, notice_prefix
            )
            await self._send_call(rpc, endpoint, params)
            return await rpc.receive_result()


class _AsyncSession(ClientSession["AsyncClient", _AsyncLMStudioWebsocket]):
    """Async client session interfaces applicable to all API namespaces."""

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize asynchronous API client session."""
        super().__init__(client)
        self._resource_manager = AsyncExitStack()

    async def _ensure_connected(self) -> None:
        # Allow lazy connection of the session websocket
        if self._lmsws is None:
            await self.connect()

    async def __aenter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        await self._ensure_connected()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()

    @sdk_public_api_async()
    async def connect(self) -> _AsyncLMStudioWebsocket:
        """Connect the client session."""
        self._fail_if_connected("Attempted to connect already connected session")
        api_host = self._client.api_host
        namespace = self.API_NAMESPACE
        if namespace is None:
            raise LMStudioClientError(
                f"No API namespace defined for {type(self).__name__}"
            )
        session_url = f"ws://{api_host}/{namespace}"
        resources = self._resource_manager
        client = self._client
        self._lmsws = lmsws = await resources.enter_async_context(
            _AsyncLMStudioWebsocket(
                client._task_manager, session_url, client._auth_details
            )
        )
        return lmsws

    @sdk_public_api_async()
    async def disconnect(self) -> None:
        """Disconnect the client session."""
        self._lmsws = None
        await self._resource_manager.aclose()

    aclose = disconnect

    # Unlike the sync API, the async API does NOT implicitly
    # connect the websocket (if necessary) when sending requests
    # Doing so would violate principles of structured concurrency,
    # since the websocket creation spawns additional background
    # tasks for ping, keepalive, and demultiplexing management
    # Instead, the client creates all connections when opened

    @asynccontextmanager
    async def _create_channel(
        self,
        endpoint: ChannelEndpoint[T, Any, Any],
    ) -> AsyncGenerator[AsyncChannel[T], None]:
        """Connect a channel to an LM Studio streaming endpoint."""
        lmsws = self._get_lmsws("create channels")
        async with lmsws.open_channel(endpoint) as channel:
            yield channel

    @sdk_public_api_async()
    async def remote_call(
        self,
        endpoint: str,
        params: AnyLMStudioStruct | None = None,
        notice_prefix: str = "RPC",
    ) -> Any:
        """Send a remote call to the given RPC endpoint and wait for the result."""
        lmsws = self._get_lmsws("make remote calls")
        return await lmsws.remote_call(endpoint, params, notice_prefix)


TAsyncSessionModel = TypeVar(
    "TAsyncSessionModel", bound="_AsyncSessionModel[Any, Any, Any, Any]"
)
TAsyncModelHandle = TypeVar("TAsyncModelHandle", bound="AsyncModelHandle[Any]")


class AsyncDownloadedModel(
    Generic[
        TModelInfo,
        TAsyncSessionModel,
        TLoadConfig,
        TLoadConfigDict,
        TAsyncModelHandle,
    ],
    DownloadedModelBase[TModelInfo, TAsyncSessionModel],
):
    @sdk_public_api_async()
    async def load_new_instance(
        self,
        *,
        ttl: int | None = DEFAULT_TTL,
        instance_identifier: str | None = None,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TAsyncModelHandle:
        """Load this model with the given identifier and configuration.

        Note: details of configuration fields may change in SDK feature releases.
        """
        handle: TAsyncModelHandle = await self._session._load_new_instance(
            self.model_key, instance_identifier, ttl, config, on_load_progress
        )
        return handle

    @sdk_public_api_async()
    async def model(
        self,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TAsyncModelHandle:
        """Retrieve model with given identifier, or load it with given configuration.

        Note: configuration of retrieved model is NOT checked against the given config.
        Note: details of configuration fields may change in SDK feature releases.
        """
        # Call _get_or_load directly, since we have a model identifier
        handle: TAsyncModelHandle = await self._session._get_or_load(
            self.model_key, ttl, config, on_load_progress
        )
        return handle


class AsyncDownloadedEmbeddingModel(
    AsyncDownloadedModel[
        EmbeddingModelInfo,
        "_AsyncSessionEmbedding",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        "AsyncEmbeddingModel",
    ],
):
    """Asynchronous download listing for an embedding model."""

    def __init__(
        self, model_info: DictObject, session: "_AsyncSessionEmbedding"
    ) -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(EmbeddingModelInfo, model_info, session)


class AsyncDownloadedLlm(
    AsyncDownloadedModel[
        LlmInfo,
        "_AsyncSessionLlm",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        "AsyncLLM",
    ]
):
    """Asynchronous ownload listing for an LLM."""

    def __init__(self, model_info: DictObject, session: "_AsyncSessionLlm") -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(LlmInfo, model_info, session)


AnyAsyncDownloadedModel: TypeAlias = AsyncDownloadedModel[Any, Any, Any, Any, Any]


class _AsyncSessionSystem(_AsyncSession):
    """Async client session for the system namespace."""

    API_NAMESPACE = "system"

    @sdk_public_api_async()
    async def list_downloaded_models(self) -> Sequence[AnyAsyncDownloadedModel]:
        """Get the list of all downloaded models that are available for loading."""
        # The list of downloaded models is only available via the system API namespace
        models = await self.remote_call("listDownloadedModels")
        return [self._process_download_listing(m) for m in models]

    def _process_download_listing(
        self, model_info: DictObject
    ) -> AnyAsyncDownloadedModel:
        model_type = model_info.get("type")
        if model_type is None:
            raise LMStudioClientError(
                f"No 'type' field in download listing: {model_info}"
            )
        match model_type:
            case "embedding":
                return AsyncDownloadedEmbeddingModel(model_info, self._client.embedding)
            case "llm":
                return AsyncDownloadedLlm(model_info, self._client.llm)
        raise LMStudioClientError(
            f"Unknown model type {model_type!r} in download listing: {model_info}"
        )


class _AsyncSessionFiles(_AsyncSession):
    """Async client session for the files namespace."""

    API_NAMESPACE = "files"

    async def _fetch_file_handle(self, file_data: _LocalFileData) -> FileHandle:
        handle = await self.remote_call("uploadFileBase64", file_data._as_fetch_param())
        # Returned dict provides the handle identifier, file type, and size in bytes
        # Add the extra fields needed for a FileHandle (aka ChatMessagePartFileData)
        handle["name"] = file_data.name
        handle["type"] = "file"
        return load_struct(handle, FileHandle)

    # Not yet implemented (server API only supports the same file types as prepare_image)
    # @sdk_public_api_async()
    async def _prepare_file(
        self, src: LocalFileInput, name: str | None = None
    ) -> FileHandle:
        """Add a file to the server. Returns a file handle for use in prediction requests."""
        file_data = _LocalFileData(src, name)
        return await self._fetch_file_handle(file_data)

    @sdk_public_api_async()
    async def prepare_image(
        self, src: LocalFileInput, name: str | None = None
    ) -> FileHandle:
        """Add an image to the server. Returns a file handle for use in prediction requests."""
        file_data = _LocalFileData(src, name)
        return await self._fetch_file_handle(file_data)


class AsyncModelDownloadOption(ModelDownloadOptionBase[_AsyncSession]):
    """A single download option for a model search result."""

    @sdk_public_api_async()
    async def download(
        self,
        on_progress: DownloadProgressCallback | None = None,
        on_finalize: DownloadFinalizedCallback | None = None,
    ) -> str:
        """Download a model and get its path for loading."""
        endpoint = self._get_download_endpoint(on_progress, on_finalize)
        async with self._session._create_channel(endpoint) as channel:
            return await channel.wait_for_result()


class AsyncAvailableModel(AvailableModelBase[_AsyncSession]):
    """A model available for download from the model repository."""

    _session: _AsyncSession

    @sdk_public_api_async()
    async def get_download_options(
        self,
    ) -> Sequence[AsyncModelDownloadOption]:
        """Get the download options for the specified model."""
        params = self._get_download_query_params()
        options = await self._session.remote_call("getModelDownloadOptions", params)
        final = []
        for m in options["results"]:
            final.append(AsyncModelDownloadOption(m, self._session))
        return final


class _AsyncSessionRepository(_AsyncSession):
    """Async client session for the repository namespace."""

    API_NAMESPACE = "repository"

    @sdk_public_api_async()
    async def search_models(
        self,
        search_term: str | None = None,
        limit: int | None = None,
        compatibility_types: list[ModelCompatibilityType] | None = None,
    ) -> Sequence[AsyncAvailableModel]:
        """Search for downloadable models satisfying a search query."""
        params = self._get_model_search_params(search_term, limit, compatibility_types)
        models = await self.remote_call("searchModels", params)
        return [AsyncAvailableModel(m, self) for m in models["results"]]


TAsyncDownloadedModel = TypeVar("TAsyncDownloadedModel", bound=AnyAsyncDownloadedModel)


class _AsyncSessionModel(
    _AsyncSession,
    Generic[
        TAsyncModelHandle,
        TLoadConfig,
        TLoadConfigDict,
        TAsyncDownloadedModel,
    ],
):
    """Async client session for a model (LLM/embedding) namespace."""

    _API_TYPES: Type[ModelSessionTypes[TLoadConfig]]

    @property
    def _system_session(self) -> _AsyncSessionSystem:
        return self._client.system

    @property
    def _files_session(self) -> _AsyncSessionFiles:
        return self._client.files

    async def _get_load_config(
        self, model_specifier: AnyModelSpecifier
    ) -> AnyLoadConfig:
        """Get the model load config for the specified model."""
        # Note that the configuration reported here uses the *server* config names,
        # not the attributes used to set the configuration in the client SDK
        params = self._API_TYPES.REQUEST_LOAD_CONFIG._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
            }
        )
        config = await self.remote_call("getLoadConfig", params)
        result_type = self._API_TYPES.MODEL_LOAD_CONFIG
        return result_type._from_any_api_dict(parse_server_config(config))

    async def _get_api_model_info(self, model_specifier: AnyModelSpecifier) -> Any:
        """Get the raw model info (if any) for a model matching the given criteria."""
        params = self._API_TYPES.REQUEST_MODEL_INFO._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "throwIfNotFound": True,
            }
        )
        return await self.remote_call("getModelInfo", params)

    @sdk_public_api_async()
    async def get_model_info(
        self, model_specifier: AnyModelSpecifier
    ) -> ModelInstanceInfo:
        """Get the model info (if any) for a model matching the given criteria."""
        response = await self._get_api_model_info(model_specifier)
        model_info = self._API_TYPES.MODEL_INSTANCE_INFO._from_any_api_dict(response)
        return model_info

    async def _get_context_length(self, model_specifier: AnyModelSpecifier) -> int:
        """Get the context length of the specified model."""
        raw_model_info = await self._get_api_model_info(model_specifier)
        return int(raw_model_info.get("contextLength", -1))

    async def _count_tokens(
        self, model_specifier: AnyModelSpecifier, input: str
    ) -> int:
        params = EmbeddingRpcCountTokensParameter._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "inputString": input,
            }
        )
        response = await self.remote_call("countTokens", params)
        return int(response["tokenCount"])

    # Private helper method to allow the main API to easily accept iterables
    async def _tokenize_text(
        self, model_specifier: AnyModelSpecifier, input: str
    ) -> Sequence[int]:
        params = EmbeddingRpcTokenizeParameter._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "inputString": input,
            }
        )
        response = await self.remote_call("tokenize", params)
        return response.get("tokens", []) if response else []

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    async def _tokenize(
        self, model_specifier: AnyModelSpecifier, input: str | Iterable[str]
    ) -> Sequence[int] | Sequence[Sequence[int]]:
        """Tokenize the input string(s) using the specified model."""
        if isinstance(input, str):
            return await self._tokenize_text(model_specifier, input)
        return await asyncio.gather(
            *[self._tokenize_text(model_specifier, s) for s in input]
        )

    @abstractmethod
    def _create_handle(self, model_identifier: str) -> TAsyncModelHandle:
        """Get a symbolic handle to the specified model."""
        ...

    @sdk_public_api_async()
    async def model(
        self,
        model_key: str | None = None,
        /,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TAsyncModelHandle:
        """Get a handle to the specified model (loading it if necessary).

        Note: configuration of retrieved model is NOT checked against the given config.
        Note: details of configuration fields may change in SDK feature releases.
        """
        if model_key is None:
            # Should this raise an error if a config is supplied?
            return await self._get_any()
        return await self._get_or_load(model_key, ttl, config, on_load_progress)

    @sdk_public_api_async()
    async def list_loaded(self) -> Sequence[TAsyncModelHandle]:
        """Get the list of currently loaded models."""
        models = await self.remote_call("listLoaded")
        return [self._create_handle(m["identifier"]) for m in models]

    @sdk_public_api_async()
    async def unload(self, model_identifier: str) -> None:
        """Unload the specified model."""
        params = self._API_TYPES.REQUEST_UNLOAD(identifier=model_identifier)
        await self.remote_call("unloadModel", params)

    # N.B. Canceling a load from the UI doesn't update the load process for a while.
    # Fortunately, this is not our fault. The server just delays in broadcasting it.
    @sdk_public_api_async()
    async def load_new_instance(
        self,
        model_key: str,
        instance_identifier: str | None = None,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TAsyncModelHandle:
        """Load the specified model with the given identifier and configuration.

        Note: details of configuration fields may change in SDK feature releases.
        """
        return await self._load_new_instance(
            model_key, instance_identifier, ttl, config, on_load_progress
        )

    async def _load_new_instance(
        self,
        model_key: str,
        instance_identifier: str | None,
        ttl: int | None,
        config: TLoadConfig | TLoadConfigDict | None,
        on_load_progress: ModelLoadingCallback | None,
    ) -> TAsyncModelHandle:
        channel_type = self._API_TYPES.REQUEST_NEW_INSTANCE
        config_type: type[TLoadConfig] = self._API_TYPES.MODEL_LOAD_CONFIG
        endpoint = LoadModelEndpoint(
            model_key,
            instance_identifier,
            ttl,
            channel_type,
            config_type,
            config,
            on_load_progress,
        )
        async with self._create_channel(endpoint) as channel:
            result = await channel.wait_for_result()
            return self._create_handle(result.identifier)

    async def _get_or_load(
        self,
        model_key: str,
        ttl: int | None,
        config: TLoadConfig | TLoadConfigDict | None,
        on_load_progress: ModelLoadingCallback | None,
    ) -> TAsyncModelHandle:
        """Load the specified model with the given identifier and configuration."""
        channel_type = self._API_TYPES.REQUEST_GET_OR_LOAD
        config_type = self._API_TYPES.MODEL_LOAD_CONFIG
        endpoint = GetOrLoadEndpoint(
            model_key, ttl, channel_type, config_type, config, on_load_progress
        )
        async with self._create_channel(endpoint) as channel:
            result = await channel.wait_for_result()
            return self._create_handle(result.identifier)

    async def _get_any(self) -> TAsyncModelHandle:
        """Get a handle to any loaded model."""
        loaded_models = await self.list_loaded()
        if not loaded_models:
            raise LMStudioClientError(
                f"Could not get_any for namespace {self.API_NAMESPACE}: No models are currently loaded."
            )
        return self._create_handle(loaded_models[0].identifier)

    @classmethod
    def _is_relevant_model(
        cls, model: AnyAsyncDownloadedModel
    ) -> TypeIs[TAsyncDownloadedModel]:
        return bool(model.type == cls.API_NAMESPACE)

    @sdk_public_api_async()
    async def list_downloaded(self) -> Sequence[TAsyncDownloadedModel]:
        """Get the list of currently downloaded models that are available for loading."""
        models = await self._system_session.list_downloaded_models()
        return [m for m in models if self._is_relevant_model(m)]

    async def _fetch_file_handle(self, file_data: _LocalFileData) -> FileHandle:
        return await self._files_session._fetch_file_handle(file_data)


AsyncPredictionChannel: TypeAlias = AsyncChannel[PredictionResult]
AsyncPredictionCM: TypeAlias = AsyncContextManager[AsyncPredictionChannel]


class AsyncPredictionStream(PredictionStreamBase):
    """Async context manager for an ongoing prediction process."""

    def __init__(
        self,
        channel_cm: AsyncPredictionCM,
        endpoint: PredictionEndpoint,
    ) -> None:
        """Initialize a prediction process representation."""
        self._resource_manager = AsyncExitStack()
        self._channel_cm: AsyncPredictionCM = channel_cm
        self._channel: AsyncPredictionChannel | None = None
        super().__init__(endpoint)

    @sdk_public_api_async()
    async def start(self) -> None:
        """Send the prediction request."""
        if self._is_finished:
            raise LMStudioRuntimeError("Prediction result has already been received.")
        if self._is_started:
            raise LMStudioRuntimeError("Prediction request has already been sent.")
        # The given channel context manager is set up to send the relevant request
        self._channel = await self._resource_manager.enter_async_context(
            self._channel_cm
        )
        self._mark_started()

    @sdk_public_api_async()
    async def aclose(self) -> None:
        """Terminate the prediction processing (if not already terminated)."""
        # Cancel the prediction (if unfinished) and release acquired resources
        if self._is_started and not self._is_finished:
            self._set_error(
                LMStudioCancelledError(
                    "Prediction cancelled unexpectedly: please use .cancel()"
                )
            )
        self._channel = None
        await self._resource_manager.aclose()

    async def __aenter__(self) -> Self:
        if self._channel is None:
            await self.start()
        return self

    async def __aexit__(
        self,
        _exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        if exc_val and not self._is_finished:
            self._set_error(exc_val)
        await self.aclose()

    async def __aiter__(self) -> AsyncIterator[LlmPredictionFragment]:
        async for event in self._iter_events():
            if isinstance(event, PredictionFragmentEvent):
                yield event.arg

    async def _iter_events(self) -> AsyncIterator[PredictionRxEvent]:
        endpoint = self._endpoint
        async with self:
            assert self._channel is not None
            async for contents in self._channel.rx_stream():
                for event in endpoint.iter_message_events(contents):
                    endpoint.handle_rx_event(event)
                    yield event
                if endpoint.is_finished:
                    break
            self._mark_finished()

    @sdk_public_api_async()
    async def wait_for_result(self) -> PredictionResult:
        """Wait for the result of the prediction."""
        async for _ in self:
            pass
        return self.result()

    @sdk_public_api_async()
    async def cancel(self) -> None:
        """Cancel the prediction process."""
        if not self._is_finished and self._channel:
            self._mark_cancelled()
            await self._channel.cancel()


class _AsyncSessionLlm(
    _AsyncSessionModel[
        "AsyncLLM",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        AsyncDownloadedLlm,
    ]
):
    """Async client session for LLM namespace."""

    API_NAMESPACE = "llm"
    _API_TYPES = ModelTypesLlm

    def _create_handle(self, model_identifier: str) -> "AsyncLLM":
        """Create a symbolic handle to the specified LLM model."""
        return AsyncLLM(model_identifier, self)

    async def _complete_stream(
        self,
        model_specifier: AnyModelSpecifier,
        prompt: str,
        *,
        response_format: ResponseSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream:
        """Request a one-off prediction without any context and stream the generated tokens.

        Note: details of configuration fields may change in SDK feature releases.
        """
        endpoint = CompletionEndpoint(
            model_specifier,
            prompt,
            response_format,
            config,
            preset,
            on_message,
            on_first_token,
            on_prediction_fragment,
            on_prompt_processing_progress,
        )
        channel_cm = self._create_channel(endpoint)
        prediction_stream = AsyncPredictionStream(channel_cm, endpoint)
        return prediction_stream

    async def _respond_stream(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: ResponseSchema | None = None,
        on_message: PredictionMessageCallback | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream:
        """Request a response in an ongoing assistant chat session and stream the generated tokens.

        Note: details of configuration fields may change in SDK feature releases.
        """
        if not isinstance(history, Chat):
            history = Chat.from_history(history)
        endpoint = ChatResponseEndpoint(
            model_specifier,
            history,
            response_format,
            config,
            preset,
            on_message,
            on_first_token,
            on_prediction_fragment,
            on_prompt_processing_progress,
        )
        channel_cm = self._create_channel(endpoint)
        prediction_stream = AsyncPredictionStream(channel_cm, endpoint)
        return prediction_stream

    async def _apply_prompt_template(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        opts: LlmApplyPromptTemplateOpts | LlmApplyPromptTemplateOptsDict = {},
    ) -> str:
        """Apply a prompt template to the given history."""
        if not isinstance(history, Chat):
            history = Chat.from_history(history)
        if not isinstance(opts, LlmApplyPromptTemplateOpts):
            opts = LlmApplyPromptTemplateOpts.from_dict(opts)
        params = LlmRpcApplyPromptTemplateParameter._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "history": history._get_history_for_prediction(),
                "predictionConfigStack": {"layers": []},
                "opts": opts.to_dict(),
            }
        )
        response = await self.remote_call("applyPromptTemplate", params)
        return response.get("formatted", "") if response else ""


class _AsyncSessionEmbedding(
    _AsyncSessionModel[
        "AsyncEmbeddingModel",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        AsyncDownloadedEmbeddingModel,
    ]
):
    """Async client session for embedding namespace."""

    API_NAMESPACE = "embedding"
    _API_TYPES = ModelTypesEmbedding

    def _create_handle(self, model_identifier: str) -> "AsyncEmbeddingModel":
        """Create a symbolic handle to the specified embedding model."""
        return AsyncEmbeddingModel(model_identifier, self)

    # Private helper method to allow the main API to easily accept iterables
    async def _embed_text(
        self, model_specifier: AnyModelSpecifier, input: str
    ) -> Sequence[float]:
        params = EmbeddingRpcEmbedStringParameter._from_api_dict(
            {
                "modelSpecifier": _model_spec_to_api_dict(model_specifier),
                "inputString": input,
            }
        )

        response = await self.remote_call("embedString", params)
        return response.get("embedding", []) if response else []

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    async def _embed(
        self, model_specifier: AnyModelSpecifier, input: str | Iterable[str]
    ) -> Sequence[float] | Sequence[Sequence[float]]:
        """Request embedding vectors for the given input string(s)."""
        if isinstance(input, str):
            return await self._embed_text(model_specifier, input)
        return await asyncio.gather(
            *[self._embed_text(model_specifier, s) for s in input]
        )


class AsyncModelHandle(
    Generic[TAsyncSessionModel], ModelHandleBase[TAsyncSessionModel]
):
    """Reference to a loaded LM Studio model."""

    @sdk_public_api_async()
    async def unload(self) -> None:
        """Unload this model."""
        await self._session.unload(self.identifier)

    @sdk_public_api_async()
    async def get_info(self) -> ModelInstanceInfo:
        """Get the model info for this model."""
        return await self._session.get_model_info(self.identifier)

    @sdk_public_api_async()
    async def get_load_config(self) -> AnyLoadConfig:
        """Get the model load config for this model."""
        return await self._session._get_load_config(self.identifier)

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    @sdk_public_api_async()
    async def tokenize(
        self, input: str | Iterable[str]
    ) -> Sequence[int] | Sequence[Sequence[int]]:
        """Tokenize the input string(s) using this model."""
        return await self._session._tokenize(self.identifier, input)

    @sdk_public_api_async()
    async def count_tokens(self, input: str) -> int:
        """Report the number of tokens needed for the input string using this model."""
        return await self._session._count_tokens(self.identifier, input)

    @sdk_public_api_async()
    async def get_context_length(self) -> int:
        """Get the context length of this model."""
        return await self._session._get_context_length(self.identifier)


AnyAsyncModel: TypeAlias = AsyncModelHandle[Any]


class AsyncLLM(AsyncModelHandle[_AsyncSessionLlm]):
    """Reference to a loaded LLM model."""

    @sdk_public_api_async()
    async def complete_stream(
        self,
        prompt: str,
        *,
        response_format: ResponseSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream:
        """Request a one-off prediction without any context and stream the generated tokens.

        Note: details of configuration fields may change in SDK feature releases.
        """
        return await self._session._complete_stream(
            self.identifier,
            prompt,
            response_format=response_format,
            config=config,
            preset=preset,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )

    @sdk_public_api_async()
    async def complete(
        self,
        prompt: str,
        *,
        response_format: ResponseSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionResult:
        """Request a one-off prediction without any context.

        Note: details of configuration fields may change in SDK feature releases.
        """
        prediction_stream = await self._session._complete_stream(
            self.identifier,
            prompt,
            response_format=response_format,
            config=config,
            preset=preset,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )
        async for _ in prediction_stream:
            # No yield in body means iterator reliably provides
            # prompt resource cleanup on coroutine cancellation
            pass
        return prediction_stream.result()

    @sdk_public_api_async()
    async def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: ResponseSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream:
        """Request a response in an ongoing assistant chat session and stream the generated tokens.

        Note: details of configuration fields may change in SDK feature releases.
        """
        return await self._session._respond_stream(
            self.identifier,
            history,
            response_format=response_format,
            config=config,
            preset=preset,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )

    @sdk_public_api_async()
    async def respond(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: ResponseSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionResult:
        """Request a response in an ongoing assistant chat session.

        Note: details of configuration fields may change in SDK feature releases.
        """
        prediction_stream = await self._session._respond_stream(
            self.identifier,
            history,
            response_format=response_format,
            config=config,
            preset=preset,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )
        async for _ in prediction_stream:
            # No yield in body means iterator reliably provides
            # prompt resource cleanup on coroutine cancellation
            pass
        return prediction_stream.result()

    # TODO: Improve code sharing between sync and async multi-round predictions
    # TODO: Accept async tools in the tools iterable
    @sdk_public_api_async()
    async def act(
        self,
        chat: Chat | ChatHistoryDataDict | str,
        tools: Iterable[ToolDefinition],
        *,
        max_prediction_rounds: int | None = None,
        max_parallel_tool_calls: int | None = 1,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        preset: str | None = None,
        on_message: Callable[[AssistantResponse | ToolResultMessage], Any]
        | None = None,
        on_first_token: Callable[[int], Any] | None = None,
        on_prediction_fragment: Callable[[LlmPredictionFragment, int], Any]
        | None = None,
        on_round_start: Callable[[int], Any] | None = None,
        on_round_end: Callable[[int], Any] | None = None,
        on_prediction_completed: Callable[[PredictionRoundResult], Any] | None = None,
        on_prompt_processing_progress: Callable[[float, int], Any] | None = None,
        handle_invalid_tool_request: Callable[
            [LMStudioPredictionError, ToolCallRequest | None], str | None
        ]
        | None = None,
    ) -> ActResult:
        """Request a response (with implicit tool use) in an ongoing agent chat session.

        Note: details of configuration fields may change in SDK feature releases.
        """
        start_time = time.perf_counter()
        # It is not yet possible to combine tool calling with requests for structured responses
        response_format = None
        agent_chat: Chat = Chat.from_history(chat)
        del chat  # Avoid any further access to the input chat history
        # Multiple rounds, until all tool calls are resolved or limit is reached
        round_counter: Iterable[int]
        if max_prediction_rounds is not None:
            if max_prediction_rounds < 1:
                raise LMStudioValueError(
                    f"Max prediction rounds must be at least 1 ({max_prediction_rounds!r} given)"
                )
            round_counter = range(max_prediction_rounds)
            final_round_index = max_prediction_rounds - 1
        else:
            # Do not force a final round when no limit is specified
            final_round_index = -1
            round_counter = itertools.count()
        llm_tool_args = ChatResponseEndpoint.parse_tools(tools, allow_async=True)
        del tools
        # Supply the round index to any endpoint callbacks that expect one
        round_index: int
        on_first_token_for_endpoint: PredictionFirstTokenCallback | None = None
        if on_first_token is not None:

            def _wrapped_on_first_token() -> None:
                assert on_first_token is not None
                on_first_token(round_index)

            on_first_token_for_endpoint = _wrapped_on_first_token
        on_prediction_fragment_for_endpoint: PredictionFragmentCallback | None = None
        if on_prediction_fragment is not None:

            def _wrapped_on_prediction_fragment(
                fragment: LlmPredictionFragment,
            ) -> None:
                assert on_prediction_fragment is not None
                on_prediction_fragment(fragment, round_index)

            on_prediction_fragment_for_endpoint = _wrapped_on_prediction_fragment
        on_prompt_processing_for_endpoint: PromptProcessingCallback | None = None
        if on_prompt_processing_progress is not None:

            def _wrapped_on_prompt_processing_progress(progress: float) -> None:
                assert on_prompt_processing_progress is not None
                on_prompt_processing_progress(progress, round_index)

            on_prompt_processing_for_endpoint = _wrapped_on_prompt_processing_progress
        # TODO: Implementation to this point is common between the sync and async APIs
        # (aside from the allow_async flag when parsing the tool definitions)
        # Implementation past this point differs (as the sync API uses its own thread pool)

        # Request predictions until no more tool call requests are received in response
        # (or the maximum number of prediction rounds is reached)
        for round_index in round_counter:
            self._logger.debug(
                "Starting .act() prediction round", round_index=round_index
            )
            if on_round_start is not None:
                err_msg = f"Round start callback failed for {self!r}"
                with sdk_callback_invocation(err_msg, self._logger):
                    on_round_start(round_index)
            # Update the endpoint definition on each iteration in order to:
            # * update the chat history with the previous round result
            # * be able to disallow tool use when the rounds are limited
            # TODO: Refactor endpoint API to avoid repeatedly performing the
            #       LlmPredictionConfig -> KvConfigStack transformation
            endpoint = ChatResponseEndpoint(
                self.identifier,
                agent_chat,
                response_format,
                config,
                preset,
                None,  # on_message is invoked directly
                on_first_token_for_endpoint,
                on_prediction_fragment_for_endpoint,
                on_prompt_processing_for_endpoint,
                handle_invalid_tool_request,
                *(llm_tool_args if round_index != final_round_index else (None, None)),
            )
            channel_cm = self._session._create_channel(endpoint)
            prediction_stream = AsyncPredictionStream(channel_cm, endpoint)
            tool_call_requests: list[ToolCallRequest] = []
            parsed_tool_calls: list[AsyncToolCall] = []
            async for event in prediction_stream._iter_events():
                if isinstance(event, PredictionToolCallEvent):
                    tool_call_request = event.arg
                    tool_call_requests.append(tool_call_request)
                    tool_call = endpoint.request_tool_call_async(tool_call_request)
                    parsed_tool_calls.append(tool_call)
            prediction = prediction_stream.result()
            self._logger.debug(
                "Completed .act() prediction round", round_index=round_index
            )
            if on_prediction_completed:
                round_result = PredictionRoundResult.from_result(
                    prediction, round_index
                )
                err_msg = f"Prediction completed callback failed for {self!r}"
                with sdk_callback_invocation(err_msg, self._logger):
                    on_prediction_completed(round_result)
            if parsed_tool_calls:
                if max_parallel_tool_calls is None:
                    max_parallel_tool_calls = len(parsed_tool_calls)
                active_tool_calls = 0
                tool_call_futures: list[asyncio.Future[ToolCallResultData]] = []
                for tool_call in parsed_tool_calls:
                    if active_tool_calls >= max_parallel_tool_calls:
                        # Wait for a previous call to finish before starting another one
                        _done, pending = await asyncio.wait(
                            tool_call_futures, return_when=asyncio.FIRST_COMPLETED
                        )
                        active_tool_calls = len(pending)
                    tool_call_futures.append(asyncio.ensure_future(tool_call()))
                    active_tool_calls += 1
                tool_call_results: list[ToolCallResultData] = []
                for tool_call_request, tool_call_future in zip(
                    tool_call_requests, tool_call_futures
                ):
                    try:
                        await tool_call_future
                    except Exception as exc:
                        tool_call_result = endpoint._handle_failed_tool_request(
                            exc, tool_call_request
                        )
                    else:
                        tool_call_result = tool_call_future.result()
                    tool_call_results.append(tool_call_result)
                requests_message = agent_chat.add_assistant_response(
                    prediction, tool_call_requests
                )
                results_message = agent_chat.add_tool_results(tool_call_results)
                if on_message is not None:
                    err_msg = f"Tool request message callback failed for {self!r}"
                    with sdk_callback_invocation(err_msg, self._logger):
                        on_message(requests_message)
                    err_msg = f"Tool result message callback failed for {self!r}"
                    with sdk_callback_invocation(err_msg, self._logger):
                        on_message(results_message)
            elif on_message is not None:
                err_msg = f"Final response message callback failed for {self!r}"
                with sdk_callback_invocation(err_msg, self._logger):
                    on_message(agent_chat.add_assistant_response(prediction))
            if on_round_end is not None:
                err_msg = f"Round end callback failed for {self!r}"
                with sdk_callback_invocation(err_msg, self._logger):
                    on_round_end(round_index)
            if not tool_call_requests:
                # No tool call requests -> we're done here
                break
            if round_index == final_round_index:
                # We somehow received at least one tool call request,
                # even though tools are omitted on the final round
                err_msg = "Model requested tool use on final prediction round."
                endpoint._handle_invalid_tool_request(err_msg)
                break
        num_rounds = round_index + 1
        duration = time.perf_counter() - start_time
        return ActResult(rounds=num_rounds, total_time_seconds=duration)

    @sdk_public_api_async()
    async def apply_prompt_template(
        self,
        history: Chat | ChatHistoryDataDict | str,
        opts: LlmApplyPromptTemplateOpts | LlmApplyPromptTemplateOptsDict = {},
    ) -> str:
        """Apply a prompt template to the given history."""
        return await self._session._apply_prompt_template(
            self.identifier,
            history,
            opts=opts,
        )


class AsyncEmbeddingModel(AsyncModelHandle[_AsyncSessionEmbedding]):
    """Reference to a loaded embedding model."""

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    @sdk_public_api_async()
    async def embed(
        self, input: str | Iterable[str]
    ) -> Sequence[float] | Sequence[Sequence[float]]:
        """Request embedding vectors for the given input string(s)."""
        return await self._session._embed(self.identifier, input)


TAsyncSession = TypeVar("TAsyncSession", bound=_AsyncSession)


class AsyncClient(ClientBase):
    """Async SDK client interface."""

    def __init__(self, api_host: str | None = None) -> None:
        """Initialize API client."""
        super().__init__(api_host)
        self._resources = AsyncExitStack()
        self._sessions: dict[str, _AsyncSession] = {}
        self._task_manager = AsyncTaskManager()
        # Unlike the sync API, we don't support GC-based resource
        # management in the async API. Structured concurrency
        # is required to reliably offer graceful termination in
        # the presence of asynchronous iterators.

    # The async API can't implicitly perform network I/O in properties.
    # However, lazy connections also don't work due to structured concurrency.
    # For now, all sessions are opened eagerly by the client
    # TODO: revisit lazy connections given the task manager implementation
    #       (for example, eagerly start tasks for all sessions, and lazily
    #       trigger events that allow them to initiate their connection)
    _ALL_SESSIONS: tuple[Type[_AsyncSession], ...] = (
        _AsyncSessionEmbedding,
        _AsyncSessionFiles,
        _AsyncSessionLlm,
        _AsyncSessionRepository,
        _AsyncSessionSystem,
    )

    async def __aenter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        with sdk_public_api():
            await self._ensure_api_host_is_valid()
        if not self._sessions:
            rm = self._resources
            await rm.enter_async_context(self._task_manager)
            for session_cls in self._ALL_SESSIONS:
                namespace = session_cls.API_NAMESPACE
                assert namespace is not None
                session = session_cls(self)
                self._sessions[namespace] = session
                await rm.enter_async_context(session)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close any started client sessions."""
        await self._resources.aclose()

    @staticmethod
    async def _query_probe_url(url: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.get(url, timeout=1)

    @classmethod
    @sdk_public_api_async()
    async def is_valid_api_host(cls, api_host: str) -> bool:
        """Report whether the given API host is running an API server instance."""
        probe_url = cls._get_probe_url(api_host)
        try:
            probe_response = await cls._query_probe_url(probe_url)
        except (httpx.ConnectTimeout, httpx.ConnectError):
            return False
        return cls._check_probe_response(probe_response)

    @classmethod
    @sdk_public_api_async()
    async def find_default_local_api_host(cls) -> str | None:
        """Query local ports for a running API server instance."""
        for api_host in cls._iter_default_api_hosts():
            if await cls.is_valid_api_host(api_host):
                return api_host
        return None

    async def _ensure_api_host_is_valid(self) -> None:
        specified_api_host = self._api_host
        if specified_api_host is None:
            api_host = await self.find_default_local_api_host()
        elif await self.is_valid_api_host(specified_api_host):
            api_host = specified_api_host
        else:
            api_host = None
        if api_host is None:
            raise self._get_probe_failure_error(specified_api_host)
        self._api_host = api_host

    def _get_session(self, cls: Type[TAsyncSession]) -> TAsyncSession:
        """Get the client session of the given type."""
        namespace = cls.API_NAMESPACE
        assert namespace is not None
        session = self._sessions[namespace]
        # This *will* be an instance of the given type.
        # The assertion notifies typecheckers of that.
        assert isinstance(session, cls)
        return session

    @property
    @sdk_public_api()
    def llm(self) -> _AsyncSessionLlm:
        """Return the LLM API client session."""
        return self._get_session(_AsyncSessionLlm)

    @property
    @sdk_public_api()
    def embedding(self) -> _AsyncSessionEmbedding:
        """Return the embedding model API client session."""
        return self._get_session(_AsyncSessionEmbedding)

    @property
    def system(self) -> _AsyncSessionSystem:
        """Return the system API client session."""
        return self._get_session(_AsyncSessionSystem)

    @property
    def files(self) -> _AsyncSessionFiles:
        """Return the files API client session."""
        return self._get_session(_AsyncSessionFiles)

    @property
    def repository(self) -> _AsyncSessionRepository:
        """Return the repository API client session."""
        return self._get_session(_AsyncSessionRepository)

    # Convenience methods
    # Not yet implemented (server API only supports the same file types as prepare_image)
    # @sdk_public_api_async()
    async def _prepare_file(
        self, src: LocalFileInput, name: str | None = None
    ) -> FileHandle:
        """Add a file to the server. Returns a file handle for use in prediction requests."""
        return await self.files._prepare_file(src, name)

    @sdk_public_api_async()
    async def prepare_image(
        self, src: LocalFileInput, name: str | None = None
    ) -> FileHandle:
        """Add an image to the server. Returns a file handle for use in prediction requests."""
        return await self.files.prepare_image(src, name)

    @sdk_public_api_async()
    async def list_downloaded_models(
        self, namespace: str | None = None
    ) -> Sequence[AnyAsyncDownloadedModel]:
        """Get the list of downloaded models."""
        namespace_filter = check_model_namespace(namespace)
        if namespace_filter is None:
            return await self.system.list_downloaded_models()
        if namespace_filter == "llm":
            return await self.llm.list_downloaded()
        return await self.embedding.list_downloaded()

    @sdk_public_api_async()
    async def list_loaded_models(
        self, namespace: str | None = None
    ) -> Sequence[AnyAsyncModel]:
        """Get the list of loaded models using the default global client."""
        namespace_filter = check_model_namespace(namespace)
        loaded_models: list[AnyAsyncModel] = []
        if namespace_filter is None or namespace_filter == "llm":
            loaded_models.extend(await self.llm.list_loaded())
        if namespace_filter is None or namespace_filter == "embedding":
            loaded_models.extend(await self.embedding.list_loaded())
        return loaded_models


# Module level convenience API (or lack thereof)
#
# The async API follows Python's "structured concurrency" model that
# disallows non-deterministic cleanup of background tasks:
#
# * https://peps.python.org/pep-0789/#motivating-examples
# * https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/
#
# Accordingly, there is no equivalent to the global default sessions present in the sync API.
