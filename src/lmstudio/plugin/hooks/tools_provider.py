"""Invoking and supporting tools provider hook implementations."""

import asyncio

from dataclasses import dataclass
from traceback import format_tb
from typing import Any, Awaitable, Callable, Generic, Iterable, TypeAlias, TypeVar
from typing_extensions import (
    # Native in 3.11+
    assert_never,
)

from anyio import create_task_group
from anyio.abc import TaskGroup

from ..._logging import new_logger, LogEventContext
from ...schemas import DictObject, EmptyDict
from ...json_api import (
    ChannelCommonRxEvent,
    ChannelEndpoint,
    ChannelFinishedEvent,
    ChannelRxEvent,
    ChatResponseEndpoint,
    ToolDefinition,
)
from ..._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsChannelSetToolsProviderToClientPacketInitSession as ProvideToolsInitSession,
    PluginsChannelSetToolsProviderToClientPacketAbortToolCall as ProvideToolsAbortCall,
    PluginsChannelSetToolsProviderToClientPacketCallTool as ProvideToolsCallTool,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict as ProvideToolsInitFailedDict,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict as ProvideToolsInitializedDict,
    # "PluginsChannelSetToolsProviderToServerPacketToolCallComplete",
    # PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict as PluginToolCallCompleteDict,
    # "PluginsChannelSetToolsProviderToServerPacketToolCallError",
    # PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict as PluginToolCallErrorDict,
    # "PluginsChannelSetToolsProviderToServerPacketToolCallStatus",
    # PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict as PluginToolCallStatusDict,
    # "PluginsChannelSetToolsProviderToServerPacketToolCallWarn",
    # PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict as PluginToolCallWarnDict,
    SerializedLMSExtendedErrorDict,
)

from ..config_schemas import BaseConfigSchema
from .common import (
    _AsyncSessionPlugins,
    HookController,
    SendMessageCallback,
    ServerRequestError,
    TPluginConfigSchema,
    TGlobalConfigSchema,
)

# Available as lmstudio.plugin.hooks.*
__all__ = [
    "ToolsProviderController",
    "ToolsProviderHook",
    "run_tools_provider",
]


class ProvideToolsDiscardSessionEvent(ChannelRxEvent[str]):
    pass


class ProvideToolsInitSessionEvent(ChannelRxEvent[ProvideToolsInitSession]):
    pass


class ProvideToolsCallToolEvent(ChannelRxEvent[ProvideToolsCallTool]):
    pass


class ProvideToolsAbortCallEvent(ChannelRxEvent[ProvideToolsAbortCall]):
    pass


PromptPreprocessingRxEvent: TypeAlias = (
    ProvideToolsDiscardSessionEvent
    | ProvideToolsInitSessionEvent
    | ProvideToolsCallToolEvent
    | ProvideToolsAbortCallEvent
    | ChannelCommonRxEvent
)


class ToolsProviderEndpoint(
    ChannelEndpoint[tuple[str, str], PromptPreprocessingRxEvent, EmptyDict]
):
    """API channel endpoint to accept prompt preprocessing requests."""

    _API_ENDPOINT = "setToolsProvider"
    _NOTICE_PREFIX = "Providing tools"

    def __init__(self) -> None:
        super().__init__({})

    def iter_message_events(
        self, contents: DictObject | None
    ) -> Iterable[PromptPreprocessingRxEvent]:
        match contents:
            case None:
                # Server can only terminate the link by closing the websocket
                pass
            case {"type": "discardSession", "sessionId": str(session_id)}:
                yield ProvideToolsDiscardSessionEvent(session_id)
            case {"type": "initSession"} as init_session_dict:
                init_session = ProvideToolsInitSession._from_any_api_dict(
                    init_session_dict
                )
                yield ProvideToolsInitSessionEvent(init_session)
            case {"type": "callTool"} as tool_call_dict:
                tool_call = ProvideToolsCallTool._from_any_api_dict(tool_call_dict)
                yield ProvideToolsCallToolEvent(tool_call)
            case {"type": "abortToolCall"} as abort_tool_call_dict:
                abort_tool_call = ProvideToolsAbortCall._from_any_api_dict(
                    abort_tool_call_dict
                )
                yield ProvideToolsAbortCallEvent(abort_tool_call)
            case unmatched:
                self.report_unknown_message(unmatched)

    def handle_rx_event(self, event: PromptPreprocessingRxEvent) -> None:
        match event:
            case ProvideToolsDiscardSessionEvent(session_id):
                self._logger.debug(f"Terminating {session_id}", session_id=session_id)
            case ProvideToolsInitSessionEvent(request):
                self._logger.debug(
                    "Received tools session request", session_id=request.session_id
                )
            case ProvideToolsCallToolEvent(request):
                self._logger.debug(
                    "Received tool call request",
                    session_id=request.session_id,
                    call_id=request.call_id,
                )
            case ProvideToolsAbortCallEvent(request):
                self._logger.debug(
                    "Received tool abort request",
                    session_id=request.session_id,
                    call_id=request.call_id,
                )
            case ChannelFinishedEvent(_):
                pass
            case _:
                assert_never(event)


