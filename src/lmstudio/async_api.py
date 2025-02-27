"""Async I/O protocol implementation for the LM Studio remote access API."""

import asyncio
import asyncio.queues
import warnings

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
    Literal,
    Self,
    Sequence,
    Type,
    TypeAlias,
    TypeVar,
    overload,
)
from typing_extensions import TypeIs

from httpx import RequestError, HTTPStatusError
from httpx_ws import aconnect_ws, AsyncWebSocketSession, HTTPXWSException

from .sdk_api import LMStudioRuntimeError, sdk_public_api, sdk_public_api_async
from .schemas import AnyLMStudioStruct, DictObject, DictSchema, ModelSchema
from .history import (
    Chat,
    ChatHistoryDataDict,
    _FileHandle,
    _FileInputType,
    _LocalFileData,
)
from .json_api import (
    AnyModelSpecifier,
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
    PromptProcessingCallback,
    RemoteCallHandler,
    TModelInfo,
    TPrediction,
    check_model_namespace,
    load_struct,
    _model_spec_to_api_dict,
)
from ._kv_config import TLoadConfig, TLoadConfigDict, dict_from_fields_key
from ._sdk_models import (
    EmbeddingRpcEmbedStringParameter,
    EmbeddingRpcTokenizeParameter,
    LlmApplyPromptTemplateOpts,
    LlmApplyPromptTemplateOptsDict,
    LlmRpcApplyPromptTemplateParameter,
    ModelCompatibilityType,
)

from ._logging import get_logger, LogEventContext

# Only the async API itself is published from
# this module. Anything needed for type hints
# and similar tasks is published from `json_api`.
# Bypassing the high level API, and working more
# directly with the underlying websocket(s) is
# supported (hence the public names), but they're
# not exported via the top-level `lmstudio` API.
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
        rx_queue: asyncio.Queue[Any],
        endpoint: ChannelEndpoint[T, Any, Any],
        send_json: Callable[[DictObject], Awaitable[None]],
        log_context: LogEventContext,
    ) -> None:
        """Initialize asynchronous websocket streaming channel."""
        self._is_finished = False
        self._rx_queue = rx_queue
        self._api_channel = ChannelHandler(channel_id, endpoint, log_context)
        self._send_json = send_json

    def get_creation_message(self) -> DictObject:
        """Get the message to send to create this channel."""
        return self._api_channel.get_creation_message()

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
                message = await self._rx_queue.get()
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
        rx_queue: asyncio.Queue[Any],
        log_context: LogEventContext,
        notice_prefix: str = "RPC",
    ) -> None:
        """Initialize asynchronous remote procedure call."""
        self._rx_queue = rx_queue
        self._rpc = RemoteCallHandler(call_id, log_context, notice_prefix)
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, call_id=call_id)

    def get_rpc_message(
        self, endpoint: str, params: AnyLMStudioStruct | None
    ) -> DictObject:
        """Get the message to send to initiate this remote procedure call."""
        return self._rpc.get_rpc_message(endpoint, params)

    async def receive_result(self) -> Any:
        """Receive call response on the receive queue."""
        message = await self._rx_queue.get()
        return self._rpc.handle_rx_message(message)


