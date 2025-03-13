"""Test specific aspects of error and event logging."""

import logging

import anyio
import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import AsyncClient

from .support import InvalidEndpoint


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.lmstudio
async def test_invalid_endpoint_request_stream(caplog: LogCap) -> None:
    caplog.set_level(logging.ERROR)
    async with AsyncClient() as client:
        session = client.llm
        # This will time out due to the bad API endpoint
        with pytest.raises(TimeoutError):
            with anyio.fail_after(1):
                endpoint = InvalidEndpoint()
                async with session._create_channel(endpoint) as channel:
                    async for _ in channel.rx_stream():
                        break
    logged_errors = caplog.records
    logged_error = logged_errors[0]
    logged_msg = logged_error.getMessage()
    assert "SDK communication warning" in logged_msg
    assert "noSuchEndpoint" in logged_msg
    assert logged_error.levelname.lower() == "error"
    assert len(logged_errors) == 1
