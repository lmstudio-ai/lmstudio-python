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
from typing import Any, Awaitable, Callable, TypeAlias, TypeVar

from anyio import create_task_group

from ..schemas import DictObject
from ..async_api import AsyncClient
from .._sdk_models import (
    PluginsRpcSetConfigSchematicsParameter as SetConfigSchematicsParam,
    PluginsRpcSetGlobalConfigSchematicsParameter as SetGlobalConfigSchematicsParam,
)
from .sdk_api import LMStudioPluginInitError
from .config_schemas import BaseConfigSchema
from .hooks import (
    AsyncSessionPlugins,
    TPluginConfigSchema,
    TGlobalConfigSchema,
    run_prompt_preprocessor,
    # run_token_generator,
    # run_tools_provider,
)

__all__ = [
    "run_plugin",
    "run_plugin_async",
]

# Warn about the plugin API stability, since it is still experimental
_PLUGIN_API_STABILITY_WARNING = """\
Note the plugin API is not yet stable and may change without notice in future releases
"""

AnyHookImpl: TypeAlias = Callable[..., Awaitable[Any]]
THookImpl = TypeVar("THookImpl", bound=AnyHookImpl)
ReadyCallback: TypeAlias = Callable[[], Any]
HookRunner: TypeAlias = Callable[
    [
        THookImpl,
        type[TPluginConfigSchema],
        type[TGlobalConfigSchema],
        AsyncSessionPlugins,
        ReadyCallback,
    ],
    Awaitable[Any],
]

_HOOK_RUNNERS: dict[str, HookRunner[Any, Any, Any]] = {
    "preprocess_prompt": run_prompt_preprocessor,
    # "generate_tokens": run_token_generator,
    # "list_provided_tools": run_tools_provider,
}


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
        # TODO: Nicer error handling, move file reading to class method and make this a data class
        self._plugin_path = plugin_path = Path(plugin_dir)
        manifest_path = plugin_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["type"] != "plugin":
            raise LMStudioPluginInitError(f"Invalid manifest type: {manifest['type']}")
        if manifest["runner"] != "python":
            # This works (even though the app doesn't natively support Python plugins yet),
            # as LM Studio doesn't check the runner type when requesting dev credentials.
            raise LMStudioPluginInitError(
                f'Invalid manifest runner: {manifest["runner"]} (expected "python")'
            )
        self._owner = manifest["owner"]
        self._name = manifest["name"]

    _ALL_SESSIONS = (
        # Plugin controller access all runs through a dedicated endpoint
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

    async def _run_hook_impl(
        self,
        hook_runner: HookRunner[THookImpl, TPluginConfigSchema, TGlobalConfigSchema],
        hook_impl: THookImpl,
        plugin_config_schema: type[TPluginConfigSchema],
        global_config_schema: type[TGlobalConfigSchema],
        notify_ready: ReadyCallback,
    ) -> None:
        """Run the given hook implementation."""
        await hook_runner(
            hook_impl,
            plugin_config_schema,
            global_config_schema,
            self.plugins,
            notify_ready,
        )

    _CONFIG_SCHEMA_SCOPES = {
        "plugin": ("ConfigSchema", "setConfigSchematics", SetConfigSchematicsParam),
        "global": (
            "GlobalConfigSchema",
            "setGlobalConfigSchematics",
            SetGlobalConfigSchematicsParam,
        ),
    }

    async def _load_config_schema(
        self, ns: DictObject, scope: str
    ) -> type[BaseConfigSchema]:
        config_name, endpoint, param_type = self._CONFIG_SCHEMA_SCOPES[scope]
        maybe_config_schema = ns.get(config_name, None)
        if maybe_config_schema is None:
            # Use an empty config in the client, don't register a schema with the server
            return BaseConfigSchema
        if not issubclass(maybe_config_schema, BaseConfigSchema):
            raise LMStudioPluginInitError(
                f"{config_name}: Expected {BaseConfigSchema!r} subclass definition, not {maybe_config_schema!r}"
            )
        config_schema: type[BaseConfigSchema] = maybe_config_schema
        kv_config_schematics = config_schema._to_kv_config_schematics()
        if kv_config_schematics is not None:
            # Only notify the server if there is at least one config field defined
            await self.plugins.remote_call(
                endpoint,
                param_type(
                    schematics=kv_config_schematics,
                ),
            )
        return config_schema

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
        # Look up config schemas in the namespace
        plugin_schema = await self._load_config_schema(plugin_ns, "plugin")
        global_schema = await self._load_config_schema(plugin_ns, "global")
        # Look up hook implementations in the namespace
        implemented_hooks: list[Callable[[], Awaitable[Any]]] = []
        hook_ready_events: list[asyncio.Event] = []
        for hook_name, hook_runner in _HOOK_RUNNERS.items():
            hook_impl = plugin_ns.get(hook_name, None)
            if hook_impl is None:
                print(f"Plugin does not define the {hook_name!r} hook")
                continue
            hook_ready_event = asyncio.Event()
            hook_ready_events.append(hook_ready_event)
            implemented_hooks.append(
                partial(
                    self._run_hook_impl,
                    hook_runner,
                    hook_impl,
                    plugin_schema,
                    global_schema,
                    hook_ready_event.set,
                )
            )
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        async with create_task_group() as tg:
            for implemented_hook in implemented_hooks:
                tg.start_soon(implemented_hook)
            # Should this have a time limit set to guard against SDK bugs?
            await asyncio.gather(*(e.wait() for e in hook_ready_events))
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
