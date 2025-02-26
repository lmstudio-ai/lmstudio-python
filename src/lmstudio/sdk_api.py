"""Common definitions for defining the SDK API boundary."""

from contextlib import AsyncContextDecorator, ContextDecorator
from os import getenv
from types import TracebackType
from typing import Self, Type, TypeVar

from ._logging import StructuredLogger

__all__ = [
    "LMStudioError",
    "LMStudioOSError",
    "LMStudioRuntimeError",
    "LMStudioValueError",
]

_SDK_MODULE = __name__.partition(".")[0]

_C = TypeVar("_C", bound=type)


def sdk_public_type(cls: _C) -> _C:
    """Indicates a class forms part of the public SDK boundary.

    Sets `__module__` to the top-level SDK import rather than
    leaving it set to the implementation module.

    Note: methods are *not* implicitly decorated as public SDK APIs
    """
    cls.__module__ = _SDK_MODULE
    return cls


@sdk_public_type
class LMStudioError(Exception):
    """Common base class for exceptions raised directly by the SDK.

    Note: exceptions raised by underlying libraries (such as websocket
          connection errors) are NOT wrapped as SDK exceptions.
    """


@sdk_public_type
class LMStudioOSError(OSError, LMStudioError):
    """The SDK received an error while accessing the local operating system."""


@sdk_public_type
class LMStudioRuntimeError(RuntimeError, LMStudioError):
    """User requested an invalid sequence of operations from the SDK."""


@sdk_public_type
class LMStudioValueError(ValueError, LMStudioError):
    """User supplied an invalid value to the SDK."""


def _truncate_traceback(exc: BaseException | None) -> None:
    """Truncate API traceback at the SDK boundary (by default)."""
    if exc is None:
        return
    # Check env var every time so it can be updated at runtime
    if getenv("LMS_KEEP_INTERNAL_STACK"):
        # Setting this environment variable turns off the traceback filtering
        return
    if isinstance(exc, LMStudioError) or not isinstance(exc, Exception):
        # Truncate the traceback for SDK exceptions at the SDK boundary.
        # Also truncate asychronous exceptions like KeyboardInterrupt.
        # Other unwrapped exceptions indicate SDK bugs and keep a full traceback.
        exc.__traceback__ = None


# We avoid contextlib.contextmanager when manipulating the way exceptions are
# reported, as it can have quirky impacts on whether changes actually take effect


class sdk_callback_invocation:
    """Catch and log raised exceptions to protect the message handling task."""

    def __init__(self, message: str, logger: StructuredLogger) -> None:
        self._message = message
        self._logger = logger

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> bool:
        if not isinstance(exc_val, Exception):
            return False
        # Callbacks are invoked from message handling tasks,
        # which need to keep going even if a callback fails
        # We don't want the SDK stack trace, but we do want
        # the callback exception details
        self._logger.error(self._message, exc_info=True, exc=repr(exc_val))
        return True


class sdk_public_api(ContextDecorator):
    """Indicates a callable forms part of the public SDK boundary.

    Also usable as a context manager (in both synchronous and
    asynchronous code) when publishing generator-based context
    managers and iterators.

    By default, tracebacks will be truncated at the SDK boundary.
    Set LMS_KEEP_INTERNAL_STACK to a non-empty string in the process
    environment to see full traceback information in SDK exceptions.
    """

    # ContextDecorator uses `functools.wraps`, so the original callable
    # can be accessed as `f.__wrapped__` when public APIs call each other
    # Unfortunately, MyPy complains if you do that:
    # https://github.com/python/typeshed/issues/13403

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        _truncate_traceback(exc_val)


class sdk_public_api_async(AsyncContextDecorator):
    """Indicates a coroutine forms part of the public SDK boundary.

    By default, tracebacks will be truncated at the SDK boundary.
    Set LMS_KEEP_INTERNAL_STACK to a non-empty string in the process
    environment to see full traceback information in SDK exceptions.
    """

    # While this *can* be used as an async context manager, there's
    # no compelling reason to ever use it that way (over just using
    # sdk_public_api as a synchronous context manager instead).

    # AsyncContextDecorator uses `functools.wraps`, so the original callable
    # can be accessed as `f.__wrapped__` when public APIs call each other
    # Unfortunately, MyPy complains if you do that:
    # https://github.com/python/typeshed/issues/13403

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        _truncate_traceback(exc_val)
