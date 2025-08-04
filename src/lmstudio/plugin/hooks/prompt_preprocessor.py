"""Invoking and supporting prompt preprocessor hook implementations."""

import asyncio

from contextlib import asynccontextmanager
from dataclasses import dataclass
from traceback import format_tb
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    TypeAlias,
)
from typing_extensions import (
    # Native in 3.11+
    assert_never,
)

from anyio import create_task_group
from anyio.abc import TaskGroup

from ..._logging import new_logger
from ...schemas import DictObject, EmptyDict, ValidationError
from ...history import UserMessage, UserMessageDict
from ...json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    SendMessageAsync,
    load_struct,
)
from ..._sdk_models import (
    PluginsRpcProcessingHandleUpdateParameter,
    ProcessingUpdate,
    ProcessingUpdateStatusCreate,
    ProcessingUpdateStatusUpdate,
    PromptPreprocessingAbortedDict,
    PromptPreprocessingCompleteDict,
    PromptPreprocessingErrorDict,
    PromptPreprocessingRequest,
    SerializedLMSExtendedErrorDict,
    StatusStepState,
    StatusStepStatus,
)
from ..config_schemas import BaseConfigSchema
from .common import (
    _AsyncSessionPlugins,
    HookController,
    ServerRequestError,
    StatusBlockController,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "PromptPreprocessorController",
    "PromptPreprocessorHook",
    "run_prompt_preprocessor",
]


class PromptPreprocessingAbortEvent(ChannelRxEvent[str]):
    pass


class PromptPreprocessingRequestEvent(ChannelRxEvent[PromptPreprocessingRequest]):
    pass


PromptPreprocessingRxEvent: TypeAlias = (
    PromptPreprocessingAbortEvent
    | PromptPreprocessingRequestEvent
    | ChannelCommonRxEvent
)


class PromptPreprocessingEndpoint(
    ChannelEndpoint[tuple[str, str], PromptPreprocessingRxEvent, EmptyDict]
):
    """API channel endpoint to accept prompt preprocessing requests."""

    _API_ENDPOINT = "setPromptPreprocessor"
    _NOTICE_PREFIX = "Prompt preprocessing"

    def __init__(self) -> None:
        super().__init__({})

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[PromptPreprocessingRxEvent]:
        match contents:
            case None:
                # Server can only terminate the link by closing the websocket
                pass
            case {"type": "abort", "taskId": str(task_id)}:
                yield PromptPreprocessingAbortEvent(task_id)
            case {"type": "preprocess"} as request_dict:
                parsed_request = PromptPreprocessingRequest._from_any_api_dict(
                    request_dict
                )
                yield PromptPreprocessingRequestEvent(parsed_request)
            case unmatched:
                self.report_unknown_message(unmatched)

    def handle_rx_event(self, event: PromptPreprocessingRxEvent) -> None:
        match event:
            case PromptPreprocessingAbortEvent(task_id):
                self._logger.debug(f"Aborting {task_id}", task_id=task_id)
            case PromptPreprocessingRequestEvent(request):
                task_id = request.task_id
                self._logger.debug(
                    "Received prompt preprocessing request", task_id=task_id
                )
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)