class ToolsProviderController(
    HookController[ProvideToolsInitSession, TPluginConfigSchema, TGlobalConfigSchema]
):
    """API access for tools provider hook implementations."""

    def __init__(
        self,
        session: _AsyncSessionPlugins,
        request: ProvideToolsInitSession,
        plugin_config_schema: type[TPluginConfigSchema],
        global_config_schema: type[TGlobalConfigSchema],
    ) -> None:
        """Initialize prompt preprocessor hook controller."""
        super().__init__(session, request, plugin_config_schema, global_config_schema)
        self.session_id = request.session_id


ToolsProviderHook = Callable[
    [ToolsProviderController[Any, Any]], Awaitable[Iterable[ToolDefinition]]
]

T = TypeVar("T")


class ToolCallHandler:
    def __init__(self, session_id: str, log_context: LogEventContext) -> None:
        self.session_id = session_id
        self._queue: asyncio.Queue[ProvideToolsCallTool | None] = asyncio.Queue()
        self._abort_events: dict[str, asyncio.Event] = {}
        self._logger = logger = new_logger(__name__)
        logger.update_context(log_context, session_id=session_id)

    async def _cancel_on_event(
        self, tg: TaskGroup, event: asyncio.Event, message: str
    ) -> None:
        await event.wait()
        self._logger.info(message)
        tg.cancel_scope.cancel()

    async def start_tool_call(self, tool_call: ProvideToolsCallTool) -> None:
        await self._queue.put(tool_call)

    async def _call_tool_implementation(self, tool_call: ProvideToolsCallTool) -> Any:
        # TODO: Share the tool invocation logic with the .act() API implementations
        # Note: synchronous tool calls must be run in asyncio.to_thread to avoid blocking
        # For now, placeholder sleep allows for manual testing of the tool call abort processing
        await asyncio.sleep(5)
        raise NotImplementedError

    async def _call_tool(
        self, tool_call: ProvideToolsCallTool, send_message: SendMessageCallback
    ) -> None:
        call_id = tool_call.call_id
        abort_events = self._abort_events
        if call_id in abort_events:
            err_msg = f"Tool call already in progress for {call_id} in session {self.session_id}"
            raise ServerRequestError(err_msg)
        abort_events[call_id] = abort_event = asyncio.Event()
        try:
            async with create_task_group() as tg:
                tg.start_soon(
                    self._cancel_on_event,
                    tg,
                    abort_event,
                    f"Aborting tool_call {call_id}",
                )
                self._logger.info(f"Running tool call {call_id}")
                # TODO: Set up context variable for status/warning message sending
                await self._call_tool_implementation(tool_call)
                # TODO: Send completed message with the result of the call
                # TODO: Send error message with any raised exceptions
                tg.cancel_scope.cancel()
        finally:
            self._abort_events.pop(call_id, None)

    def abort_tool_call(self, call_id: str) -> None:
        abort_event = self._abort_events.get(call_id)
        if abort_event is not None:
            abort_event.set()
        # Any server notification will be sent from the tool calling task

    def _abort_all_calls(self) -> None:
        for abort_event in self._abort_events.values():
            abort_event.set()
        # Any server notifications will be sent from the tool calling tasks

    async def discard_session(self) -> None:
        await self._queue.put(None)

    async def receive_tool_calls(self, send_message: SendMessageCallback) -> None:
        session_queue = self._queue
        try:
            while True:
                tool_call = await session_queue.get()
                if tool_call is None:
                    break
                await self._call_tool(tool_call, send_message)
        finally:
            self._abort_all_calls()


