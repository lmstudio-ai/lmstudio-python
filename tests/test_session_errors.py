"""Test common client session error reporting behaviour."""

import logging

from typing import cast

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import (
    AsyncClient,
    LMStudioWebsocketError,
    Client,
)
from lmstudio.async_api import (
    _AsyncSession,
    _AsyncSessionSystem,
)
from lmstudio.sync_api import (
    SyncLMStudioWebsocket,
    _SyncSession,
    _SyncSessionSystem,
)

from .support import (
    EXPECT_TB_TRUNCATION,
    InvalidEndpoint,
    nonresponsive_api_host,
    closed_api_host,
    check_sdk_error,
    check_unfiltered_error,
)

from .support.lmstudio import ErrFunc


async def check_call_errors_async(session: _AsyncSession) -> None:
    # Remote calls on the underlying websocket are expected to fail when not connected
    with pytest.raises(
        LMStudioWebsocketError,
        match="must be connected.*remote calls",
    ) as call_exc_info:
        await session.remote_call("invalid")
    check_sdk_error(call_exc_info, __file__)
    # Creating channels is expected to fail when not connected
    # This is an internal error, so we don't expect truncation
    channel_cm = session._create_channel(InvalidEndpoint())
    err_func = cast(ErrFunc, session._get_lmsws)
    with pytest.raises(
        LMStudioWebsocketError,
        match="must be connected.*create channels",
    ) as channel_exc_info:
        await channel_cm.__aenter__()
    check_unfiltered_error(channel_exc_info, __file__, err_func)


@pytest.mark.asyncio
async def test_session_not_started_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = _AsyncSessionSystem(AsyncClient())
    # Sessions start out disconnected
    assert not session.connected
    # Check server call errors are reported as expected
    await check_call_errors_async(session)


@pytest.mark.lmstudio
@pytest.mark.asyncio
async def test_session_disconnected_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    api_host = await AsyncClient.find_default_local_api_host()
    client = AsyncClient(api_host)
    session = _AsyncSessionSystem(client)
    async with client._task_manager, session:
        assert session.connected
    # Session is disconnected after use
    assert not session.connected
    # Check server call errors are reported as expected
    await check_call_errors_async(session)


@pytest.mark.asyncio
async def test_session_closed_port_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    client = AsyncClient(closed_api_host())
    session = _AsyncSessionSystem(client)
    # Sessions start out disconnected
    assert not session.connected
    # Should get an SDK exception rather than the underlying exception
    async with client._task_manager:
        with pytest.raises(LMStudioWebsocketError, match="is not reachable"):
            await session.connect()
    # Session should still be considered disconnected
    assert not session.connected
    # Check server call errors are reported as expected
    await check_call_errors_async(session)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_session_nonresponsive_port_async(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with nonresponsive_api_host() as api_host:
        client = AsyncClient(api_host)
        session = _AsyncSessionSystem(client)
        # Sessions start out disconnected
        assert not session.connected
        # Should get an SDK exception rather than the underlying exception
        async with client._task_manager:
            with pytest.raises(LMStudioWebsocketError, match="is not reachable"):
                await session.connect()
    # Session should still be considered disconnected
    assert not session.connected
    # Check server call errors are reported as expected
    await check_call_errors_async(session)


def check_call_errors_sync(session: _SyncSession) -> None:
    # Remote calls are expected to fail when not connected
    with pytest.raises(
        LMStudioWebsocketError,
        match="is not reachable",
    ) as call_exc_info:
        session.remote_call("invalid")
    check_sdk_error(call_exc_info, __file__)
    # Creating channels is expected to fail when not connected
    # This internal API may call a public one, so we expect partial truncation
    # *unless* we're testing on Python 3.10, where there is no truncation at all
    channel_cm = session._create_channel(InvalidEndpoint())
    if EXPECT_TB_TRUNCATION:
        err_func = cast(ErrFunc, session._ensure_connected)
    else:
        err_func = cast(ErrFunc, SyncLMStudioWebsocket.connect)
    with pytest.raises(
        LMStudioWebsocketError,
        match="is not reachable",
    ) as channel_exc_info:
        channel_cm.__enter__()
    check_unfiltered_error(channel_exc_info, __file__, err_func)


def test_session_closed_port_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    session = _SyncSessionSystem(Client(closed_api_host()))
    # Sessions start out disconnected
    assert not session.connected
    # Should get an SDK exception rather than the underlying exception
    with pytest.raises(LMStudioWebsocketError, match="is not reachable"):
        session.connect()
    # Session should still be considered disconnected
    assert not session.connected
    # Check server call errors are reported as expected
    check_call_errors_sync(session)


@pytest.mark.slow
def test_session_nonresponsive_port_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)
    with nonresponsive_api_host() as api_host:
        session = _SyncSessionSystem(Client(api_host))
        # Sessions start out disconnected
        assert not session.connected
        # Should get an SDK exception rather than the underlying exception
        with pytest.raises(LMStudioWebsocketError, match="is not reachable"):
            session.connect()
    # Session should still be considered disconnected
    assert not session.connected
    # Check server call errors are reported as expected
    check_call_errors_sync(session)
