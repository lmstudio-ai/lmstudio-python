"""Command line interface implementation."""

import argparse
import logging
import os.path
import sys
import warnings

from typing import Sequence

from ..sdk_api import sdk_public_api

from . import _dev_runner, runner


def _parse_args(
    argv: Sequence[str] | None = None,
) -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    py_name = os.path.basename(sys.executable).removesuffix(".exe")
    parser = argparse.ArgumentParser(
        prog=f"{py_name} -m {__spec__.parent}",
        description="LM Studio plugin runner for Python plugins",
    )
    parser.add_argument(
        "plugin_path", metavar="PLUGIN_PATH", help="Directory name of plugin to run"
    )
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser, parser.parse_args(argv)


@sdk_public_api()
def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``lmstudio.plugin`` CLI.

    If *args* is not given, defaults to using ``sys.argv``.
    """
    parser, args = _parse_args(argv)
    plugin_path = args.plugin_path
    if not os.path.exists(plugin_path):
        parser.print_usage()
        print(f"ERROR: Failed to find plugin folder at {plugin_path!r}")
        return 1
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    if sys.platform == "win32":
        # Accept Ctrl-C events even in non-default process groups
        # (allows for graceful termination when Ctrl-C is received
        # from a controlling process rather than from a console)
        # Based on https://github.com/python/cpython/blob/3.14/Lib/test/win_console_handler.py
        # and https://stackoverflow.com/questions/35772001/how-can-i-handle-a-signal-sigint-on-a-windows-os-machine/35792192#35792192
        from ctypes import c_void_p, windll, wintypes

        SetConsoleCtrlHandler = windll.kernel32.SetConsoleCtrlHandler
        SetConsoleCtrlHandler.argtypes = (c_void_p, wintypes.BOOL)
        SetConsoleCtrlHandler.restype = wintypes.BOOL
        if not SetConsoleCtrlHandler(None, 0):
            print("Failed to enable Ctrl-C events, termination may be abrupt")
    if not args.dev:
        warnings.filterwarnings(
            "ignore", ".*the plugin API is not yet stable", FutureWarning
        )
        try:
            runner.run_plugin(plugin_path, allow_local_imports=True)
        except KeyboardInterrupt:
            print("Plugin execution terminated by console interrupt", flush=True)
    else:
        # Retrieve args from API host, spawn plugin in subprocess
        try:
            _dev_runner.run_plugin(plugin_path, debug=args.debug)
        except KeyboardInterrupt:
            pass  # Subprocess handles reporting the plugin termination
    return 0
