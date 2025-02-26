"""Ensure the traceback filtering works as expected."""

import pytest
from pytest import LogCaptureFixture as LogCap

from lmstudio import LMStudioError
from lmstudio.sdk_api import sdk_callback_invocation
from lmstudio._logging import get_logger

from .support import check_sdk_error, check_unfiltered_error
from .support.lmstudio import (
    TestCoro,
    TestFunc,
    SYNC_API,
    ASYNC_API,
    raise_external_error,
    raise_internal_error,
    raise_sdk_error,
)


@pytest.mark.parametrize("public_api", SYNC_API)
def test_sync_api_truncation_sdk_error(public_api: TestFunc) -> None:
    with pytest.raises(LMStudioError) as exc_info:
        public_api(raise_sdk_error)
    check_sdk_error(exc_info, __file__)


@pytest.mark.parametrize("public_api", SYNC_API)
def test_sync_api_truncation_external_error(public_api: TestFunc) -> None:
    with pytest.raises(BaseException) as exc_info:
        public_api(raise_external_error)
    check_sdk_error(exc_info, __file__, check_exc=False)


@pytest.mark.parametrize("public_api", SYNC_API)
def test_sync_api_truncation_internal_error(public_api: TestFunc) -> None:
    with pytest.raises(Exception) as exc_info:
        public_api(raise_internal_error)
    check_unfiltered_error(exc_info, __file__, raise_internal_error)


@pytest.mark.asyncio
@pytest.mark.parametrize("public_api", ASYNC_API)
async def test_async_api_truncation_sdk_error(public_api: TestCoro) -> None:
    with pytest.raises(LMStudioError) as exc_info:
        await public_api(raise_sdk_error)
    check_sdk_error(exc_info, __file__)


@pytest.mark.asyncio
@pytest.mark.parametrize("public_api", ASYNC_API)
async def test_async_api_truncation_external_error(public_api: TestCoro) -> None:
    with pytest.raises(BaseException) as exc_info:
        await public_api(raise_external_error)
    check_sdk_error(exc_info, __file__, check_exc=False)


@pytest.mark.asyncio
@pytest.mark.parametrize("public_api", ASYNC_API)
async def test_async_api_truncation_internal_error(public_api: TestCoro) -> None:
    with pytest.raises(Exception) as exc_info:
        await public_api(raise_internal_error)
    check_unfiltered_error(exc_info, __file__, raise_internal_error)


def test_callback_invocation(caplog: LogCap) -> None:
    logger = get_logger(__name__)
    exc_to_raise = Exception("This will be raised")
    with sdk_callback_invocation("Callback test", logger):
        raise exc_to_raise
    logged_errors = caplog.get_records("call")
    logged_error = logged_errors[0]
    logged_msg = logged_error.getMessage()
    assert "Callback test" in logged_msg
    assert "This will be raised" in logged_msg
    assert logged_error.levelname.lower() == "error"
    assert len(logged_errors) == 1
