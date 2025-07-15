"""Invoking and supporting prompt preprocessor hook implementations."""

from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    TypeAlias,
    assert_never,
)

from anyio import create_task_group

from ...schemas import DictObject, EmptyDict
from ...history import AnyChatMessage, AnyChatMessageDict
from ...json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    LMStudioChannelClosedError,
)
from ..._sdk_models import (
    PluginsRpcProcessingHandleUpdateParameter,
    ProcessingUpdate,
    ProcessingUpdateStatusCreate,
    ProcessingUpdateStatusUpdate,
    PromptPreprocessingCompleteDict,
    PromptPreprocessingRequest,
    StatusStepState,
    StatusStepStatus,
)
from ..config_schemas import BaseConfigSchema
from .common import AsyncSessionPlugins, HookController, StatusBlockController


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
    """API channel endpoint to register a development plugin and receive credentials."""

    _API_ENDPOINT = "setPromptPreprocessor"
    _NOTICE_PREFIX = "Prompt preprocessing"

    def __init__(self) -> None:
        super().__init__({})

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[PromptPreprocessingRxEvent]:
        match contents:
            case None:
                raise LMStudioChannelClosedError(
                    "Server failed to complete development plugin registration."
                )
            case {"type": "abort", "task_id": str(task_id)}:
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
                self._logger.info(f"Aborting {task_id}", task_id=task_id)
            case PromptPreprocessingRequestEvent(request):
                task_id = request.task_id
                self._logger.info(
                    "Received prompt preprocessing request", task_id=task_id
                )
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)


class PromptPreprocessorController(HookController[PromptPreprocessingRequest]):
    """API access for prompt preprocessor hook implementations."""

    def __init__(
        self,
        session: AsyncSessionPlugins,
        request: PromptPreprocessingRequest,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> None:
        """Initialize prompt preprocessor hook controller."""
        super().__init__(session, request, plugin_config)
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
    [PromptPreprocessorController, AnyChatMessage], Awaitable[AnyChatMessageDict | None]
]


async def run_prompt_preprocessor(
    hook_impl: PromptPreprocessorHook,
    plugin_config: type[BaseConfigSchema] | None,
    session: AsyncSessionPlugins,
    notify_ready: Callable[[], Any],
) -> None:
    """Accept prompt preprocessing requests."""
    endpoint = PromptPreprocessingEndpoint()
    async with session._create_channel(endpoint) as channel:
        notify_ready()
        print("Opened channel to receive prompt preprocessing requests...")

        async def _invoke_hook(request: PromptPreprocessingRequest) -> None:
            message = request.input
            hook_controller = PromptPreprocessorController(
                session, request, plugin_config
            )
            # TODO once stable: use sdk_api_callback context manager
            response = await hook_impl(hook_controller, message)
            if response is None:
                response = message.to_dict()
            await channel.send_message(
                PromptPreprocessingCompleteDict(
                    type="complete",
                    taskId=request.task_id,
                    processed=response,
                )
            )

        async with create_task_group() as tg:
            print("Waiting for prompt preprocessing requests...")
            async for contents in channel.rx_stream():
                print(f"Handling prompt preprocessing channel message: {contents}")
                for event in endpoint.iter_message_events(contents):
                    print("Handling prompt preprocessing channel event")
                    endpoint.handle_rx_event(event)
                    match event:
                        case PromptPreprocessingRequestEvent():
                            print("Running prompt preprocessing request hook")
                            tg.start_soon(_invoke_hook, event.arg)
                if endpoint.is_finished:
                    break