# TODO: Define a common "PluginHookHandler" base class
@dataclass()
class ToolsProvider(Generic[TPluginConfigSchema, TGlobalConfigSchema]):
    """Handle accepting tools provider session requests."""

    plugin_name: str
    hook_impl: ToolsProviderHook
    plugin_config_schema: type[TPluginConfigSchema]
    global_config_schema: type[TGlobalConfigSchema]

    def __post_init__(self) -> None:
        self._logger = logger = new_logger(__name__)
        logger.update_context(plugin_name=self.plugin_name)
        self._call_handlers: dict[str, ToolCallHandler] = {}

    async def process_requests(
        self, ws_session: _AsyncSessionPlugins, notify_ready: Callable[[], Any]
    ) -> None:
        """Create plugin channel and wait for server requests."""
        logger = self._logger
        endpoint = ToolsProviderEndpoint()
        # Async API expects timeouts to be handled via task groups,
        # so there's no default timeout to override when creating the channel
        async with ws_session._create_channel(endpoint) as channel:
            notify_ready()
            logger.info("Opened channel to receive tools session requests...")
            send_message = channel.send_message
            async with create_task_group() as tg:
                logger.debug("Waiting for tools session requests...")
                async for contents in channel.rx_stream():
                    logger.debug(f"Handling tools provider channel message: {contents}")
                    for event in endpoint.iter_message_events(contents):
                        logger.debug("Handling tools provider channel event")
                        endpoint.handle_rx_event(event)
                        match event:
                            case ProvideToolsDiscardSessionEvent():
                                await self._discard_session(event.arg)
                            case ProvideToolsInitSessionEvent():
                                logger.debug("Running tools listing hook")
                                ctl = ToolsProviderController(
                                    ws_session,
                                    event.arg,
                                    self.plugin_config_schema,
                                    self.global_config_schema,
                                )
                                tg.start_soon(self._invoke_hook, ctl, send_message)
                            case ProvideToolsCallToolEvent(_):
                                tg.start_soon(self._call_tool, event.arg)
                            case ProvideToolsAbortCallEvent(_):
                                self._abort_tool_call(event.arg)
                            case ChannelFinishedEvent(_):
                                pass
                            case _:
                                assert_never(event)
                    if endpoint.is_finished:
                        break

    async def _discard_session(self, session_id: str) -> None:
        """Abort the specified tools session (if it is still running)."""
        call_handler = self._call_handlers.get(session_id, None)
        if call_handler is not None:
            await call_handler.discard_session()

    async def _call_tool(self, tool_call_request: ProvideToolsCallTool) -> None:
        """Call the specified tool."""
        call_handler = self._call_handlers.get(tool_call_request.session_id, None)
        if call_handler is not None:
            await call_handler.start_tool_call(tool_call_request)

    def _abort_tool_call(self, abort_request: ProvideToolsAbortCall) -> None:
        """Abort the specified tool call (if it is still running)."""
        call_handler = self._call_handlers.get(abort_request.session_id, None)
        if call_handler is not None:
            call_handler.abort_tool_call(abort_request.call_id)

    async def _run_tools_session(
        self, session_id: str, send_message: SendMessageCallback
    ) -> None:
        logger = self._logger
        call_handlers = self._call_handlers
        if session_id in call_handlers:
            err_msg = f"Tools session already in progress for {session_id}"
            raise ServerRequestError(err_msg)
        call_handler = call_handlers[session_id] = ToolCallHandler(
            session_id, self._logger.event_context
        )
        try:
            logger.info(f"Running tools session {session_id}")
            await call_handler.receive_tool_calls(send_message)
        finally:
            call_handlers.pop(session_id, None)
        logger.info(f"Terminated tools session {session_id}")

    async def _invoke_hook(
        self,
        ctl: ToolsProviderController[TPluginConfigSchema, TGlobalConfigSchema],
        send_message: SendMessageCallback,
    ) -> None:
        logger = self._logger
        session_id = ctl.session_id
        error_details: SerializedLMSExtendedErrorDict | None = None
        try:
            plugin_tools_list = await self.hook_impl(ctl)
            llm_tools_array, client_tools_map = ChatResponseEndpoint.parse_tools(
                plugin_tools_list
            )
            llm_tools_list = llm_tools_array.to_dict()["tools"]
            assert llm_tools_list is not None  # Ensured by the parse_tools method
        except Exception as exc:
            err_msg = "Error calling tools listing hook"
            logger.error(err_msg, exc_info=True, exc=repr(exc))
            # TODO: Determine if it's worth sending the stack trace to the server
            error_title = f"Tools listing error in plugin {self.plugin_name!r}"
            ui_cause = f"{err_msg}\n({type(exc).__name__}: {exc})"
            error_details = SerializedLMSExtendedErrorDict(
                title=error_title,
                rootTitle=error_title,
                cause=ui_cause,
                stack="\n".join(format_tb(exc.__traceback__)),
            )
            error_message = ProvideToolsInitFailedDict(
                type="sessionInitializationFailed",
                sessionId=session_id,
                error=error_details,
            )
            await send_message(error_message)
            return
        init_message = ProvideToolsInitializedDict(
            type="sessionInitialized",
            sessionId=session_id,
            toolDefinitions=llm_tools_list,
        )
        await send_message(init_message)
        # Wait for further messages (until the session is discarded)
        await self._run_tools_session(session_id, send_message)


async def run_tools_provider(
    plugin_name: str,
    hook_impl: ToolsProviderHook,
    plugin_config_schema: type[BaseConfigSchema],
    global_config_schema: type[BaseConfigSchema],
    session: _AsyncSessionPlugins,
    notify_ready: Callable[[], Any],
) -> None:
    """Accept tools provider session requests."""
    tools_provider = ToolsProvider(
        plugin_name, hook_impl, plugin_config_schema, global_config_schema
    )
    await tools_provider.process_requests(session, notify_ready)
