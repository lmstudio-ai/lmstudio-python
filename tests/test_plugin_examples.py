"""Test plugin examples can run as dev plugins."""

import subprocess
import sys
import time


from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from typing import Iterable, TextIO

import pytest

from lmstudio.plugin._dev_runner import (
    _interrupt_child_process,
    _start_child_process,
    _PLUGIN_STOP_TIMEOUT,
)
from lmstudio.plugin.runner import _PLUGIN_API_STABILITY_WARNING


_THIS_DIR = Path(__file__).parent.resolve()
_PLUGIN_EXAMPLES_DIR = (_THIS_DIR / "../examples/plugins").resolve()


def _get_plugin_paths() -> list[Path]:
    return [p for p in _PLUGIN_EXAMPLES_DIR.iterdir() if p.is_dir()]


def _monitor_stream(stream: TextIO, queue: Queue[str], *, debug: bool = False) -> None:
    for line in stream:
        if debug:
            print(line)
        queue.put(line)


def _drain_queue(queue: Queue[str]) -> Iterable[str]:
    while True:
        try:
            yield queue.get(block=False)
        except Empty:
            break


def _exec_plugin(plugin_path: Path) -> subprocess.Popen[str]:
    # Run plugin in dev mode with IO pipes line buffered
    # (as the test process is monitoring for specific output)
    cmd = [
        sys.executable,
        "-u",
        "-m",
        "lmstudio.plugin",
        "--dev",
        str(plugin_path),
    ]
    return _start_child_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


_PLUGIN_START_TIMEOUT = 5


def _exec_and_interrupt(plugin_path: Path) -> tuple[list[str], list[str], list[str]]:
    # Start the plugin in a child process
    process = _exec_plugin(plugin_path)
    # Ensure pipes don't fill up and block subprocess execution
    stdout_q: Queue[str] = Queue()
    stdout_thread = Thread(target=_monitor_stream, args=[process.stdout, stdout_q])
    stdout_thread.start()
    stderr_q: Queue[str] = Queue()
    stderr_thread = Thread(target=_monitor_stream, args=[process.stderr, stderr_q])
    stderr_thread.start()
    startup_lines: list[str] = []
    # Wait for plugin to start
    start_deadline = time.monotonic() + _PLUGIN_START_TIMEOUT
    try:
        print(f"Monitoring {stdout_q!r} for plugin started message")
        while True:
            remaining_time = start_deadline - time.monotonic()
            print(f"Waiting {remaining_time} seconds for plugin to start")
            try:
                line = stdout_q.get(timeout=remaining_time)
            except Empty:
                assert False, "Plugin subprocess failed to start"
            print(line)
            startup_lines.append(line)
            if "Ctrl-C to terminate" in line:
                break
    finally:
        # Instruct the process to terminate
        print("Sending termination request to plugin subprocess")
        stop_deadline = time.monotonic() + _PLUGIN_STOP_TIMEOUT
        _interrupt_child_process(process, (stop_deadline - time.monotonic()))
        # Give threads a chance to halt their file reads
        # (process terminating will close the pipes)
        stdout_thread.join(timeout=(stop_deadline - time.monotonic()))
        stderr_thread.join(timeout=(stop_deadline - time.monotonic()))
        with process:
            # Closes open pipes
            pass
    # Collect remainder of subprocess output
    shutdown_lines = [*_drain_queue(stdout_q)]
    stderr_lines = [*_drain_queue(stderr_q)]
    return startup_lines, shutdown_lines, stderr_lines


def _plugin_case_id(plugin_path: Path) -> str:
    return plugin_path.name


@pytest.mark.lmstudio
@pytest.mark.parametrize("plugin_path", _get_plugin_paths(), ids=_plugin_case_id)
def test_plugin_execution(plugin_path: Path) -> None:
    startup_lines, shutdown_lines, stderr_lines = _exec_and_interrupt(plugin_path)
    # Stderr should start with the API stability warning...
    warning_lines = [
        *_PLUGIN_API_STABILITY_WARNING.splitlines(keepends=True),
        "\n",
        "warnings.warn(_PLUGIN_API_STABILITY_WARNING, FutureWarning)\n",
    ]
    for warning_line in warning_lines:
        stderr_line = stderr_lines.pop(0)
        assert stderr_line.endswith(warning_line)
    # ... and then consist solely of logged information messages
    for log_line in stderr_lines:
        assert log_line.startswith("INFO:")
    # Startup should finish with the notification of how to terminate the dev plugin
    assert startup_lines[-1].endswith("Ctrl-C to terminate...\n")
    # Shutdown should finish with a graceful shutdown notice from the plugin runner
    assert shutdown_lines[-1] == "Plugin execution terminated by console interrupt\n"