class AsyncLMStudioWebsocket(
    LMStudioWebsocket[AsyncWebSocketSession, asyncio.Queue[Any]]
):
    """Asynchronous websocket client that handles demultiplexing of reply messages."""

    def __init__(
        self,
        ws_url: str,
        auth_details: DictObject,
        log_context: LogEventContext | None = None,
    ) -> None:
        """Initialize asynchronous websocket client."""
        super().__init__(ws_url, auth_details, log_context)
        self._resource_manager = AsyncExitStack()
        self._rx_task: asyncio.Task[None] | None = None

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

    async def _send_json(self, message: DictObject) -> None:
        # Callers are expected to call `_ensure_connected` before this method
        ws = self._ws
        assert ws is not None
        try:
            await ws.send_json(message)
        except Exception as exc:
            err = self._get_tx_error(message, exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _receive_json(self) -> Any:
        # Callers are expected to call `_ensure_connected` before this method
        ws = self._ws
        assert ws is not None
        try:
            return await ws.receive_json()
        except Exception as exc:
            err = self._get_rx_error(exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def connect(self) -> Self:
        """Connect to and authenticate with the LM Studio API."""
        self._fail_if_connected("Attempted to connect already connected websocket")
        resources = self._resource_manager
        try:
            ws: AsyncWebSocketSession = await resources.enter_async_context(
                aconnect_ws(self._ws_url)
            )
        except (RequestError, HTTPStatusError, HTTPXWSException) as exc:
            err = self._get_connection_failure_error(exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None
        self._ws = ws
        self._logger.debug("Websocket connected")
        # Authenticate
        auth_message = self._auth_details
        await self._send_json(auth_message)
        auth_result = await self._receive_json()
        self._logger.debug("Websocket authenticated", json=auth_result)
        if not auth_result["success"]:
            raise self._get_auth_failure_error(auth_result["error"])
        # Start the websocket demultiplexing task
        # The websocket manages a task group internally and will complain
        # if those aren't managed correctly, so we don't worry about
        # creating a task group of our own here
        self._rx_task = rx_task = asyncio.create_task(self._receive_messages())

        async def _terminate_rx_task() -> None:
            rx_task.cancel()
            try:
                await rx_task
            except asyncio.CancelledError:
                pass

        self._resource_manager.push_async_callback(_terminate_rx_task)
        self._logger.info(f"Websocket session established ({self._ws_url})")
        return self

    async def disconnect(self) -> None:
        """Drop the LM Studio API connection."""
        self._ws = None
        self._rx_task = None
        await self._notify_client_termination()
        await self._resource_manager.aclose()
        self._logger.info(f"Websocket session disconnected ({self._ws_url})")

    aclose = disconnect

    async def _process_next_message(self) -> bool:
        """Process the next message received on the websocket.

        Returns True if a message queue was updated.
        """
        self._ensure_connected("receive messages")
        message = await self._receive_json()
        rx_queue = self._mux.map_rx_message(message)
        if rx_queue is None:
            return False
        await rx_queue.put(message)
        return True

    async def _receive_messages(self) -> None:
        """Process received messages until connection is terminated."""
        while True:
            try:
                await self._process_next_message()
            except (LMStudioWebsocketError, HTTPXWSException):
                self._logger.exception("Websocket failed, terminating session.")
                await self.disconnect()
                break

    async def _notify_client_termination(self) -> None:
        """Send None to all clients with open receive queues."""
        for rx_queue in self._mux.all_queues():
            await rx_queue.put(None)

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
        rx_queue: asyncio.Queue[Any] = asyncio.Queue()
        with self._mux.assign_channel_id(rx_queue) as channel_id:
            channel = AsyncChannel(
                channel_id,
                rx_queue,
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
        self._logger.debug("Sending RPC request", json=call_message)
        await self._send_json(call_message)

    async def remote_call(
        self,
        endpoint: str,
        params: AnyLMStudioStruct | None,
        notice_prefix: str = "RPC",
    ) -> Any:
        """Make a remote procedure call over the websocket."""
        rx_queue: asyncio.Queue[Any] = asyncio.Queue()
        with self._mux.assign_call_id(rx_queue) as call_id:
            rpc = AsyncRemoteCall(
                call_id, rx_queue, self._logger.event_context, notice_prefix
            )
            await self._send_call(rpc, endpoint, params)
            return await rpc.receive_result()


class AsyncSession(ClientSession["AsyncClient", AsyncLMStudioWebsocket]):
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
    async def connect(self) -> AsyncLMStudioWebsocket:
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
        self._lmsws = lmsws = await resources.enter_async_context(
            AsyncLMStudioWebsocket(session_url, self._client._auth_details)
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
    "TAsyncSessionModel", bound="AsyncSessionModel[Any, Any, Any, Any]"
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
        """Load this model with the given identifier and configuration."""
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
        # Call _get_or_load directly, since we have a model identifier
        handle: TAsyncModelHandle = await self._session._get_or_load(
            self.model_key, ttl, config, on_load_progress
        )
        return handle


class AsyncDownloadedEmbeddingModel(
    AsyncDownloadedModel[
        EmbeddingModelInfo,
        "AsyncSessionEmbedding",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        "AsyncEmbeddingModel",
    ],
):
    """Asynchronous download listing for an embedding model."""

    def __init__(
        self, model_info: DictObject, session: "AsyncSessionEmbedding"
    ) -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(EmbeddingModelInfo, model_info, session)


class AsyncDownloadedLlm(
    AsyncDownloadedModel[
        LlmInfo,
        "AsyncSessionLlm",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        "AsyncLLM",
    ]
):
    """Asynchronous ownload listing for an LLM."""

    def __init__(self, model_info: DictObject, session: "AsyncSessionLlm") -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(LlmInfo, model_info, session)


AnyAsyncDownloadedModel: TypeAlias = AsyncDownloadedModel[Any, Any, Any, Any, Any]


class AsyncSessionSystem(AsyncSession):
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


class _AsyncSessionFiles(AsyncSession):
    """Async client session for the files namespace."""

    API_NAMESPACE = "files"

    async def _fetch_file_handle(self, file_data: _LocalFileData) -> _FileHandle:
        handle = await self.remote_call("uploadFileBase64", file_data._as_fetch_param())
        # Returned dict provides the handle identifier, file type, and size in bytes
        # Add the extra fields needed for a FileHandle (aka ChatMessagePartFileData)
        handle["name"] = file_data.name
        handle["type"] = "file"
        return load_struct(handle, _FileHandle)

    @sdk_public_api_async()
    async def _add_temp_file(
        self, src: _FileInputType, name: str | None = None
    ) -> _FileHandle:
        """Add a file to the server."""
        # Private until LM Studio file handle support stabilizes
        file_data = _LocalFileData(src, name)
        return await self._fetch_file_handle(file_data)


class AsyncModelDownloadOption(ModelDownloadOptionBase[AsyncSession]):
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


class AsyncAvailableModel(AvailableModelBase[AsyncSession]):
    """A model available for download from the model repository."""

    _session: AsyncSession

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


class AsyncSessionRepository(AsyncSession):
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


class AsyncSessionModel(
    AsyncSession,
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
    def _system_session(self) -> AsyncSessionSystem:
        return self._client.system

    @property
    def _files_session(self) -> _AsyncSessionFiles:
        return self._client._files

    async def _get_load_config(self, model_specifier: AnyModelSpecifier) -> DictObject:
        """Get the model load config for the specified model."""
        # Note that the configuration reported here uses the *server* config names,
        # not the attributes used to set the configuration in the client SDK
        params = self._API_TYPES.REQUEST_LOAD_CONFIG._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
            }
        )
        config = await self.remote_call("getLoadConfig", params)
        return dict_from_fields_key(config)

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
    @sdk_public_api_async()
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
        """Get a handle to the specified model (loading it if necessary)."""
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
        """Load the specified model with the given identifier and configuration."""
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
        config_type = self._API_TYPES.MODEL_LOAD_CONFIG
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

    async def _fetch_file_handle(self, file_data: _LocalFileData) -> _FileHandle:
        return await self._files_session._fetch_file_handle(file_data)


AsyncPredictionChannel: TypeAlias = AsyncChannel[PredictionResult[T]]
AsyncPredictionCM: TypeAlias = AsyncContextManager[AsyncPredictionChannel[T]]


class AsyncPredictionStream(PredictionStreamBase[TPrediction]):
    """Async context manager for an ongoing prediction process."""

    def __init__(
        self,
        channel_cm: AsyncPredictionCM[TPrediction],
        endpoint: PredictionEndpoint[TPrediction],
    ) -> None:
        """Initialize a prediction process representation."""
        self._resource_manager = AsyncExitStack()
        self._channel_cm: AsyncPredictionCM[TPrediction] = channel_cm
        self._channel: AsyncPredictionChannel[TPrediction] | None = None
        # See comments in BasePrediction regarding not calling super().__init__() here
        self._init_prediction(endpoint)

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
        endpoint = self._endpoint
        async with self:
            assert self._channel is not None
            async for contents in self._channel.rx_stream():
                for event in endpoint.iter_message_events(contents):
                    endpoint.handle_rx_event(event)
                    if isinstance(event, PredictionFragmentEvent):
                        yield event.arg
                if endpoint.is_finished:
                    break
            self._mark_finished()

    @sdk_public_api_async()
    async def wait_for_result(self) -> PredictionResult[TPrediction]:
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


class AsyncSessionLlm(
    AsyncSessionModel[
        "AsyncLLM",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        AsyncDownloadedLlm,
    ]
):
    """Async client session for LLM namespace."""

    API_NAMESPACE = "llm"
    _API_TYPES = ModelTypesLlm

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize API client session for LLM interaction."""
        super().__init__(client)

    def _create_handle(self, model_identifier: str) -> "AsyncLLM":
        """Create a symbolic handle to the specified LLM model."""
        return AsyncLLM(model_identifier, self)

    @overload
    async def _complete_stream(
        self,
        model_specifier: AnyModelSpecifier,
        prompt: str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[str]: ...
    @overload
    async def _complete_stream(
        self,
        model_specifier: AnyModelSpecifier,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[DictObject]: ...
    async def _complete_stream(
        self,
        model_specifier: AnyModelSpecifier,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream[str] | AsyncPredictionStream[DictObject]:
        """Request a one-off prediction without any context and stream the generated tokens."""
        endpoint = CompletionEndpoint(
            model_specifier,
            prompt,
            response_format,
            config,
            on_message,
            on_first_token,
            on_prediction_fragment,
            on_prompt_processing_progress,
        )
        channel_cm = self._create_channel(endpoint)
        prediction_stream = AsyncPredictionStream(channel_cm, endpoint)
        return prediction_stream

    @overload
    async def _respond_stream(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[str]: ...
    @overload
    async def _respond_stream(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[DictObject]: ...
    async def _respond_stream(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        on_message: PredictionMessageCallback | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream[str] | AsyncPredictionStream[DictObject]:
        """Request a response in an ongoing assistant chat session and stream the generated tokens."""
        if not isinstance(history, Chat):
            history = Chat.from_history(history)
        await history._fetch_file_handles_async(self._fetch_file_handle)
        endpoint = ChatResponseEndpoint(
            model_specifier,
            history,
            response_format,
            config,
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
        await history._fetch_file_handles_async(self._fetch_file_handle)
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


class AsyncSessionEmbedding(
    AsyncSessionModel[
        "AsyncEmbeddingModel",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        AsyncDownloadedEmbeddingModel,
    ]
):
    """Async client session for embedding namespace."""

    API_NAMESPACE = "embedding"
    _API_TYPES = ModelTypesEmbedding

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize API client session for embedding model interaction."""
        super().__init__(client)

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


class AsyncModelHandle(ModelHandleBase[TAsyncSessionModel]):
    """Reference to a loaded LM Studio model."""

    @sdk_public_api_async()
    async def unload(self) -> None:
        """Unload this model."""
        await self._session.unload(self.identifier)

    @sdk_public_api_async()
    async def get_info(self) -> ModelInstanceInfo:
        """Get the model info for this model."""
        return await self._session.get_model_info(self.identifier)

    # Private until this API can emit the client config types
    @sdk_public_api_async()
    async def _get_load_config(self) -> DictObject:
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
    async def get_context_length(self) -> int:
        """Get the context length of this model."""
        return await self._session._get_context_length(self.identifier)


AnyAsyncModel: TypeAlias = AsyncModelHandle[Any]


class AsyncLLM(AsyncModelHandle[AsyncSessionLlm]):
    """Reference to a loaded LLM model."""

    @overload
    async def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[str]: ...
    @overload
    async def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[DictObject]: ...
    @sdk_public_api_async()
    async def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream[str] | AsyncPredictionStream[DictObject]:
        """Request a one-off prediction without any context and stream the generated tokens."""
        return await self._session._complete_stream(
            self.identifier,
            prompt,
            response_format=response_format,
            config=config,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )

    @overload
    async def complete(
        self,
        prompt: str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionResult[str]: ...
    @overload
    async def complete(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionResult[DictObject]: ...
    @sdk_public_api_async()
    async def complete(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionResult[str] | PredictionResult[DictObject]:
        """Request a one-off prediction without any context."""
        prediction_stream = await self._session._complete_stream(
            self.identifier,
            prompt,
            response_format=response_format,
            config=config,
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

    @overload
    async def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[str]: ...
    @overload
    async def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> AsyncPredictionStream[DictObject]: ...
    @sdk_public_api_async()
    async def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> AsyncPredictionStream[str] | AsyncPredictionStream[DictObject]:
        """Request a response in an ongoing assistant chat session and stream the generated tokens."""
        return await self._session._respond_stream(
            self.identifier,
            history,
            response_format=response_format,
            config=config,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )

    @overload
    async def respond(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionResult[str]: ...
    @overload
    async def respond(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionResult[DictObject]: ...
    @sdk_public_api_async()
    async def respond(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionResult[str] | PredictionResult[DictObject]:
        """Request a response in an ongoing assistant chat session."""
        prediction_stream = await self._session._respond_stream(
            self.identifier,
            history,
            response_format=response_format,
            config=config,
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


class AsyncEmbeddingModel(AsyncModelHandle[AsyncSessionEmbedding]):
    """Reference to a loaded embedding model."""

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    @sdk_public_api_async()
    async def embed(
        self, input: str | Iterable[str]
    ) -> Sequence[float] | Sequence[Sequence[float]]:
        """Request embedding vectors for the given input string(s)."""
        return await self._session._embed(self.identifier, input)


TAsyncSession = TypeVar("TAsyncSession", bound=AsyncSession)

_ASYNC_API_STABILITY_WARNING = """\
Note the async API is not yet stable and is expected to change in future releases
"""


class AsyncClient(ClientBase):
    """Async SDK client interface."""

    def __init__(self, api_host: str | None = None) -> None:
        """Initialize API client."""
        # Warn about the async API stability, since we expect it to change
        # (in particular, accepting coroutine functions as callbacks)
        warnings.warn(_ASYNC_API_STABILITY_WARNING, FutureWarning)
        super().__init__(api_host)
        self._resources = AsyncExitStack()
        self._sessions: dict[str, AsyncSession] = {}
        # Unlike the sync API, we don't support GC-based resource
        # management in the async API. Structured concurrency
        # is required to reliably offer graceful termination in
        # the presence of asynchronous iterators.

    # The async API can't implicitly perform network I/O in properties.
    # However, lazy connections also don't work due to structured concurrency.
    # For now, all sessions are opened eagerly by the client
    # TODO: provide a way to selectively exclude unnecessary client sessions
    _ALL_SESSIONS = (
        AsyncSessionEmbedding,
        _AsyncSessionFiles,
        AsyncSessionLlm,
        AsyncSessionRepository,
        AsyncSessionSystem,
    )

    async def __aenter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        if not self._sessions:
            for cls in self._ALL_SESSIONS:
                namespace = cls.API_NAMESPACE
                assert namespace is not None
                session = cls(self)
                self._sessions[namespace] = session
                await self._resources.enter_async_context(session)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close any started client sessions."""
        await self._resources.aclose()

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
    def llm(self) -> AsyncSessionLlm:
        """Return the LLM API client session."""
        return self._get_session(AsyncSessionLlm)

    @property
    @sdk_public_api()
    def embedding(self) -> AsyncSessionEmbedding:
        """Return the embedding model API client session."""
        return self._get_session(AsyncSessionEmbedding)

    @property
    def system(self) -> AsyncSessionSystem:
        """Return the system API client session."""
        return self._get_session(AsyncSessionSystem)

    @property
    def _files(self) -> _AsyncSessionFiles:
        """Return the files API client session."""
        # Private until LM Studio file handle support stabilizes
        return self._get_session(_AsyncSessionFiles)

    @property
    def repository(self) -> AsyncSessionRepository:
        """Return the repository API client session."""
        return self._get_session(AsyncSessionRepository)

    # Convenience methods
    @sdk_public_api_async()
    async def _add_temp_file(
        self, src: _FileInputType, name: str | None = None
    ) -> _FileHandle:
        """Add a file to the server."""
        # Private until LM Studio file handle support stabilizes
        return await self._files._add_temp_file(src, name)

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
