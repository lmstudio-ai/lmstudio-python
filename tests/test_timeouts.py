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
from lmstudio.sync_api import _DEFAULT_TIMEOUT

from .support import EXPECTED_LLM_ID

# Sync only, as async API uses standard async timeout constructs like anyio.move_on_after


@contextmanager
def sync_api_timeout(timeout: float | None) -> Generator[float | None, None, None]:
    previous_timeout = get_sync_api_timeout()
    set_sync_api_timeout(timeout)
    try:
        yield previous_timeout
    finally:
        set_sync_api_timeout(previous_timeout)


def test_default_timeout() -> None:
    # Ensure default timeout is defined, but is not excessively short or long
    # (the bounds that are considered reasonable may change over time)
    assert _DEFAULT_TIMEOUT is not None
    assert _DEFAULT_TIMEOUT >= 60
    assert _DEFAULT_TIMEOUT <= 600


@pytest.mark.parametrize("timeout", (None, 0, 1.5, 3600, 3600 * 24 * 7))
def test_timeout_updates_sync(timeout: float | None) -> None:
    with sync_api_timeout(timeout) as previous_timeout:
        assert previous_timeout == _DEFAULT_TIMEOUT
        assert get_sync_api_timeout() == timeout
    assert get_sync_api_timeout() == previous_timeout


@pytest.mark.lmstudio
def test_timeout_rpc_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)

    with Client() as client:
        model = client.llm.model(EXPECTED_LLM_ID)
        with sync_api_timeout(0):
            assert get_sync_api_timeout() == 0
            with pytest.raises(LMStudioTimeoutError):
                response = model.get_info()
                logging.error(f"Unexpected response: {response}")


@pytest.mark.lmstudio
def test_timeout_channel_sync(caplog: LogCap) -> None:
    caplog.set_level(logging.DEBUG)

    with Client() as client:
        model = client.llm.model(EXPECTED_LLM_ID)
        with sync_api_timeout(0):
            assert get_sync_api_timeout() == 0
            with pytest.raises(LMStudioTimeoutError):
                response = model.respond("This will time out")
                logging.error(f"Unexpected response: {response}")
