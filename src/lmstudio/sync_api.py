"""Sync I/O protocol implementation for the LM Studio remote access API."""

import asyncio
import itertools
import time
import threading
import queue
import weakref

from abc import abstractmethod
from concurrent.futures import Future as SyncFuture, ThreadPoolExecutor, as_completed
from contextlib import (
    asynccontextmanager,
    AsyncExitStack,
    contextmanager,
    ExitStack,
)
from types import TracebackType
from typing import (
    Any,
    AsyncGenerator,
    ContextManager,
    Coroutine,
    Generator,
    Iterable,
    Iterator,
    Callable,
    Generic,
    Literal,
    NoReturn,
    Self,
    Sequence,
    Type,
    TypeAlias,
    TypeVar,
    overload,
)
from typing_extensions import TypeIs

# Synchronous API still uses an async websocket (just in a background thread)
from httpx_ws import aconnect_ws, AsyncWebSocketSession, HTTPXWSException

from .sdk_api import (
    LMStudioRuntimeError,
    LMStudioValueError,
    sdk_callback_invocation,
    sdk_public_api,
)
from .schemas import AnyLMStudioStruct, DictObject, DictSchema, ModelSchema
from .history import (
    AssistantResponse,
    ToolResultMessage,
    Chat,
    ChatHistoryDataDict,
    _FileHandle,
    _FileInputType,
    _LocalFileData,
    ToolCallRequest,
)
from .json_api import (
    ActResult,
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
    PredictionEndpoint,
    PredictionFirstTokenCallback,
    PredictionFragmentCallback,
    PredictionFragmentEvent,
    PredictionMessageCallback,
    PredictionResult,
    PredictionRoundResult,
    PredictionRxEvent,
    PredictionStreamBase,
    PredictionToolCallEvent,
    PromptProcessingCallback,
    RemoteCallHandler,
    TModelInfo,
    TPrediction,
    ToolDefinition,
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

# Only the sync API itself is published from
# this module. Anything needed for type hints
# and similar tasks is published from `json_api`.
# Bypassing the high level API, and working more
# directly with the underlying websocket(s) is
# supported (hence the public names), but they're
# not exported via the top-level `lmstudio` API.
__all__ = [
    "AnyDownloadedModel",
    "Client",
    "DownloadedEmbeddingModel",
    "DownloadedLlm",
    "EmbeddingModel",
    "LLM",
    "SyncModelHandle",
    "PredictionStream",
    "get_default_client",
    "embedding_model",
    "list_downloaded_models",
    "list_loaded_models",
    "llm",
]


T = TypeVar("T")


class SyncChannel(Generic[T]):
    """Communication subchannel over multiplexed async websocket."""

    def __init__(
        self,
        channel_id: int,
        rx_queue: queue.Queue[Any],
        endpoint: ChannelEndpoint[T, Any, Any],
        send_json: Callable[[DictObject], None],
        log_context: LogEventContext,
    ) -> None:
        """Initialize synchronous websocket streaming channel."""
        self._is_finished = False
        self._rx_queue = rx_queue
        self._api_channel = ChannelHandler(channel_id, endpoint, log_context)
        self._send_json = send_json

    def get_creation_message(self) -> DictObject:
        """Get the message to send to create this channel."""
        return self._api_channel.get_creation_message()

    def cancel(self) -> None:
        """Cancel the channel."""
        if self._is_finished:
            return
        cancel_message = self._api_channel.get_cancel_message()
        self._send_json(cancel_message)

    def rx_stream(
        self,
    ) -> Iterator[DictObject | None]:
        """Stream received channel messages until channel is closed by server."""
        while not self._is_finished:
            with sdk_public_api():
                # Avoid emitting tracebacks that delve into supporting libraries
                # (we can't easily suppress the SDK's own frames for iterators)
                message = self._rx_queue.get()
                contents = self._api_channel.handle_rx_message(message)
            if contents is None:
                self._is_finished = True
                break
            yield contents

    def wait_for_result(self) -> T:
        """Wait for the channel to finish and return the result."""
        endpoint = self._api_channel.endpoint
        for contents in self.rx_stream():
            endpoint.handle_message_events(contents)
            if endpoint.is_finished:
                break
        return endpoint.result()


class SyncRemoteCall:
    """Remote procedure call over multiplexed async websocket."""

    def __init__(
        self,
        call_id: int,
        rx_queue: queue.Queue[Any],
        log_context: LogEventContext,
        notice_prefix: str = "RPC",
    ) -> None:
        """Initialize synchronous remote procedure call."""
        self._rx_queue = rx_queue
        self._rpc = RemoteCallHandler(call_id, log_context, notice_prefix)
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, call_id=call_id)

    def get_rpc_message(
        self, endpoint: str, params: AnyLMStudioStruct | None
    ) -> DictObject:
        """Get the message to send to initiate this remote procedure call."""
        return self._rpc.get_rpc_message(endpoint, params)

    def receive_result(self) -> Any:
        """Receive call response on the receive queue."""
        message = self._rx_queue.get()
        return self._rpc.handle_rx_message(message)


