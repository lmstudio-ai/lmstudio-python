"""Command line interface implementation."""

import argparse
import os.path
import sys
import warnings

from typing import Sequence

from . import _api_client, _dev_client


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
    return parser, parser.parse_args(argv)


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
    warnings.filterwarnings(
        "ignore", ".*the plugin API is not yet stable", FutureWarning
    )
    warnings.filterwarnings(
        "ignore", ".*the async API is not yet stable", FutureWarning
    )
    if not args.dev:
        return _api_client.run_plugin(plugin_path)
    # Retrieve args from API host, spawn plugin in subprocess
    return _dev_client.run_plugin(plugin_path)
