"""Load the models required by the test suite."""

import asyncio
from contextlib import contextmanager
from typing import Generator

import lmstudio as lms

from .support import (
    EXPECTED_EMBEDDING_ID,
    EXPECTED_LLM_ID,
    EXPECTED_VLM_ID,
    LLM_LOAD_CONFIG,
    TOOL_LLM_ID,
)
from .unload_models import unload_models

# LM Studio may default to JIT handling for models loaded with `getOrLoad`,
# so ensure we restore a regular non-JIT instance with no TTL set


@contextmanager
def print_load_result(model_identifier: str) -> Generator[None, None, None]:
    try:
        yield
    except lms.LMStudioModelNotFoundError:
        print(f"Load error: {model_identifier!r} is not yet downloaded")
    else:
        print(f"Loaded: {model_identifier!r}")


async def _load_llm(client: lms.AsyncClient, model_identifier: str) -> None:
    with print_load_result(model_identifier):
        await client.llm.load_new_instance(
            model_identifier, config=LLM_LOAD_CONFIG, ttl=None
        )


async def _load_embedding_model(client: lms.AsyncClient, model_identifier: str) -> None:
    with print_load_result(model_identifier):
        await client.embedding.load_new_instance(model_identifier, ttl=None)


async def reload_models() -> None:
    await unload_models()
    async with lms.AsyncClient() as client:
        await asyncio.gather(
            _load_llm(client, EXPECTED_LLM_ID),
            _load_llm(client, EXPECTED_VLM_ID),
            _load_llm(client, TOOL_LLM_ID),
            _load_embedding_model(client, EXPECTED_EMBEDDING_ID),
        )


if __name__ == "__main__":
    asyncio.run(reload_models())
