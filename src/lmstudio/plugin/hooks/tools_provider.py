"""Invoking and supporting tools provider hook implementations."""

import asyncio

from contextlib import asynccontextmanager
from dataclasses import dataclass
from traceback import format_tb
from typing import Any, AsyncIterator, Awaitable, Callable, Generic, Iterable, TypeAlias
from typing_extensions import (
    # Native in 3.11+
    assert_never,
)

from anyio import create_task_group
from anyio.abc import TaskGroup

from ..._logging import new_logger
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
    # "PluginsChannelSetToolsProviderToClientPacketAbortToolCall",
    # "PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict",
    # "PluginsChannelSetToolsProviderToClientPacketCallTool",
    # "PluginsChannelSetToolsProviderToClientPacketCallToolDict",
    # "PluginsChannelSetToolsProviderToClientPacketDiscardSession",
    # "PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict",
    PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict as ProvideToolsInitFailedDict,
    PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict as ProvideToolsInitializedDict,
    # "PluginsChannelSetToolsProviderToServerPacketToolCallComplete",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallError",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallStatus",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallWarn",
    # "PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict",
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


PromptPreprocessingRxEvent: TypeAlias = (
    ProvideToolsDiscardSessionEvent
    | ProvideToolsInitSessionEvent
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
            case {"type": "initSession"} as request_dict:
                parsed_request = ProvideToolsInitSession._from_any_api_dict(
                    request_dict
                )
                yield ProvideToolsInitSessionEvent(parsed_request)
            case unmatched:
                self.report_unknown_message(unmatched)

    def handle_rx_event(self, event: PromptPreprocessingRxEvent) -> None:
        match event:
            case ProvideToolsDiscardSessionEvent(session_id):
                self._logger.debug(f"Aborting {session_id}", session_id=session_id)
            case ProvideToolsInitSessionEvent(request):
                session_id = request.session_id
                self._logger.debug(
                    "Received tools session request", session_id=session_id
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
        self._abort_events: dict[str, asyncio.Event] = {}

    async def process_requests(
        self, session: _AsyncSessionPlugins, notify_ready: Callable[[], Any]
    ) -> None:
        """Create plugin channel and wait for server requests."""
        logger = self._logger
        endpoint = ToolsProviderEndpoint()
        # Async API expects timeouts to be handled via task groups,
        # so there's no default timeout to override when creating the channel
        async with session._create_channel(endpoint) as channel:
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
                                self._discard_session(event.arg)
                            case ProvideToolsInitSessionEvent():
                                logger.debug("Running tools listing hook")
                                ctl = ToolsProviderController(
                                    session,
                                    event.arg,
                                    self.plugin_config_schema,
                                    self.global_config_schema,
                                )
                                tg.start_soon(self._invoke_hook, ctl, send_message)
                    if endpoint.is_finished:
                        break

    def _discard_session(self, session_id: str) -> None:
        """Abort the specified tools session (if it is still running)."""
        abort_event = self._abort_events.get(session_id, None)
        if abort_event is not None:
            abort_event.set()

    async def _cancel_on_event(
        self, tg: TaskGroup, event: asyncio.Event, message: str
    ) -> None:
        await event.wait()
        self._logger.info(message)
        tg.cancel_scope.cancel()

    @asynccontextmanager
    async def _run_tools_session(self, session_id: str) -> AsyncIterator[asyncio.Event]:
        logger = self._logger
        abort_events = self._abort_events
        if session_id in abort_events:
            err_msg = f"Tools session already in progress for {session_id}"
            raise ServerRequestError(err_msg)
        abort_events[session_id] = abort_event = asyncio.Event()
        try:
            async with create_task_group() as tg:
                tg.start_soon(
                    self._cancel_on_event,
                    tg,
                    abort_event,
                    f"Aborting tools session {session_id}",
                )
                logger.info(f"Running tools session {session_id}")
                yield abort_event
                tg.cancel_scope.cancel()
        finally:
            abort_events.pop(session_id, None)
        logger.info(f"Terminated tools session {session_id}")

    async def _invoke_hook(
        self,
        ctl: ToolsProviderController[TPluginConfigSchema, TGlobalConfigSchema],
        send_response: SendMessageCallback,
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
            await send_response(error_message)
            return
        init_message = ProvideToolsInitializedDict(
            type="sessionInitialized",
            sessionId=session_id,
            toolDefinitions=llm_tools_list,
        )
        await send_response(init_message)
        async with self._run_tools_session(session_id) as abort_event:
            # TODO: Set up per-session queues to receive tool call requests
            # Receiving None on the queue may replace the abort events...
            await abort_event.wait()


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
