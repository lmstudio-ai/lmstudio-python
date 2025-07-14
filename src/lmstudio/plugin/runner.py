"""Plugin API client implementation."""

# Plugins are expected to maintain multiple concurrently open channels and handle
# multiple concurrent server requests, so plugin implementations are always async

import asyncio
import json
import os
import runpy
import sys
import warnings

from functools import partial
from pathlib import Path

from anyio import create_task_group

from ..schemas import DictObject
from ..async_api import AsyncClient
from .._sdk_models import (
    # TODO: Define aliases at schema generation time
    PluginsRpcSetConfigSchematicsParameter,
)
from .sdk_api import LMStudioPluginInitError
from .config_schemas import BaseConfigSchema
from .hooks import (
    AsyncSessionPlugins,
    PromptPreprocessorHook,
    TokenGeneratorHook,
    ToolsProviderHook,
    run_prompt_preprocessor,
)

__all__ = [
    "run_plugin",
    "run_plugin_async",
]

# Warn about the plugin API stability, since it is still experimental
_PLUGIN_API_STABILITY_WARNING = """\
Note the plugin API is not yet stable and may change without notice in future releases
"""


class PluginClient(AsyncClient):
    def __init__(
        self,
        plugin_dir: str | os.PathLike[str],
        client_id: str | None = None,
        client_key: str | None = None,
    ) -> None:
        warnings.warn(_PLUGIN_API_STABILITY_WARNING, FutureWarning)
        self._client_id = client_id
        self._client_key = client_key
        super().__init__()
        self._hook_ready_events = {
            "prompt_preprocessor": asyncio.Event(),
            "token_generator": asyncio.Event(),
            "tools_provider": asyncio.Event(),
        }
        # TODO: Nicer error handling, move file reading to class method and make this a data class
        self._plugin_path = plugin_path = Path(plugin_dir)
        manifest_path = plugin_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["type"] != "plugin":
            raise LMStudioPluginInitError(f"Invalid manifest type: {manifest['type']}")
        if (
            manifest["runner"] != "node"
        ):  # TODO: Change to "python" once that is supported
            raise LMStudioPluginInitError(
                f"Invalid manifest runner: {manifest['runner']}"
            )
        self._owner = manifest["owner"]
        self._name = manifest["name"]

    _ALL_SESSIONS = (
        # Possible TODO: add other sessions here if
        # necessary for controller implementations
        # *ASyncSession._ALL_SESSIONS,
        AsyncSessionPlugins,
    )

    def _create_auth_message(self) -> DictObject:
        """Create an LM Studio websocket authentication message."""
        if self._client_id is None or self._client_key is None:
            return super()._create_auth_message()
        # Use plugin credentials to unlock the full plugin client API
        return self._format_auth_message(self._client_id, self._client_key)

    @property
    def plugins(self) -> AsyncSessionPlugins:
        """Return the plugins API client session."""
        return self._get_session(AsyncSessionPlugins)

    async def run_hook_prompt_preprocessor(
        self,
        hook_impl: PromptPreprocessorHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept prompt preprocessing requests."""
        hook_ready_event = self._hook_ready_events["prompt_preprocessor"]
        if hook_impl is None:
            print("No hook defined for prompt preprocessing requests")
            hook_ready_event.set()
            return False
        await run_prompt_preprocessor(
            hook_impl, plugin_config, self.plugins, hook_ready_event.set
        )
        return True

    async def run_hook_token_generator(
        self,
        hook_impl: TokenGeneratorHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept token generation requests."""
        hook_ready_event = self._hook_ready_events["token_generator"]
        if hook_impl is None:
            print("No hook defined for token generation requests")
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined token generation hook
        return True

    async def run_hook_tools_provider(
        self,
        hook_impl: ToolsProviderHook | None,
        plugin_config: type[BaseConfigSchema] | None,
    ) -> bool:
        """Accept tools provider requests."""
        # TODO: Retrieve hook definition from plugin
        hook_ready_event = self._hook_ready_events["tools_provider"]
        if hook_impl is None:
            print("No hook defined for tools provider requests")
            hook_ready_event.set()
            return False
        # TODO: Dispatch to plugin defined tools provision hook
        return True

    # TODO: Cleanup the assorted debugging prints (either remove or migrate to logging)
    async def run_plugin(self, *, allow_local_imports: bool = False) -> int:
        # TODO: Nicer error handling
        source_path = self._plugin_path / "src"
        plugin_path = source_path / "plugin.py"
        if not plugin_path.exists():
            raise FileNotFoundError(plugin_path)
        print(f"Running {plugin_path}")
        if allow_local_imports:
            # We don't try to revert the path change, as that can have odd side-effects
            sys.path.insert(0, str(source_path))
        plugin_ns = runpy.run_path(str(plugin_path), run_name="__lms_plugin__")
        prompt_preprocessor: PromptPreprocessorHook | None = plugin_ns.get(
            "preprocess_prompt", None
        )
        config_schema: type[BaseConfigSchema] | None = plugin_ns.get(
            "ConfigSchema", None
        )
        if config_schema is not None:
            if not issubclass(config_schema, BaseConfigSchema):
                raise LMStudioPluginInitError(
                    f"Expected {BaseConfigSchema!r} subclass definition, not {config_schema!r}"
                )
            await self.plugins.remote_call(
                "setConfigSchematics",
                PluginsRpcSetConfigSchematicsParameter(
                    schematics=config_schema._to_kv_config_schematics(),
                ),
            )
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        async with create_task_group() as tg:
            tg.start_soon(
                self.run_hook_prompt_preprocessor, prompt_preprocessor, config_schema
            )
            tg.start_soon(self.run_hook_token_generator, None, config_schema)
            tg.start_soon(self.run_hook_tools_provider, None, config_schema)
            # Should this have a time limit set to guard against SDK bugs?
            await asyncio.gather(*(e.wait() for e in self._hook_ready_events.values()))
            await self.plugins.remote_call("pluginInitCompleted")
            # Indicate that prompt processing is ready
            # Terminate all running tasks when termination is requested
            try:
                await asyncio.to_thread(partial(input, "Press Enter to terminate..."))
            finally:
                tg.cancel_scope.cancel()
        return 0


ENV_CLIENT_ID = "LMS_PLUGIN_CLIENT_IDENTIFIER"
ENV_CLIENT_KEY = "LMS_PLUGIN_CLIENT_PASSKEY"


def get_plugin_credentials_from_env() -> tuple[str, str]:
    return os.environ[ENV_CLIENT_ID], os.environ[ENV_CLIENT_KEY]


async def run_plugin_async(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> int:
    """Asynchronously execute a plugin in development mode."""
    try:
        client_id, client_key = get_plugin_credentials_from_env()
    except KeyError:
        print(
            f"ERROR: {ENV_CLIENT_ID} and {ENV_CLIENT_KEY} must both be set in the environment"
        )
        return 1
    async with PluginClient(plugin_dir, client_id, client_key) as plugin_client:
        return await plugin_client.run_plugin(allow_local_imports=allow_local_imports)


def run_plugin(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> int:
    """Execute a plugin in application mode."""
    return asyncio.run(
        run_plugin_async(plugin_dir, allow_local_imports=allow_local_imports)
    )