class _AsyncWebsocketThread(threading.Thread):
    def __init__(
        self,
        ws_url: str,
        auth_details: DictObject,
        enqueue_message: Callable[[DictObject], bool],
        log_context: LogEventContext,
    ) -> None:
        # Annoyingly, we have to mark the background thread as a daemon thread to
        # prevent hanging at shutdown. Even checking `sys.is_finalizing()` is inadequate
        # https://discuss.python.org/t/should-sys-is-finalizing-report-interpreter-finalization-instead-of-runtime-finalization/76695
        super().__init__(daemon=True)
        self._auth_details = auth_details
        # Event usage:
        #    threading.Event: set by background thread, checked by main thread
        #    asyncio.Event: set by main thread, checked by background thread
        self._connection_attempted = threading.Event()
        self._connection_failure: Exception | None = None
        self._auth_failure: Any | None = None
        self._terminate = asyncio.Event()
        self._ws_url = ws_url
        self._ws: AsyncWebSocketSession | None = None
        self._ws_loop: asyncio.AbstractEventLoop | None = None
        self._rx_task: asyncio.Task[None] | None = None
        self._queue_message = enqueue_message
        self._logger = logger = get_logger(type(self).__name__)
        logger.update_context(log_context, thread_id=self.name)

    def connect(self) -> bool:
        self.start()
        self._connection_attempted.wait()  # Block until connection has been attempted
        return self._ws is not None and self._ws_loop is not None

    def disconnect(self) -> None:
        if self._ws is not None:
            self._call_in_background(self._terminate_main_task)
        self.join()  # Block until thread has terminated

    def run(self) -> None:
        self._logger.info("Websocket thread started")
        try:
            asyncio.run(self._main_task())
        except BaseException:
            err_msg = "Terminating websocket thread due to exception"
            self._logger.debug(err_msg, exc_info=True)
        finally:
            # Ensure the main thread is unblocked even if the
            # background async task errors out completely
            self._connection_attempted.set()
        self._logger.info("Websocket thread terminated")

    # TODO: Improve code sharing between this background thread async websocket
    #       and the async-native AsyncLMStudioWebsocket implementation
    async def _main_task(self) -> None:
        resources = AsyncExitStack()
        try:
            ws: AsyncWebSocketSession = await resources.enter_async_context(
                aconnect_ws(self._ws_url)
            )
        except Exception as exc:
            self._connection_failure = exc
            raise

        def _clear_task_state() -> None:
            # Break the reference cycle with the main thread
            del self._queue_message
            # Websocket is about to be disconnected
            self._ws = None
            # Event loop is about to shut down
            self._ws_loop = None

        resources.callback(_clear_task_state)
        self._ws_loop = asyncio.get_running_loop()
        async with resources:
            self._logger.debug("Websocket connected")
            self._ws = ws
            if not await self._authenticate():
                return
            async with self._manage_demultiplexing():
                self._connection_attempted.set()
                self._logger.info(f"Websocket session established ({self._ws_url})")
                # Keep the event loop alive until termination is requested
                await self._terminate.wait()

    async def _send_json(self, message: DictObject) -> None:
        # This is only called if the websocket has been created
        ws = self._ws
        assert ws is not None
        try:
            await ws.send_json(message)
        except Exception as exc:
            err = LMStudioWebsocket._get_tx_error(message, exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _receive_json(self) -> Any:
        # This is only called if the websocket has been created
        ws = self._ws
        assert ws is not None
        try:
            return await ws.receive_json()
        except Exception as exc:
            err = LMStudioWebsocket._get_rx_error(exc)
            # Log the underlying exception info, but simplify the raised traceback
            self._logger.debug(str(err), exc_info=True)
            raise err from None

    async def _authenticate(self) -> bool:
        # This is only called if the websocket has been created
        ws = self._ws
        assert ws is not None
        auth_message = self._auth_details
        await self._send_json(auth_message)
        auth_result = await self._receive_json()
        self._logger.debug("Websocket authenticated", json=auth_result)
        if not auth_result["success"]:
            self._auth_failure = auth_result["error"]
            return False
        return True

    @asynccontextmanager
    async def _manage_demultiplexing(
        self,
    ) -> AsyncGenerator[asyncio.Task[None], None]:
        self._rx_task = rx_task = asyncio.create_task(self._demultiplexing_task())
        try:
            yield rx_task
        finally:
            if rx_task.cancel():
                try:
                    await rx_task
                except asyncio.CancelledError:
                    pass

    async def _process_next_message(self) -> bool:
        """Process the next message received on the websocket.

        Returns True if a message queue was updated.
        """
        # This is only called if the websocket has been created
        ws = self._ws
        assert ws is not None
        message = await ws.receive_json()
        return await asyncio.to_thread(self._queue_message, message)

    def _raise_on_termination(
        self,
    ) -> tuple[Coroutine[None, None, NoReturn], Type[Exception]]:
        class TerminateTask(Exception):
            pass

        async def raise_on_termination() -> NoReturn:
            await self._terminate.wait()
            raise TerminateTask

        return raise_on_termination(), TerminateTask

    async def _demultiplexing_task(self) -> None:
        """Process received messages until connection is terminated."""
        raise_on_termination, terminated_exc = self._raise_on_termination()
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(raise_on_termination)
                tg.create_task(self._receive_messages())
        except* terminated_exc:
            self._logger.info("Websocket closed, terminating demultiplexing task.")

    async def _receive_messages(self) -> None:
        """Process received messages until task is cancelled."""
        while True:
            try:
                await self._process_next_message()
            except (LMStudioWebsocketError, HTTPXWSException):
                if self._ws is not None:
                    # Websocket failed unexpectedly (rather than due to client shutdown)
                    self._logger.exception("Websocket failed, terminating session.")
                    self._terminate.set()
                break

    def _terminate_main_task(self) -> None:
        self._terminate.set()

    def _run_background_task(self, coro: Coroutine[None, None, Any]) -> SyncFuture[Any]:
        # Runtime state consistency checks are in SyncLMStudioWebsocket
        loop = self._ws_loop
        assert loop is not None
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def _call_in_background(self, callback: Callable[[], Any]) -> None:
        # Runtime state consistency checks are in SyncLMStudioWebsocket
        loop = self._ws_loop
        assert loop is not None
        loop.call_soon_threadsafe(callback)

    def send_json(self, message: DictObject) -> None:
        future = self._run_background_task(self._send_json(message))
        future.result()  # Block until message has been sent


class SyncLMStudioWebsocket(LMStudioWebsocket[_AsyncWebsocketThread, queue.Queue[Any]]):
    """Synchronous websocket client that handles demultiplexing of reply messages."""

    def __init__(
        self,
        ws_url: str,
        auth_details: DictObject,
        log_context: LogEventContext | None = None,
    ) -> None:
        """Initialize synchronous websocket client."""
        super().__init__(ws_url, auth_details, log_context)

    @property
    def _httpx_ws(self) -> AsyncWebSocketSession | None:
        # Underlying HTTPX session is accessible for testing purposes
        ws_thread = self._ws
        if ws_thread is None:
            return None
        return ws_thread._ws

    def __enter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        if self._ws is None:
            self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    def connect(self) -> Self:
        """Connect to and authenticate with the LM Studio API."""
        self._fail_if_connected("Attempted to connect already connected websocket")
        ws = _AsyncWebsocketThread(
            self._ws_url,
            self._auth_details,
            self._enqueue_message,
            self._logger.event_context,
        )
        if not ws.connect():
            if ws._connection_failure is not None:
                raise self._get_connection_failure_error(ws._connection_failure)
            if ws._auth_failure is not None:
                raise self._get_auth_failure_error(ws._auth_failure)
            self._logger.error("Connection failed, but no failure reason reported.")
            raise self._get_connection_failure_error()
        self._ws = ws
        return self

    def disconnect(self) -> None:
        """Drop the LM Studio API connection."""
        ws = self._ws
        self._ws = None
        self._rx_task = None
        if ws is not None:
            self._logger.debug(f"Disconnecting websocket session ({self._ws_url})")
            self._notify_client_termination()
            ws.disconnect()
        self._logger.info(f"Websocket session disconnected ({self._ws_url})")

    close = disconnect

    def _enqueue_message(self, message: Any) -> bool:
        rx_queue = self._mux.map_rx_message(message)
        if rx_queue is None:
            return False
        rx_queue.put(message)
        return True

    def _notify_client_termination(self) -> None:
        """Send None to all clients with open receive queues."""
        for rx_queue in self._mux.all_queues():
            rx_queue.put(None)

    def _send_json(self, message: DictObject) -> None:
        # Callers are expected to call `_ensure_connected` before this method
        ws = self._ws
        assert ws is not None
        # Background thread handles the exception conversion
        ws.send_json(message)

    def _connect_to_endpoint(self, channel: SyncChannel[Any]) -> None:
        """Connect channel to specified endpoint."""
        self._ensure_connected("open channel endpoints")
        create_message = channel.get_creation_message()
        self._logger.debug("Connecting channel endpoint", json=create_message)
        self._send_json(create_message)

    @contextmanager
    def open_channel(
        self,
        endpoint: ChannelEndpoint[T, Any, Any],
    ) -> Generator[SyncChannel[T], None, None]:
        """Open a streaming channel over the websocket."""
        rx_queue: queue.Queue[Any] = queue.Queue()
        with self._mux.assign_channel_id(rx_queue) as channel_id:
            channel = SyncChannel(
                channel_id,
                rx_queue,
                endpoint,
                self._send_json,
                self._logger.event_context,
            )
            self._connect_to_endpoint(channel)
            yield channel

    def _send_call(
        self,
        rpc: SyncRemoteCall,
        endpoint: str,
        params: AnyLMStudioStruct | None = None,
    ) -> None:
        """Initiate remote call to specified endpoint."""
        self._ensure_connected("send remote procedure call")
        call_message = rpc.get_rpc_message(endpoint, params)
        self._logger.debug("Sending RPC request", json=call_message)
        self._send_json(call_message)

    def remote_call(
        self,
        endpoint: str,
        params: AnyLMStudioStruct | None,
        notice_prefix: str = "RPC",
    ) -> Any:
        """Make a remote procedure call over the websocket."""
        rx_queue: queue.Queue[Any] = queue.Queue()
        with self._mux.assign_call_id(rx_queue) as call_id:
            rpc = SyncRemoteCall(
                call_id, rx_queue, self._logger.event_context, notice_prefix
            )
            self._send_call(rpc, endpoint, params)
            return rpc.receive_result()


class SyncSession(ClientSession["Client", SyncLMStudioWebsocket]):
    """Sync client session interfaces applicable to all API namespaces."""

    def __init__(self, client: "Client") -> None:
        """Initialize synchronous API client session."""
        super().__init__(client)
        self._resources = ExitStack()

    def _ensure_connected(self) -> None:
        # Allow lazy connection of the session websocket
        if self._lmsws is None:
            self.connect()

    def __enter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        self._ensure_connected()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    @sdk_public_api()
    def connect(self) -> SyncLMStudioWebsocket:
        """Connect the client session."""
        self._fail_if_connected("Attempted to connect already connected session")
        api_host = self._client.api_host
        namespace = self.API_NAMESPACE
        if namespace is None:
            raise LMStudioClientError(
                f"No API namespace defined for {type(self).__name__}"
            )
        session_url = f"ws://{api_host}/{namespace}"
        resources = self._resources
        self._lmsws = lmsws = resources.enter_context(
            SyncLMStudioWebsocket(session_url, self._client._auth_details)
        )
        return lmsws

    @sdk_public_api()
    def disconnect(self) -> None:
        """Disconnect the client session."""
        self._lmsws = None
        self._resources.close()

    close = disconnect

    # To allow for client level management of the session lifecycles
    # without requiring network I/O on property access, we implicitly
    # connect the websocket (if necessary) when sending requests

    @contextmanager
    def _create_channel(
        self,
        endpoint: ChannelEndpoint[T, Any, Any],
    ) -> Generator[SyncChannel[T], None, None]:
        """Connect a channel to an LM Studio streaming endpoint."""
        self._ensure_connected()
        lmsws = self._get_lmsws("create channels")
        with lmsws.open_channel(endpoint) as channel:
            yield channel

    @sdk_public_api()
    def remote_call(
        self,
        endpoint: str,
        params: AnyLMStudioStruct | None = None,
        notice_prefix: str = "RPC",
    ) -> Any:
        """Send a remote call to the given RPC endpoint and wait for the result."""
        self._ensure_connected()
        lmsws = self._get_lmsws("make remote calls")
        return lmsws.remote_call(endpoint, params, notice_prefix)


TSyncSessionModel = TypeVar(
    "TSyncSessionModel", bound="SyncSessionModel[Any, Any, Any, Any]"
)
TModelHandle = TypeVar("TModelHandle", bound="SyncModelHandle[Any]")


class DownloadedModel(
    Generic[
        TModelInfo,
        TSyncSessionModel,
        TLoadConfig,
        TLoadConfigDict,
        TModelHandle,
    ],
    DownloadedModelBase[TModelInfo, TSyncSessionModel],
):
    @sdk_public_api()
    def load_new_instance(
        self,
        *,
        ttl: int | None = DEFAULT_TTL,
        instance_identifier: str | None = None,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TModelHandle:
        """Load this model with the given identifier and configuration."""
        handle: TModelHandle = self._session._load_new_instance(
            self.model_key, instance_identifier, ttl, config, on_load_progress
        )
        return handle

    @sdk_public_api()
    def model(
        self,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TModelHandle:
        # Call _get_or_load directly, since we have a model identifier
        handle: TModelHandle = self._session._get_or_load(
            self.model_key, ttl, config, on_load_progress
        )
        return handle


class DownloadedEmbeddingModel(
    DownloadedModel[
        EmbeddingModelInfo,
        "SyncSessionEmbedding",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        "EmbeddingModel",
    ],
):
    """Download listing for an embedding model."""

    def __init__(self, model_info: DictObject, session: "SyncSessionEmbedding") -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(EmbeddingModelInfo, model_info, session)


class DownloadedLlm(
    DownloadedModel[
        LlmInfo,
        "SyncSessionLlm",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        "LLM",
    ]
):
    """Download listing for an LLM."""

    def __init__(self, model_info: DictObject, session: "SyncSessionLlm") -> None:
        """Initialize downloaded embedding model details."""
        super().__init__(LlmInfo, model_info, session)


AnyDownloadedModel: TypeAlias = DownloadedModel[Any, Any, Any, Any, Any]


class SyncSessionSystem(SyncSession):
    """Sync client session for the system namespace."""

    API_NAMESPACE = "system"

    @sdk_public_api()
    def list_downloaded_models(self) -> Sequence[AnyDownloadedModel]:
        """Get the list of all downloaded models that are available for loading."""
        # The list of downloaded models is only available via the system API namespace
        models = self.remote_call("listDownloadedModels")
        return [self._process_download_listing(m) for m in models]

    def _process_download_listing(self, model_info: DictObject) -> AnyDownloadedModel:
        model_type = model_info.get("type")
        if model_type is None:
            raise LMStudioClientError(
                f"No 'type' field in download listing: {model_info}"
            )
        match model_type:
            case "embedding":
                return DownloadedEmbeddingModel(model_info, self._client.embedding)
            case "llm":
                return DownloadedLlm(model_info, self._client.llm)
        raise LMStudioClientError(
            f"Unknown model type {model_type!r} in download listing: {model_info}"
        )


class _SyncSessionFiles(SyncSession):
    """Sync client session for the files namespace."""

    API_NAMESPACE = "files"

    def _fetch_file_handle(self, file_data: _LocalFileData) -> _FileHandle:
        handle = self.remote_call("uploadFileBase64", file_data._as_fetch_param())
        # Returned dict provides the handle identifier, file type, and size in bytes
        # Add the extra fields needed for a FileHandle (aka ChatMessagePartFileData)
        handle["name"] = file_data.name
        handle["type"] = "file"
        return load_struct(handle, _FileHandle)

    @sdk_public_api()
    def _add_temp_file(
        self, src: _FileInputType, name: str | None = None
    ) -> _FileHandle:
        """Add a file to the server."""
        # Private until LM Studio file handle support stabilizes
        file_data = _LocalFileData(src, name)
        return self._fetch_file_handle(file_data)


class ModelDownloadOption(ModelDownloadOptionBase[SyncSession]):
    """A single download option for a model search result."""

    @sdk_public_api()
    def download(
        self,
        on_progress: DownloadProgressCallback | None = None,
        on_finalize: DownloadFinalizedCallback | None = None,
    ) -> str:
        """Download a model and get its path for loading."""
        endpoint = self._get_download_endpoint(on_progress, on_finalize)
        with self._session._create_channel(endpoint) as channel:
            return channel.wait_for_result()


class AvailableModel(AvailableModelBase[SyncSession]):
    """A model available for download from the model repository."""

    @sdk_public_api()
    def get_download_options(
        self,
    ) -> Sequence[ModelDownloadOption]:
        """Get the download options for the specified model."""
        params = self._get_download_query_params()
        options = self._session.remote_call("getModelDownloadOptions", params)
        final = []
        for m in options["results"]:
            final.append(ModelDownloadOption(m, self._session))
        return final


class SyncSessionRepository(SyncSession):
    """Sync client session for the repository namespace."""

    API_NAMESPACE = "repository"

    @sdk_public_api()
    def search_models(
        self,
        search_term: str | None = None,
        limit: int | None = None,
        compatibility_types: list[ModelCompatibilityType] | None = None,
    ) -> Sequence[AvailableModel]:
        """Search for downloadable models satisfying a search query."""
        params = self._get_model_search_params(search_term, limit, compatibility_types)
        models = self.remote_call("searchModels", params)
        return [AvailableModel(m, self) for m in models["results"]]


TDownloadedModel = TypeVar("TDownloadedModel", bound=AnyDownloadedModel)


class SyncSessionModel(
    SyncSession,
    Generic[TModelHandle, TLoadConfig, TLoadConfigDict, TDownloadedModel],
):
    """Sync client session for a model (LLM/embedding) namespace."""

    _API_TYPES: Type[ModelSessionTypes[TLoadConfig]]

    @property
    def _system_session(self) -> SyncSessionSystem:
        return self._client.system

    @property
    def _files_session(self) -> _SyncSessionFiles:
        return self._client._files

    def _get_load_config(self, model_specifier: AnyModelSpecifier) -> DictObject:
        """Get the model load config for the specified model."""
        # Note that the configuration reported here uses the *server* config names,
        # not the attributes used to set the configuration in the client SDK
        params = self._API_TYPES.REQUEST_LOAD_CONFIG._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
            }
        )
        config = self.remote_call("getLoadConfig", params)
        return dict_from_fields_key(config)

    def _get_api_model_info(self, model_specifier: AnyModelSpecifier) -> Any:
        """Get the raw model info (if any) for a model matching the given criteria."""
        params = self._API_TYPES.REQUEST_MODEL_INFO._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "throwIfNotFound": True,
            }
        )
        return self.remote_call("getModelInfo", params)

    @sdk_public_api()
    def get_model_info(self, model_specifier: AnyModelSpecifier) -> ModelInstanceInfo:
        """Get the model info (if any) for a model matching the given criteria."""
        response = self._get_api_model_info(model_specifier)
        model_info = self._API_TYPES.MODEL_INSTANCE_INFO._from_any_api_dict(response)
        return model_info

    def _get_context_length(self, model_specifier: AnyModelSpecifier) -> int:
        """Get the context length of the specified model."""
        raw_model_info = self._get_api_model_info(model_specifier)
        return int(raw_model_info.get("contextLength", -1))

    # Private helper method to allow the main API to easily accept iterables
    def _tokenize_text(
        self, model_specifier: AnyModelSpecifier, input: str
    ) -> Sequence[int]:
        params = EmbeddingRpcTokenizeParameter._from_api_dict(
            {
                "specifier": _model_spec_to_api_dict(model_specifier),
                "inputString": input,
            }
        )
        response = self.remote_call("tokenize", params)
        return response.get("tokens", []) if response else []

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    def _tokenize(
        self, model_specifier: AnyModelSpecifier, input: str | Iterable[str]
    ) -> Sequence[int] | Sequence[Sequence[int]]:
        """Tokenize the input string(s) using the specified model."""
        if isinstance(input, str):
            return self._tokenize_text(model_specifier, input)
        return [self._tokenize_text(model_specifier, i) for i in input]

    @abstractmethod
    def _create_handle(self, model_identifier: str) -> TModelHandle:
        """Get a symbolic handle to the specified model."""
        ...

    @sdk_public_api()
    def model(
        self,
        model_key: str | None = None,
        /,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TModelHandle:
        """Get a handle to the specified model (loading it if necessary)."""
        if model_key is None:
            # Should this raise an error if a config is supplied?
            return self._get_any()
        return self._get_or_load(model_key, ttl, config, on_load_progress)

    @sdk_public_api()
    def list_loaded(self) -> Sequence[TModelHandle]:
        """Get the list of currently loaded models."""
        models = self.remote_call("listLoaded")
        return [self._create_handle(m["identifier"]) for m in models]

    @sdk_public_api()
    def unload(self, model_identifier: str) -> None:
        """Unload the specified model."""
        params = self._API_TYPES.REQUEST_UNLOAD(identifier=model_identifier)
        self.remote_call("unloadModel", params)

    # N.B. Canceling a load from the UI doesn't update the load process for a while.
    # Fortunately, this is not our fault. The server just delays in broadcasting it.
    @sdk_public_api()
    def load_new_instance(
        self,
        model_key: str,
        instance_identifier: str | None = None,
        *,
        ttl: int | None = DEFAULT_TTL,
        config: TLoadConfig | TLoadConfigDict | None = None,
        on_load_progress: ModelLoadingCallback | None = None,
    ) -> TModelHandle:
        """Load the specified model with the given identifier and configuration."""
        return self._load_new_instance(
            model_key, instance_identifier, ttl, config, on_load_progress
        )

    def _load_new_instance(
        self,
        model_key: str,
        instance_identifier: str | None,
        ttl: int | None,
        config: TLoadConfig | TLoadConfigDict | None,
        on_load_progress: ModelLoadingCallback | None,
    ) -> TModelHandle:
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
        with self._create_channel(endpoint) as channel:
            result = channel.wait_for_result()
            return self._create_handle(result.identifier)

    def _get_or_load(
        self,
        model_key: str,
        ttl: int | None,
        config: TLoadConfig | TLoadConfigDict | None,
        on_load_progress: ModelLoadingCallback | None,
    ) -> TModelHandle:
        """Get the specified model if it is already loaded, otherwise load it."""
        channel_type = self._API_TYPES.REQUEST_GET_OR_LOAD
        config_type = self._API_TYPES.MODEL_LOAD_CONFIG
        endpoint = GetOrLoadEndpoint(
            model_key, ttl, channel_type, config_type, config, on_load_progress
        )
        with self._create_channel(endpoint) as channel:
            result = channel.wait_for_result()
            return self._create_handle(result.identifier)

    def _get_any(self) -> TModelHandle:
        """Get a handle to any loaded model."""
        loaded_models = self.list_loaded()
        if not loaded_models:
            raise LMStudioClientError(
                f"Could not get model handle in namespace {self.API_NAMESPACE} (no models are currently loaded)."
            )
        return self._create_handle(loaded_models[0].identifier)

    @classmethod
    def _is_relevant_model(cls, model: AnyDownloadedModel) -> TypeIs[TDownloadedModel]:
        return bool(model.type == cls.API_NAMESPACE)

    @sdk_public_api()
    def list_downloaded(self) -> Sequence[TDownloadedModel]:
        """Get the list of currently downloaded models that are available for loading."""
        models = self._system_session.list_downloaded_models()
        return [m for m in models if self._is_relevant_model(m)]

    def _fetch_file_handle(self, file_data: _LocalFileData) -> _FileHandle:
        return self._files_session._fetch_file_handle(file_data)


SyncPredictionChannel: TypeAlias = SyncChannel[PredictionResult[T]]
SyncPredictionCM: TypeAlias = ContextManager[SyncPredictionChannel[T]]


class PredictionStream(PredictionStreamBase[TPrediction]):
    """Sync context manager for an ongoing prediction process."""

    def __init__(
        self,
        channel_cm: SyncPredictionCM[TPrediction],
        endpoint: PredictionEndpoint[TPrediction],
    ) -> None:
        """Initialize a prediction process representation."""
        self._resources = ExitStack()
        self._channel_cm: SyncPredictionCM[TPrediction] = channel_cm
        self._channel: SyncPredictionChannel[TPrediction] | None = None
        # See comments in BasePrediction regarding not calling super().__init__() here
        self._init_prediction(endpoint)

    @sdk_public_api()
    def start(self) -> None:
        """Send the prediction request."""
        if self._is_finished:
            raise LMStudioRuntimeError("Prediction result has already been received.")
        if self._is_started:
            raise LMStudioRuntimeError("Prediction request has already been sent.")
        # The given channel context manager is set up to send the relevant request
        self._channel = self._resources.enter_context(self._channel_cm)
        self._mark_started()

    @sdk_public_api()
    def close(self) -> None:
        """Terminate the prediction processing (if not already terminated)."""
        # Cancel the prediction (if unfinished) and release acquired resources
        if self._is_started and not self._is_finished:
            self._set_error(
                LMStudioCancelledError(
                    "Prediction cancelled unexpectedly: please use .cancel()"
                )
            )
        self._channel = None
        self._resources.close()

    def __enter__(self) -> Self:
        if self._channel is None:
            self.start()
        return self

    def __exit__(
        self,
        _exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        if exc_val and not self._is_finished:
            self._set_error(exc_val)
        self.close()

    def __iter__(self) -> Iterator[LlmPredictionFragment]:
        for event in self._iter_events():
            if isinstance(event, PredictionFragmentEvent):
                yield event.arg

    def _iter_events(self) -> Iterator[PredictionRxEvent]:
        endpoint = self._endpoint
        with self:
            assert self._channel is not None
            for contents in self._channel.rx_stream():
                for event in endpoint.iter_message_events(contents):
                    endpoint.handle_rx_event(event)
                    yield event
                if endpoint.is_finished:
                    break
            self._mark_finished()

    @sdk_public_api()
    def wait_for_result(self) -> PredictionResult[TPrediction]:
        """Wait for the result of the prediction."""
        for _ in self:
            pass
        return self.result()

    @sdk_public_api()
    def cancel(self) -> None:
        """Cancel the prediction process."""
        if not self._is_finished and self._channel:
            self._mark_cancelled()
            self._channel.cancel()


class SyncSessionLlm(
    SyncSessionModel[
        "LLM",
        LlmLoadModelConfig,
        LlmLoadModelConfigDict,
        DownloadedLlm,
    ]
):
    """Sync client session for LLM namespace."""

    API_NAMESPACE = "llm"
    _API_TYPES = ModelTypesLlm

    def __init__(self, client: "Client") -> None:
        """Initialize API client session for LLM interaction."""
        super().__init__(client)

    def _create_handle(self, model_identifier: str) -> "LLM":
        """Create a symbolic handle to the specified LLM model."""
        return LLM(model_identifier, self)

    @overload
    def _complete_stream(
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
    ) -> PredictionStream[str]: ...
    @overload
    def _complete_stream(
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
    ) -> PredictionStream[DictObject]: ...
    def _complete_stream(
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
    ) -> PredictionStream[str] | PredictionStream[DictObject]:
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
        prediction_stream = PredictionStream(channel_cm, endpoint)
        return prediction_stream

    @overload
    def _respond_stream(
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
    ) -> PredictionStream[str]: ...
    @overload
    def _respond_stream(
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
    ) -> PredictionStream[DictObject]: ...
    def _respond_stream(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionStream[str] | PredictionStream[DictObject]:
        """Request a response in an ongoing assistant chat session and stream the generated tokens."""
        if not isinstance(history, Chat):
            history = Chat.from_history(history)
        history._fetch_file_handles(self._fetch_file_handle)
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
        prediction_stream = PredictionStream(channel_cm, endpoint)
        return prediction_stream

    def _apply_prompt_template(
        self,
        model_specifier: AnyModelSpecifier,
        history: Chat | ChatHistoryDataDict | str,
        opts: LlmApplyPromptTemplateOpts | LlmApplyPromptTemplateOptsDict = {},
    ) -> str:
        """Apply a prompt template to the given history."""
        if not isinstance(history, Chat):
            history = Chat.from_history(history)
        history._fetch_file_handles(self._fetch_file_handle)
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
        response = self.remote_call("applyPromptTemplate", params)
        return response.get("formatted", "") if response else ""


class SyncSessionEmbedding(
    SyncSessionModel[
        "EmbeddingModel",
        EmbeddingLoadModelConfig,
        EmbeddingLoadModelConfigDict,
        DownloadedEmbeddingModel,
    ]
):
    """Sync client session for embedding namespace."""

    API_NAMESPACE = "embedding"
    _API_TYPES = ModelTypesEmbedding

    def __init__(self, client: "Client") -> None:
        """Initialize API client session for embedding model interaction."""
        super().__init__(client)

    def _create_handle(self, model_identifier: str) -> "EmbeddingModel":
        """Create a symbolic handle to the specified embedding model."""
        return EmbeddingModel(model_identifier, self)

    # Private helper method to allow the main API to easily accept iterables
    def _embed_text(
        self, model_specifier: AnyModelSpecifier, input: str
    ) -> Sequence[float]:
        params = EmbeddingRpcEmbedStringParameter._from_api_dict(
            {
                "modelSpecifier": _model_spec_to_api_dict(model_specifier),
                "inputString": input,
            }
        )

        response = self.remote_call("embedString", params)
        return response.get("embedding", []) if response else []

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    def _embed(
        self, model_specifier: AnyModelSpecifier, input: str | Iterable[str]
    ) -> Sequence[float] | Sequence[Sequence[float]]:
        """Request embedding vectors for the given input string(s)."""
        if isinstance(input, str):
            return self._embed_text(model_specifier, input)
        return [self._embed_text(model_specifier, i) for i in input]


class SyncModelHandle(ModelHandleBase[TSyncSessionModel]):
    """Reference to a loaded LM Studio model."""

    @sdk_public_api()
    def unload(self) -> None:
        """Unload this model."""
        self._session.unload(self.identifier)

    @sdk_public_api()
    def get_info(self) -> ModelInstanceInfo:
        """Get the model info for this model."""
        return self._session.get_model_info(self.identifier)

    # Private until this API can emit the client config types
    @sdk_public_api()
    def _get_load_config(self) -> DictObject:
        """Get the model load config for this model."""
        return self._session._get_load_config(self.identifier)

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    @sdk_public_api()
    def tokenize(
        self, input: str | Iterable[str]
    ) -> Sequence[int] | Sequence[Sequence[int]]:
        """Tokenize the input string(s) using this model."""
        return self._session._tokenize(self.identifier, input)

    @sdk_public_api()
    def get_context_length(self) -> int:
        """Get the context length of this model."""
        return self._session._get_context_length(self.identifier)


AnySyncModel: TypeAlias = SyncModelHandle[Any]


class LLM(SyncModelHandle[SyncSessionLlm]):
    """Reference to a loaded LLM model."""

    @overload
    def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionStream[str]: ...
    @overload
    def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionStream[DictObject]: ...
    @sdk_public_api()
    def complete_stream(
        self,
        prompt: str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionStream[str] | PredictionStream[DictObject]:
        """Request a one-off prediction without any context and stream the generated tokens."""
        return self._session._complete_stream(
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
    def complete(
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
    def complete(
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
    @sdk_public_api()
    def complete(
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
        prediction_stream = self._session._complete_stream(
            self.identifier,
            prompt,
            response_format=response_format,
            config=config,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )
        for _ in prediction_stream:
            # No yield in body means iterator reliably provides
            # prompt resource cleanup on coroutine cancellation
            pass
        return prediction_stream.result()

    @overload
    def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Literal[None] = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionStream[str]: ...
    @overload
    def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema = ...,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = ...,
        on_message: PredictionMessageCallback | None = ...,
        on_first_token: PredictionFirstTokenCallback | None = ...,
        on_prediction_fragment: PredictionFragmentCallback | None = ...,
        on_prompt_processing_progress: PromptProcessingCallback | None = ...,
    ) -> PredictionStream[DictObject]: ...
    @sdk_public_api()
    def respond_stream(
        self,
        history: Chat | ChatHistoryDataDict | str,
        *,
        response_format: Type[ModelSchema] | DictSchema | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
        on_message: PredictionMessageCallback | None = None,
        on_first_token: PredictionFirstTokenCallback | None = None,
        on_prediction_fragment: PredictionFragmentCallback | None = None,
        on_prompt_processing_progress: PromptProcessingCallback | None = None,
    ) -> PredictionStream[str] | PredictionStream[DictObject]:
        """Request a response in an ongoing assistant chat session and stream the generated tokens."""
        return self._session._respond_stream(
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
    def respond(
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
    def respond(
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
    @sdk_public_api()
    def respond(
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
        prediction_stream = self._session._respond_stream(
            self.identifier,
            history,
            response_format=response_format,
            config=config,
            on_message=on_message,
            on_first_token=on_first_token,
            on_prediction_fragment=on_prediction_fragment,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )
        for _ in prediction_stream:
            # No yield in body means iterator reliably provides
            # prompt resource cleanup on coroutine cancellation
            pass
        return prediction_stream.result()

    # Multi-round predictions are currently a sync-only handle-only feature
    # TODO: Refactor to allow for more code sharing with the async API
    #       with defined aliases for the expected callback signatures
    @sdk_public_api()
    def act(
        self,
        chat: Chat | ChatHistoryDataDict | str,
        tools: Iterable[ToolDefinition],
        *,
        max_prediction_rounds: int | None = None,
        config: LlmPredictionConfig | LlmPredictionConfigDict | None = None,
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
            [LMStudioPredictionError, ToolCallRequest | None], str
        ]
        | None = None,
    ) -> ActResult:
        """Request a response (with implicit tool use) in an ongoing agent chat session."""
        start_time = time.perf_counter()
        # It is not yet possible to combine tool calling with requests for structured responses
        response_format = None
        if isinstance(chat, Chat):
            chat._fetch_file_handles(self._session._fetch_file_handle)
        agent_chat: Chat = Chat.from_history(chat)
        del chat
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
        llm_tool_args = ChatResponseEndpoint.parse_tools(tools)
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
        # Request predictions until no more tool call requests are received in response
        # (or the maximum number of prediction rounds is reached)
        with ThreadPoolExecutor() as pool:
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
                    None,  # Multiple messages are generated per round
                    on_first_token_for_endpoint,
                    on_prediction_fragment_for_endpoint,
                    on_prompt_processing_for_endpoint,
                    handle_invalid_tool_request,
                    *(
                        llm_tool_args
                        if round_index != final_round_index
                        else (None, None)
                    ),
                )
                channel_cm = self._session._create_channel(endpoint)
                prediction_stream = PredictionStream(channel_cm, endpoint)
                tool_call_requests: list[ToolCallRequest] = []
                pending_tool_calls: list[SyncFuture[Any]] = []
                for event in prediction_stream._iter_events():
                    if isinstance(event, PredictionToolCallEvent):
                        tool_call_request = event.arg
                        tool_call_requests.append(tool_call_request)
                        tool_call = endpoint.request_tool_call(tool_call_request)
                        pending_tool_calls.append(pool.submit(tool_call))
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
                if pending_tool_calls:
                    tool_results = [
                        fut.result() for fut in as_completed(pending_tool_calls)
                    ]
                    requests_message = agent_chat.add_assistant_response(
                        prediction, tool_call_requests
                    )
                    results_message = agent_chat.add_tool_results(tool_results)
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

    @sdk_public_api()
    def apply_prompt_template(
        self,
        history: Chat | ChatHistoryDataDict | str,
        opts: LlmApplyPromptTemplateOpts | LlmApplyPromptTemplateOptsDict = {},
    ) -> str:
        """Apply a prompt template to the given history."""
        return self._session._apply_prompt_template(
            self.identifier,
            history,
            opts=opts,
        )


class EmbeddingModel(SyncModelHandle[SyncSessionEmbedding]):
    """Reference to a loaded embedding model."""

    # Alas, type hints don't properly support distinguishing str vs Iterable[str]:
    #     https://github.com/python/typing/issues/256
    @sdk_public_api()
    def embed(
        self, input: str | Iterable[str]
    ) -> Sequence[float] | Sequence[Sequence[float]]:
        """Request embedding vectors for the given input string(s)."""
        return self._session._embed(self.identifier, input)


TSyncSession = TypeVar("TSyncSession", bound=SyncSession)


class Client(ClientBase):
    """Synchronous SDK client interface."""

    def __init__(self, api_host: str | None = None) -> None:
        """Initialize API client."""
        super().__init__(api_host)
        self._resources = rm = ExitStack()
        self._sessions: dict[str, SyncSession] = {}
        # Suport GC-based resource management in the sync API by
        # finalizing at the client layer, and letting its resource
        # manager handle clearing up everything else
        rm.callback(self._sessions.clear)
        weakref.finalize(self, rm.close)

    def __enter__(self) -> Self:
        # Handle reentrancy the same way files do:
        # allow nested use as a CM, but close on the first exit
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close any started client sessions."""
        self._resources.close()

    # Doing network I/O in properties is generally considered undesirable.
    # The async API can't perform network I/O in properties at all.
    # Unlike the async API (which follows the principles of structured
    # concurrency), the sync API can resolve this by delaying the creation
    # of the underlying websockets until they're actually used.

    def _get_session(self, cls: Type[TSyncSession]) -> TSyncSession:
        """Get the client session of the given type."""
        namespace = cls.API_NAMESPACE
        assert namespace is not None
        try:
            session = self._sessions[namespace]
        except KeyError:
            pass
        else:
            # This *will* be an instance of the given type.
            # The assertion notifies typecheckers of that.
            assert isinstance(session, cls)
            return session
        # No session yet for this namespace, so create one
        session = cls(self)
        self._sessions[namespace] = session
        # Note: session starts itself on first use rather than immediately
        # We push the exit callback here so that only the client itself
        # needs to be explicitly managed as a context manager. Directly
        # managing the individual session is supported, but not required.
        self._resources.push(session)
        return session

    @property
    @sdk_public_api()
    def llm(self) -> SyncSessionLlm:
        """Return the LLM API client session."""
        return self._get_session(SyncSessionLlm)

    @property
    @sdk_public_api()
    def embedding(self) -> SyncSessionEmbedding:
        """Return the embedding model API client session."""
        return self._get_session(SyncSessionEmbedding)

    @property
    def system(self) -> SyncSessionSystem:
        """Return the system API client session."""
        return self._get_session(SyncSessionSystem)

    @property
    def _files(self) -> _SyncSessionFiles:
        """Return the files API client session."""
        # Private until LM Studio file handle support stabilizes
        return self._get_session(_SyncSessionFiles)

    @property
    def repository(self) -> SyncSessionRepository:
        """Return the repository API client session."""
        return self._get_session(SyncSessionRepository)

    # Convenience methods
    @sdk_public_api()
    def _add_temp_file(
        self, src: _FileInputType, name: str | None = None
    ) -> _FileHandle:
        """Add a file to the server."""
        # Private until LM Studio file handle support stabilizes
        return self._files._add_temp_file(src, name)

    @sdk_public_api()
    def list_downloaded_models(
        self, namespace: str | None = None
    ) -> Sequence[AnyDownloadedModel]:
        """Get the list of downloaded models."""
        namespace_filter = check_model_namespace(namespace)
        if namespace_filter is None:
            return self.system.list_downloaded_models()
        if namespace_filter == "llm":
            return self.llm.list_downloaded()
        return self.embedding.list_downloaded()

    @sdk_public_api()
    def list_loaded_models(
        self, namespace: str | None = None
    ) -> Sequence[AnySyncModel]:
        """Get the list of loaded models using the default global client."""
        namespace_filter = check_model_namespace(namespace)
        loaded_models: list[AnySyncModel] = []
        if namespace_filter is None or namespace_filter == "llm":
            loaded_models.extend(self.llm.list_loaded())
        if namespace_filter is None or namespace_filter == "embedding":
            loaded_models.extend(self.embedding.list_loaded())
        return loaded_models


# Convenience API
_default_client: Client | None = None


@sdk_public_api()
def get_default_client(api_host: str | None = None) -> Client:
    """Get the default global client (creating it if necessary)."""
    global _default_client
    if _default_client is None:
        _default_client = Client(api_host)
    elif api_host is not None:
        raise LMStudioClientError(
            "Default session already connected, cannot set API host."
        )
    return _default_client


@sdk_public_api()
def llm(
    model_key: str | None = None,
    /,
    *,
    ttl: int | None = DEFAULT_TTL,
    config: LlmLoadModelConfig | LlmLoadModelConfigDict | None = None,
) -> LLM:
    """Access an LLM using the default global client."""
    return get_default_client().llm.model(model_key, ttl=ttl, config=config)


@sdk_public_api()
def embedding_model(
    model_key: str | None = None,
    /,
    *,
    ttl: int | None = DEFAULT_TTL,
    config: EmbeddingLoadModelConfig | EmbeddingLoadModelConfigDict | None = None,
) -> EmbeddingModel:
    """Access an embedding model using the default global client."""
    return get_default_client().embedding.model(model_key, ttl=ttl, config=config)


@sdk_public_api()
def _add_temp_file(src: _FileInputType, name: str | None = None) -> _FileHandle:
    """Add a file to the server using the default global client."""
    # Private until LM Studio file handle support stabilizes
    return get_default_client()._add_temp_file(src, name)


@sdk_public_api()
def list_downloaded_models(
    namespace: str | None = None,
) -> Sequence[AnyDownloadedModel]:
    """Get the list of downloaded models using the default global client."""
    return get_default_client().list_downloaded_models(namespace)


@sdk_public_api()
def list_loaded_models(namespace: str | None = None) -> Sequence[AnySyncModel]:
    """Get the list of loaded models using the default global client."""
    return get_default_client().list_loaded_models(namespace)
