"""Emulated "SDK" for the traceback filtering unit tests."""

from pathlib import Path
from typing import AsyncGenerator, Callable, Coroutine, Generator, NoReturn, TypeAlias

from lmstudio import LMStudioError
from lmstudio.sdk_api import sdk_public_api, sdk_public_api_async, sdk_public_type

# The traceback filtering tests rely on this file being in
# an "lmstudio" folder (similar to the real SDK)
assert __name__.rpartition(".")[2] == "lmstudio"
assert "lmstudio" in Path(__file__).parts


def raise_sdk_error() -> NoReturn:
    raise LMStudioError("Emulate anticipated runtime error")


def raise_external_error() -> NoReturn:
    raise BaseException("Emulate Ctrl-C")


def raise_internal_error() -> NoReturn:
    raise Exception("Emulate unexpected runtime error")


ErrFunc: TypeAlias = Callable[[], NoReturn]


def internal_func(err_func: ErrFunc) -> NoReturn:
    err_func()


@sdk_public_api()
def public_func(err_func: ErrFunc) -> NoReturn:
    internal_func(err_func)


@sdk_public_api()
def public_wrapper_func(err_func: ErrFunc) -> NoReturn:
    public_func(err_func)


class InternalIterator:
    # Define an iterable class to align with the way
    # AsyncPrediction and Prediction are implemented
    def __init__(self, err_func: ErrFunc) -> None:
        self._err_func = err_func


class AsyncInternalIterator(InternalIterator):
    async def __aiter__(self) -> AsyncGenerator[None, NoReturn]:
        yield None
        internal_func(self._err_func)


class SyncInternalIterator(InternalIterator):
    def __iter__(self) -> Generator[None, None, NoReturn]:
        yield None
        internal_func(self._err_func)


@sdk_public_api()
def public_iter_wrapper(err_func: ErrFunc) -> None:
    for _ in SyncInternalIterator(err_func):
        pass


@sdk_public_api_async()
async def public_coroutine(err_func: ErrFunc) -> NoReturn:
    internal_func(err_func)


@sdk_public_api_async()
async def public_wrapper_coroutine(err_func: ErrFunc) -> NoReturn:
    await public_coroutine(err_func)


@sdk_public_api_async()
async def public_asynciter_wrapper(err_func: ErrFunc) -> None:
    async for _ in AsyncInternalIterator(err_func):
        pass


@sdk_public_type
class PublicClass:
    def internal_method(self, err_func: ErrFunc) -> NoReturn:
        internal_func(err_func)

    @sdk_public_api()
    def public_method(self, err_func: ErrFunc) -> NoReturn:
        self.internal_method(err_func)

    @sdk_public_api()
    def public_wrapper_method(self, err_func: ErrFunc) -> NoReturn:
        self.public_method(err_func)

    @sdk_public_api()
    def public_iter_wrapper_method(self, err_func: ErrFunc) -> None:
        for _ in SyncInternalIterator(err_func):
            pass

    @sdk_public_api_async()
    async def public_async_method(self, err_func: ErrFunc) -> NoReturn:
        internal_func(err_func)

    @sdk_public_api_async()
    async def public_async_wrapper_method(self, err_func: ErrFunc) -> NoReturn:
        await public_coroutine(err_func)

    @sdk_public_api_async()
    async def public_asynciter_wrapper_method(self, err_func: ErrFunc) -> None:
        async for _ in AsyncInternalIterator(err_func):
            pass


TestFunc: TypeAlias = Callable[[ErrFunc], NoReturn | None]
TestCoro: TypeAlias = Callable[[ErrFunc], Coroutine[None, None, NoReturn | None]]

_PC = PublicClass()

SYNC_API: tuple[TestFunc, ...] = (
    public_func,
    public_wrapper_func,
    public_iter_wrapper,
    _PC.public_method,
    _PC.public_wrapper_method,
    _PC.public_iter_wrapper_method,
)
ASYNC_API: tuple[TestCoro, ...] = (
    public_coroutine,
    public_wrapper_coroutine,
    public_asynciter_wrapper,
    _PC.public_async_method,
    _PC.public_async_wrapper_method,
    _PC.public_asynciter_wrapper_method,
)
