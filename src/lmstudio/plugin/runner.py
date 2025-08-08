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

from .._logging import new_logger
from ..sdk_api import LMStudioFileNotFoundError, sdk_public_api
from ..schemas import DictObject
from ..async_api import AsyncClient
from .._sdk_models import (
    PluginsRpcSetConfigSchematicsParameter as SetConfigSchematicsParam,
    PluginsRpcSetGlobalConfigSchematicsParameter as SetGlobalConfigSchematicsParam,
)
from .sdk_api import LMStudioPluginInitError, LMStudioPluginRuntimeError
from .config_schemas import BaseConfigSchema
from .hooks import (
    _AsyncSessionPlugins,
    TPluginConfigSchema,
    TGlobalConfigSchema,
    run_prompt_preprocessor,
    run_token_generator,
    run_tools_provider,
)

# Available as lmstudio.plugin.*
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
        str,  # Plugin name
        THookImpl,
        type[TPluginConfigSchema],
        type[TGlobalConfigSchema],
        _AsyncSessionPlugins,
        ReadyCallback,
    ],
    Awaitable[Any],
]

_HOOK_RUNNERS: dict[str, HookRunner[Any, Any, Any]] = {
    "preprocess_prompt": run_prompt_preprocessor,
    "generate_tokens": run_token_generator,
    "list_provided_tools": run_tools_provider,
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
        # TODO: Consider moving file reading to class method and make this a data class
        self._plugin_path = plugin_path = Path(plugin_dir)
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise LMStudioFileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["type"] != "plugin":
            raise LMStudioPluginInitError(f"Invalid manifest type: {manifest['type']}")
        if manifest["runner"] != "python":
            # This works (even though the app doesn't natively support Python plugins yet),
            # as LM Studio doesn't check the runner type when requesting dev credentials.
            raise LMStudioPluginInitError(
                f'Invalid manifest runner: {manifest["runner"]} (expected "python")'
            )
        self.owner = manifest["owner"]
        self.name = name = manifest["name"]
        self._logger = logger = new_logger(__name__)
        logger.update_context(plugin=name)

    _ALL_SESSIONS = (
        # Plugin controller access all runs through a dedicated endpoint
        _AsyncSessionPlugins,
    )

    def _create_auth_message(self) -> DictObject:
        """Create an LM Studio websocket authentication message."""
        if self._client_id is None or self._client_key is None:
            return super()._create_auth_message()
        # Use plugin credentials to unlock the full plugin client API
        return self._format_auth_message(self._client_id, self._client_key)

    @property
    def plugins(self) -> _AsyncSessionPlugins:
        """Return the plugins API client session."""
        return self._get_session(_AsyncSessionPlugins)

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
            self.name,
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
        logger = self._logger
        config_name, endpoint, param_type = self._CONFIG_SCHEMA_SCOPES[scope]
        maybe_config_schema = ns.get(config_name, None)
        if maybe_config_schema is None:
            # Use an empty config in the client, don't register any schema with the server
            logger.debug(f"Plugin does not define {config_name!r}")
            return BaseConfigSchema
        if not issubclass(maybe_config_schema, BaseConfigSchema):
            raise LMStudioPluginInitError(
                f"{config_name}: Expected {BaseConfigSchema!r} subclass definition, not {maybe_config_schema!r}"
            )
        config_schema: type[BaseConfigSchema] = maybe_config_schema
        kv_config_schematics = config_schema._to_kv_config_schematics()
        if kv_config_schematics is None:
            # No fields to configure, no need to register schema with the server
            logger.info(f"Plugin defines an empty {config_name!r}")
        else:
            # Only notify the server if there is at least one config field defined
            logger.info(f"Plugin defines {config_name!r}, sending to server...")
            await self.plugins.remote_call(
                endpoint,
                param_type(
                    schematics=kv_config_schematics,
                ),
            )
        return config_schema

    async def run_plugin(self, *, allow_local_imports: bool = False) -> int:
        # TODO: Nicer error handling
        plugin_path = self._plugin_path
        source_dir_path = plugin_path / "src"
        source_path = source_dir_path / "plugin.py"
        if not source_path.exists():
            raise LMStudioFileNotFoundError(source_path)
        # TODO: Consider passing this logger to hook runners (instead of each creating their own)
        logger = self._logger
        logger.update_context(plugin_name=self.name)
        logger.info(f"Running {source_path}")
        if allow_local_imports:
            # We don't try to revert the path change, as that can have odd side-effects
            sys.path.insert(0, str(source_dir_path))
        plugin_ns = runpy.run_path(str(source_path), run_name="__lms_plugin__")
        # Look up config schemas in the namespace
        plugin_schema = await self._load_config_schema(plugin_ns, "plugin")
        global_schema = await self._load_config_schema(plugin_ns, "global")
        # Look up hook implementations in the namespace
        implemented_hooks: list[Callable[[], Awaitable[Any]]] = []
        hook_ready_events: list[asyncio.Event] = []
        for hook_name, hook_runner in _HOOK_RUNNERS.items():
            hook_impl = plugin_ns.get(hook_name, None)
            if hook_impl is None:
                logger.debug(f"Plugin does not define the {hook_name!r} hook")
                continue
            logger.info(f"Plugin defines the {hook_name!r} hook")
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
        plugin = self.name
        if not implemented_hooks:
            hook_list = "\n  - ".join(("", *sorted(_HOOK_RUNNERS)))
            print(
                f"No plugin hooks defined in {plugin!r}, "
                f"expected at least one of:{hook_list}"
            )
            return 1
        # Use anyio and exceptiongroup to handle the lack of native task
        # and exception groups prior to Python 3.11
        async with create_task_group() as tg:
            for implemented_hook in implemented_hooks:
                tg.start_soon(implemented_hook)
            # Should this have a time limit set to guard against SDK bugs?
            await asyncio.gather(*(e.wait() for e in hook_ready_events))
            await self.plugins.remote_call("pluginInitCompleted")
            # Indicate that prompt processing is ready
            print(
                f"Plugin {plugin!r} running, press Ctrl-C to terminate...", flush=True
            )
            # Task group will wait for the plugins to run
        return 0


ENV_CLIENT_ID = "LMS_PLUGIN_CLIENT_IDENTIFIER"
ENV_CLIENT_KEY = "LMS_PLUGIN_CLIENT_PASSKEY"


def get_plugin_credentials_from_env() -> tuple[str, str]:
    return os.environ[ENV_CLIENT_ID], os.environ[ENV_CLIENT_KEY]


@sdk_public_api()
async def run_plugin_async(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> None:
    """Asynchronously execute a plugin in development mode."""
    try:
        client_id, client_key = get_plugin_credentials_from_env()
    except KeyError:
        err_msg = f"ERROR: {ENV_CLIENT_ID} and {ENV_CLIENT_KEY} must both be set in the environment"
        raise LMStudioPluginRuntimeError(err_msg)
    async with PluginClient(plugin_dir, client_id, client_key) as plugin_client:
        await plugin_client.run_plugin(allow_local_imports=allow_local_imports)


@sdk_public_api()
def run_plugin(
    plugin_dir: str | os.PathLike[str], *, allow_local_imports: bool = False
) -> None:
    """Execute a plugin in application mode."""
    asyncio.run(run_plugin_async(plugin_dir, allow_local_imports=allow_local_imports))
