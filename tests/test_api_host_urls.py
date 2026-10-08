"""Offline checks for API host URL handling."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from lmstudio import AsyncClient, Client

from lmstudio.json_api import ClientBase, LMStudioClientError, LMStudioWebsocket


@pytest.mark.parametrize(
    "host, expected",
    [
        ("localhost:1234", "http://localhost:1234/lmstudio-greeting"),
        ("http://localhost:1234", "http://localhost:1234/lmstudio-greeting"),
        ("ws://localhost:1234", "http://localhost:1234/lmstudio-greeting"),
        ("https://example.com", "https://example.com/lmstudio-greeting"),
        ("wss://example.com", "https://example.com/lmstudio-greeting"),
        ("http://localhost:1234/", "http://localhost:1234/lmstudio-greeting"),
        ("https://example.com/api/", "https://example.com/api/lmstudio-greeting"),
        ("[::1]:1234", "http://[::1]:1234/lmstudio-greeting"),
    ],
)
def test_probe_url(host: str, expected: str) -> None:
    assert ClientBase._get_probe_url(host) == expected


@pytest.mark.parametrize(
    "host, expected",
    [
        ("localhost:1234", "ws://localhost:1234/llm"),
        ("http://localhost:1234", "ws://localhost:1234/llm"),
        ("ws://localhost:1234", "ws://localhost:1234/llm"),
        ("https://example.com", "wss://example.com/llm"),
        ("wss://example.com", "wss://example.com/llm"),
        ("https://example.com/api/", "wss://example.com/api/llm"),
        ("[::1]:1234", "ws://[::1]:1234/llm"),
    ],
)
def test_websocket_url(host: str, expected: str) -> None:
    assert ClientBase._get_session_url(host, "llm") == expected


@pytest.mark.parametrize("path", ["/api%2Fv1", "/api%3Fv1", "/api%23v1", "/api%25v1"])
def test_encoded_api_path_and_query_are_preserved(path: str) -> None:
    host = f"https://example.com{path}/?token=test"
    assert ClientBase._get_probe_url(host) == (
        f"https://example.com{path}/lmstudio-greeting?token=test"
    )
    assert ClientBase._get_session_url(host, "llm") == (
        f"wss://example.com{path}/llm?token=test"
    )


@pytest.mark.parametrize("host", ["ftp://example.com", "file:///tmp/server"])
def test_unsupported_scheme(host: str) -> None:
    with pytest.raises(LMStudioClientError, match="Unsupported API host URL scheme"):
        ClientBase._get_probe_url(host)


def test_secure_probe_failure_mentions_tls() -> None:
    error = ClientBase._get_probe_failure_error("https://example.com")
    assert "TLS" in str(error)


def test_secure_websocket_failure_mentions_tls() -> None:
    websocket = LMStudioWebsocket[object]("wss://example.com/llm", {})
    assert "TLS" in str(websocket._get_connection_failure_error())


@pytest.mark.parametrize("host", [None, "localhost:1234", "[::1]:1234"])
def test_plain_probe_failure_preserves_diagnostic(host: str | None) -> None:
    error = ClientBase._get_probe_failure_error(host)
    expected_host = host if host is not None else "any default port"
    assert str(error) == (
        f"LM Studio is not reachable at {expected_host}. Is LM Studio running?"
    )


@pytest.mark.parametrize("host", ["http://example.com", "https://example.com"])
def test_sync_client_connects_to_expected_urls(host: str) -> None:
    scheme = "https" if host.startswith("https:") else "http"
    ws_scheme = "wss" if scheme == "https" else "ws"
    response = httpx.Response(200, json={"lmstudio": True})
    with (
        patch.object(Client, "_query_probe_url", return_value=response) as probe,
        patch("lmstudio.sync_api.SyncLMStudioWebsocket") as websocket,
    ):
        with Client(host) as client:
            client.llm.connect()
        probe.assert_called_once_with(f"{scheme}://example.com/lmstudio-greeting")
        assert websocket.call_args.args[1] == f"{ws_scheme}://example.com/llm"


@pytest.mark.asyncio
@pytest.mark.parametrize("host", ["ws://example.com", "wss://example.com"])
async def test_async_client_connects_to_expected_urls(host: str) -> None:
    scheme = "https" if host.startswith("wss:") else "http"
    ws_scheme = "wss" if scheme == "https" else "ws"
    response = httpx.Response(200, json={"lmstudio": True})
    websocket_context = MagicMock()
    websocket_context.__aenter__ = AsyncMock()
    websocket_context.__aexit__ = AsyncMock()
    with (
        patch.object(AsyncClient, "_query_probe_url", return_value=response) as probe,
        patch(
            "lmstudio.async_api._AsyncLMStudioWebsocket",
            return_value=websocket_context,
        ) as websocket,
    ):
        async with AsyncClient(host):
            pass
        probe.assert_awaited_once_with(f"{scheme}://example.com/lmstudio-greeting")
        assert {call.args[1] for call in websocket.call_args_list} == {
            f"{ws_scheme}://example.com/{session.API_NAMESPACE}"
            for session in AsyncClient._ALL_SESSIONS
        }
