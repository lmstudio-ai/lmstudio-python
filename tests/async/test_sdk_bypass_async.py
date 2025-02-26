"""Test bypassing the SDK and accessing the API server directly."""

# This test case helps to differentiate between actual SDK failures
# and general failures due to an incorrect test environment setup.

import logging
import uuid
import warnings

from typing import Any, AsyncContextManager

import pytest

from httpx_ws import aconnect_ws, AsyncWebSocketSession


@pytest.mark.asyncio
@pytest.mark.lmstudio
async def test_connect_and_predict_async(caplog: Any) -> None:
    base_url = "localhost:1234"
    model_identifier = "hugging-quants/llama-3.2-1b-instruct"
    prompt = "Hello"

    caplog.set_level(logging.DEBUG)
    ws_cm: AsyncContextManager[AsyncWebSocketSession] = aconnect_ws(
        f"ws://{base_url}/llm"
    )

    async with ws_cm as ws:
        # Authenticate
        client_identifier = str(uuid.uuid4())
        client_passkey = str(uuid.uuid4())
        auth_message = {
            "authVersion": 1,
            "clientIdentifier": client_identifier,
            "clientPasskey": client_passkey,
        }
        await ws.send_json(auth_message)
        auth_result = await ws.receive_json()
        if not auth_result["success"]:
            raise Exception(f"Authentication failed: {auth_result['error']}")

        # Send prediction request
        channel_id = 1
        creation_parameter = {
            "modelSpecifier": {
                "type": "query",
                "query": {"identifier": model_identifier},
            },
            "history": {
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            },
            "predictionConfigStack": {"layers": []},
        }
        create_message = {
            "type": "channelCreate",
            "endpoint": "predict",
            "channelId": channel_id,
            "creationParameter": creation_parameter,
        }
        await ws.send_json(create_message)

        # Process prediction response
        fragments = []
        while True:
            message = await ws.receive_json()

            match message:
                case {"type": "channelSend", "message": contents}:
                    match contents:
                        case {"type": "fragment", "fragment": {"content": fragment}}:
                            fragments.append(fragment)
                        case {"type": "fragment", "fragment": fragment}:
                            # Older LM Studio instance where message fragments were just strings
                            fragments.append(fragment)
                        case {"type": "success"}:
                            # We're done here
                            break
                case {"type": "channelError", "error": error}:
                    raise Exception(f"Prediction error: {error}")
                case {"type": "communicationWarning", "warning": warning}:
                    warnings.warn(f"Channel warning: {warning}")

    response = "".join(fragments)

    # The initial query from the LLM will change, but we expect it to be a question
    logging.info(f"LLM response: {response!r}")
    assert "?" in response