class PromptPreprocessorController(
    HookController[PromptPreprocessingRequest, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for prompt preprocessor hook implementations."""

    def __init__(
        self,
        session: _AsyncSessionPlugins,
        request: PromptPreprocessingRequest,
        plugin_config_schema: type[TPluginConfigSchema],
        global_config_schema: type[TGlobalConfigSchema],
    ) -> None:
        """Initialize prompt preprocessor hook controller."""
        super().__init__(session, request, plugin_config_schema, global_config_schema)
        self.task_id = request.task_id
        self.pci = request.pci
        self.token = request.token

    async def _send_handle_update(self, update: ProcessingUpdate) -> Any:
        handle_update = PluginsRpcProcessingHandleUpdateParameter(
            pci=self.pci,
            token=self.token,
            update=update,
        )
        return await self.session.remote_call("processingHandleUpdate", handle_update)

    async def _create_status_block(
        self, block_id: str, status: StatusStepStatus, message: str
    ) -> None:
        await self._send_handle_update(
            ProcessingUpdateStatusCreate(
                id=block_id,
                state=StatusStepState(
                    status=status,
                    text=message,
                ),
            ),
        )

    async def _send_status_update(
        self, block_id: str, status: StatusStepStatus, message: str
    ) -> None:
        await self._send_handle_update(
            ProcessingUpdateStatusUpdate(
                id=block_id,
                state=StatusStepState(
                    status=status,
                    text=message,
                ),
            ),
        )

    async def notify_start(self, message: str) -> StatusBlockController:
        """Report task initiation in a new UI status block, return controller for updates."""
        status_block = StatusBlockController(
            self._create_ui_block_id(),
            self._send_status_update,
        )
        await self._create_status_block(status_block._id, "waiting", message)
        return status_block

    async def notify_done(self, message: str) -> None:
        """Report task completion in a new UI status block."""
        await self._create_status_block(self._create_ui_block_id(), "done", message)


PromptPreprocessorHook = Callable[
    [PromptPreprocessorController[Any, Any], UserMessage],
    Awaitable[UserMessage | UserMessageDict | None],
]


# TODO: Define a common "PluginHookHandler" base class
@dataclass()
class PromptPreprocessor(Generic[TPluginConfigSchema, TGlobalConfigSchema]):
    """Handle accepting prompt preprocessing requests."""

    plugin_name: str
    hook_impl: PromptPreprocessorHook
    plugin_config_schema: type[TPluginConfigSchema]
    global_config_schema: type[TGlobalConfigSchema]

    def __post_init__(self) -> None:
        self._logger = logger = new_logger(__name__)
        logger.update_context(plugin_name=self.plugin_name)
        self._abort_events: dict[str, asyncio.Event] = {}

    async def process_requests(
        self, session: _AsyncSessionPlugins, notify_ready: Callable[[], Any]
    ) -> None:
        """Create plugin channel and wait for server requests."""
        logger = self._logger
        endpoint = PromptPreprocessingEndpoint()
        # Async API expects timeouts to be handled via task groups,
        # so there's no default timeout to override when creating the channel
        async with session._create_channel(endpoint) as channel:
            notify_ready()
            logger.info("Opened channel to receive prompt preprocessing requests...")
            send_message = channel.send_message
            async with create_task_group() as tg:
                logger.debug("Waiting for prompt preprocessing requests...")
                async for contents in channel.rx_stream():
                    logger.debug(
                        f"Handling prompt preprocessing channel message: {contents}"
                    )
                    for event in endpoint.iter_message_events(contents):
                        logger.debug("Handling prompt preprocessing channel event")
                        endpoint.handle_rx_event(event)
                        match event:
                            case PromptPreprocessingAbortEvent():
                                await self._abort_hook_invocation(
                                    event.arg, send_message
                                )
                            case PromptPreprocessingRequestEvent():
                                logger.debug(
                                    "Running prompt preprocessing request hook"
                                )
                                ctl = PromptPreprocessorController(
                                    session,
                                    event.arg,
                                    self.plugin_config_schema,
                                    self.global_config_schema,
                                )
                                tg.start_soon(self._invoke_hook, ctl, send_message)
                    if endpoint.is_finished:
                        break

    async def _abort_hook_invocation(
        self, task_id: str, send_json: SendMessageAsync
    ) -> None:
        """Abort the specified hook invocation (if it is still running)."""
        abort_event = self._abort_events.get(task_id, None)
        if abort_event is not None:
            abort_event.set()
        response = PromptPreprocessingAbortedDict(
            type="aborted",
            taskId=task_id,
        )
        await send_json(response)

    async def _cancel_on_event(
        self, tg: TaskGroup, event: asyncio.Event, message: str
    ) -> None:
        await event.wait()
        self._logger.info(message)
        tg.cancel_scope.cancel()

    @asynccontextmanager
    async def _registered_hook_invocation(
        self, task_id: str
    ) -> AsyncIterator[asyncio.Event]:
        logger = self._logger
        abort_events = self._abort_events
        if task_id in abort_events:
            err_msg = f"Hook invocation already in progress for {task_id}"
            raise ServerRequestError(err_msg)
        abort_events[task_id] = abort_event = asyncio.Event()
        try:
            async with create_task_group() as tg:
                tg.start_soon(
                    self._cancel_on_event,
                    tg,
                    abort_event,
                    f"Aborting request {task_id}",
                )
                logger.info(f"Processing request {task_id}")
                yield abort_event
                tg.cancel_scope.cancel()
        finally:
            abort_events.pop(task_id, None)
        if abort_event.is_set():
            completion_message = f"Aborted request {task_id}"
        else:
            completion_message = f"Processed request {task_id}"
        logger.info(completion_message)

    async def _invoke_hook(
        self,
        ctl: PromptPreprocessorController[TPluginConfigSchema, TGlobalConfigSchema],
        send_json: SendMessageAsync,
    ) -> None:
        logger = self._logger
        task_id = ctl.task_id
        message = ctl.request.input
        error_details: SerializedLMSExtendedErrorDict | None = None
        response_dict: UserMessageDict
        expected_cls = UserMessage
        try:
            if not isinstance(message, expected_cls):
                err_msg = f"Received {type(message).__name__!r} ({expected_cls.__name__!r} expected)"
                raise ServerRequestError(err_msg)
            async with self._registered_hook_invocation(task_id) as abort_event:
                response = await self.hook_impl(ctl, message)
        except Exception as exc:
            err_msg = "Error calling prompt preprocessing hook"
            logger.error(err_msg, exc_info=True, exc=repr(exc))
            # TODO: Determine if it's worth sending the stack trace to the server
            ui_cause = f"{err_msg}\n({type(exc).__name__}: {exc})"
            error_details = SerializedLMSExtendedErrorDict(
                cause=ui_cause, stack="\n".join(format_tb(exc.__traceback__))
            )
        else:
            if abort_event.is_set():
                # Processing was aborted by the server, skip sending a response
                return
            if response is None:
                logger.debug("No changes made to preprocessed prompt")
                response_dict = message.to_dict()
            else:
                logger.debug(
                    "Validating prompt preprocessing response", response=response
                )
                if isinstance(response, dict):
                    try:
                        parsed_response = load_struct(response, expected_cls)
                    except ValidationError as exc:
                        err_msg = f"Failed to parse prompt preprocessing response as {expected_cls.__name__}\n({exc})"
                        logger.error(err_msg)
                        error_details = SerializedLMSExtendedErrorDict(cause=err_msg)
                    else:
                        response_dict = parsed_response.to_dict()
                elif isinstance(response, UserMessage):
                    response_dict = response.to_dict()
                else:
                    err_msg = f"Prompt preprocessing hook returned {type(response).__name__!r} ({expected_cls.__name__!r} expected)"
                    logger.error(err_msg)
                    error_details = SerializedLMSExtendedErrorDict(cause=err_msg)
        channel_message: DictObject
        if error_details is not None:
            error_title = f"Prompt preprocessing error in plugin {self.plugin_name!r}"
            common_error_args: SerializedLMSExtendedErrorDict = {
                "title": error_title,
                "rootTitle": error_title,
            }
            error_details.update(common_error_args)
            channel_message = PromptPreprocessingErrorDict(
                type="error",
                taskId=task_id,
                error=error_details,
            )
        else:
            channel_message = PromptPreprocessingCompleteDict(
                type="complete",
                taskId=task_id,
                processed=response_dict,
            )
        await send_json(channel_message)


async def run_prompt_preprocessor(
    plugin_name: str,
    hook_impl: PromptPreprocessorHook,
    plugin_config_schema: type[BaseConfigSchema],
    global_config_schema: type[BaseConfigSchema],
    session: _AsyncSessionPlugins,
    notify_ready: Callable[[], Any],
) -> None:
    """Accept prompt preprocessing requests."""
    prompt_preprocessor = PromptPreprocessor(
        plugin_name, hook_impl, plugin_config_schema, global_config_schema
    )
    await prompt_preprocessor.process_requests(session, notify_ready)
