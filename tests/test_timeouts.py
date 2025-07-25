"""Test client timeout behaviour."""

import logging

from contextlib import contextmanager
from typing import Generator

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import (
    Client,
    LMStudioTimeoutError,
    get_sync_api_timeout,
    set_sync_api_timeout,
)

from .support import EXPECTED_LLM_ID

# Sync only, as async API uses standard async timeout constructs like anyio.move_on_after


@contextmanager
def sync_api_timeout(timeout: float | None) -> Generator[float | None, None, None]:
    default_timeout = get_sync_api_timeout()
    try:
        yield default_timeout
    finally:
        set_sync_api_timeout(default_timeout)


@pytest.mark.parametrize("timeout", (None, 0, 1.5, 3600, 3600 * 24 * 7))
def test_timeout_updates_sync(timeout: float | None) -> None:
    with sync_api_timeout(timeout) as previous_timeout:
        assert previous_timeout is not None
        assert previous_timeout > 0
        set_sync_api_timeout(timeout)
        assert get_sync_api_timeout() == timeout
    assert get_sync_api_timeout() == previous_timeout


@pytest.mark.lmstudio
def test_rpc_timeout_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)

    with Client() as client:
        model = client.llm.model(EXPECTED_LLM_ID)
        with sync_api_timeout(0):
            with pytest.raises(LMStudioTimeoutError):
                model.get_info()


@pytest.mark.lmstudio
def test_channel_timeout_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)

    with Client() as client:
        model = client.llm.model(EXPECTED_LLM_ID)
        with sync_api_timeout(0):
            with pytest.raises(LMStudioTimeoutError):
                model.respond("This will time out")
