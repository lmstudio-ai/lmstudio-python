"""Unload the models required by the test suite."""

import asyncio
import lmstudio as lms

from .support import (
    EXPECTED_EMBEDDING_ID,
    EXPECTED_LLM_ID,
    EXPECTED_VLM_ID,
    TOOL_LLM_ID,
)

AsyncSessionModel = lms.async_api.AsyncSessionEmbedding | lms.async_api.AsyncSessionLlm


async def _unload_model(session: AsyncSessionModel, model_identifier: str) -> None:
    try:
        await session.unload(model_identifier)
    except lms.LMStudioModelNotFoundError:
        print(f"Unloaded: {model_identifier!r} (model was not loaded)")
    else:
        print(f"Unloaded: {model_identifier!r}")


async def unload_models() -> None:
    async with lms.AsyncClient() as client:
        await asyncio.gather(
            _unload_model(client.llm, EXPECTED_LLM_ID),
            _unload_model(client.llm, EXPECTED_VLM_ID),
            _unload_model(client.llm, TOOL_LLM_ID),
            _unload_model(client.embedding, EXPECTED_EMBEDDING_ID),
        )


if __name__ == "__main__":
    asyncio.run(unload_models())
