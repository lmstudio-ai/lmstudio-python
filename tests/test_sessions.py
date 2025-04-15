"""Test common client session behaviour."""

import logging
from typing import Generator

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import (
    AsyncClient,
    Client,
    LMStudioWebsocketError,
)
from lmstudio.async_api import (
    AsyncLMStudioWebsocket,
    AsyncSession,
    AsyncSessionSystem,
)
from lmstudio.sync_api import (
    SyncLMStudioWebsocket,
    SyncSession,
    SyncSessionSystem,
)
from lmstudio._ws_impl import AsyncWebsocketThread

from .support import LOCAL_API_HOST


async def check_connected_async_session(session: AsyncSession) -> None:
    assert session.connected
    session_ws = session._lmsws
    assert session_ws is not None
    assert session_ws.connected
    # Attempting explicit reconnection fails when connected
    with pytest.raises(LMStudioWebsocketError, match="already connected"):
        await session.connect()
    # Reentering a session has no effect if the websocket is open
    async with session:
        assert session.connected
        assert session_ws.connected
        assert session._lmsws is session_ws
    # But the session is closed after the *first* CM exit
    assert not session.connected
    assert not session_ws.connected


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_session_cm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = AsyncSessionSystem(AsyncClient())
    # Sessions start out disconnected
    assert not session.connected
    # Disconnecting should run without error
    await session.disconnect()
    # Entering a session opens the websocket if it isn't already open
    async with session as entry_result:
        # Sessions are their own entry result
        assert entry_result is session
        # Check connected session behaves as expected
        await check_connected_async_session(session)


# Check the synchronous session API


def check_connected_sync_session(session: SyncSession) -> None:
    assert session.connected
    session_ws = session._lmsws
    assert session_ws is not None
    assert session_ws.connected
    # Attempting explicit reconnection fails when connected
    with pytest.raises(LMStudioWebsocketError, match="already connected"):
        session.connect()
    # Reentering a session has no effect if the websocket is open
    with session:
        assert session.connected
        assert session_ws.connected
        assert session._lmsws is session_ws
    # But the session is closed after the *first* CM exit
    assert not session.connected
    assert not session_ws.connected


@pytest.mark.lmstudio
def test_session_cm_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = SyncSessionSystem(Client())
    # Sessions start out disconnected
    assert not session.connected
    # Disconnecting should run without error
    session.disconnect()
    # Entering a session opens the websocket if it isn't already open
    with session as entry_result:
        # Sessions are their own entry result
        assert entry_result is session
        # Check connected session behaves as expected
        check_connected_sync_session(session)


# Sessions support implicit creation of the underlying websocket


@pytest.mark.lmstudio
def test_implicit_connection_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = SyncSessionSystem(Client())
    # Sessions start out disconnected
    assert not session.connected
    try:
        # Sync sessions will connect implicitly
        models = session.remote_call("listDownloadedModels")
        assert models is not None
        # Check connected session behaves as expected
        check_connected_sync_session(session)
    finally:
        # Still close the session even if an assertion fails
        session.close()


@pytest.mark.lmstudio
def test_implicit_reconnection_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = SyncSessionSystem(Client())
    with session:
        assert session.connected
    # Session is disconnected after use
    assert not session.connected
    try:
        # Sync sessions will reconnect implicitly
        models = session.remote_call("listDownloadedModels")
        assert models is not None
        # Check connected session behaves as expected
        check_connected_sync_session(session)
    finally:
        # Still close the session even if an assertion fails
        session.close()


# Also test the underlying websocket helper classes directly

# From RFC 6455 via
# http://python-hyper.org/projects/wsproto/en/stable/api.html#wsproto.connection.ConnectionState
WS_STATE_OPEN = 1
WS_STATE_LOCAL_CLOSING = 3
WS_STATE_CLOSED = 4
# We only expect local websocket closure, not remote
WS_CLOSING_STATES = (WS_STATE_LOCAL_CLOSING, WS_STATE_CLOSED)


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_websocket_cm_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    auth_details = AsyncClient._create_auth_message()
    lmsws = AsyncLMStudioWebsocket(f"http://{LOCAL_API_HOST}/system", auth_details)
    # SDK client websockets start out disconnected
    assert not lmsws.connected
    # Entering the CM opens the websocket if it isn't already open
    async with lmsws as entry_result:
        assert lmsws.connected
        httpx_ws = lmsws._httpx_ws
        assert httpx_ws is not None
        assert httpx_ws.connection.state.value == WS_STATE_OPEN
        # Sessions are their own entry result
        assert entry_result is lmsws
        # Attempting explicit reconnection fails when connected
        with pytest.raises(LMStudioWebsocketError, match="already connected"):
            await lmsws.connect()
        # Reentering the CM has no effect if the websocket is open
        async with lmsws:
            assert lmsws.connected
            assert httpx_ws.connection.state.value == WS_STATE_OPEN
            assert lmsws._httpx_ws is httpx_ws
        # But the websocket is closed after the *first* CM exit
        assert not lmsws.connected
        assert httpx_ws.connection.state.value in WS_CLOSING_STATES


@pytest.fixture
def ws_thread() -> Generator[AsyncWebsocketThread, None, None]:
    ws_thread = AsyncWebsocketThread()
    ws_thread.start()
    try:
        yield ws_thread
    finally:
        ws_thread.terminate()


@pytest.mark.lmstudio
def test_websocket_cm_sync(ws_thread: AsyncWebsocketThread, caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    auth_details = Client._create_auth_message()
    lmsws = SyncLMStudioWebsocket(
        ws_thread, f"http://{LOCAL_API_HOST}/system", auth_details
    )
    # SDK client websockets start out disconnected
    assert not lmsws.connected
    # Entering the CM opens the websocket if it isn't already open
    with lmsws as entry_result:
        assert lmsws.connected
        httpx_ws = lmsws._httpx_ws
        assert httpx_ws is not None
        assert httpx_ws.connection.state.value == WS_STATE_OPEN
        # Sessions are their own entry result
        assert entry_result is lmsws
        # Attempting explicit reconnection fails when connected
        with pytest.raises(LMStudioWebsocketError, match="already connected"):
            lmsws.connect()
        # Reentering the CM has no effect if the websocket is open
        with lmsws:
            assert lmsws.connected
            assert httpx_ws.connection.state.value == WS_STATE_OPEN
            assert lmsws._httpx_ws is httpx_ws
        # But the websocket is closed after the *first* CM exit
        assert not lmsws.connected
        assert httpx_ws.connection.state.value in WS_CLOSING_STATES
