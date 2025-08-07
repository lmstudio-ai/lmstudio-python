"""Support for implementing LM Studio plugins in Python."""

# Using wildcard imports to export API symbols is acceptable
# ruff: noqa: F403

from .sdk_api import *
from .config_schemas import *
from .hooks import *
from .runner import *

# Initial Python plugin SDK TODO list
#
# General tasks
# * [DONE] refactor hook channel and controller definitions out to a submodule
# * [DONE] refactor hook registration to be data driven instead of hardcoded in the runner
# * refactor to allow "Abort" request handling to be common across hook invocation tasks
# * refactor to allow hook invocation error handling to be common across hook invocation tasks
# * [DONE] gracefully handle app termination while a dev plugin is still running
# * [DONE] gracefully handle using Ctrl-C to terminate a running dev plugin
# * [DONE] add async tool handling support to SDK (as part of adding .act() to the async API)
#
# Controller APIs (may be limited to relevant hook controllers)
#
# * [DONE] status blocks (both simple "done" blocks, and blocks with in-place updates)
# * citation blocks
# * debug info blocks
# * [DONE] tool status reporting
# * full content block display
# * chat history retrieval
# * model handle retrieval
# * UI block sender name configuration
# * [not necessary (handled directly by UI)] interactive tool call request confirmation
#
# Prompt preprocessing hook
# * [DONE] emit a status notification block when the demo plugin fires
# * [DONE] add a global plugin config to control the in-place status update demo
# * [DONE] handle "Abort" requests from server (including sending "Aborted" responses)
# * [DONE] catch hook invocation failures and send "Error" responses
# * [DONE] this includes adding runtime checks for the hook returning the wrong type
#
# Token generator hook
# * add an example plugin for this (probably proxying a remote LM Studio instance)
# * define the channel, hook invocation task and hook invocation controller for this hook
# * main request initiation message is "Generate"
# * handle "Abort" requests from server (including sending "Aborted" responses)
# * add controller API for fragment generation
# * add controller API for tool call generation
# * add controller API to indicate when token generation for a given request is completed (or failed)
# * catch hook invocation failures and send "Error" responses
#
# Tools provider hook
# * [DONE] add example synchronous tool plugin (dice rolling)
# * [DONE] add example asynchronous tool plugin (Wikipedia lookup) (note: requires async tool support in SDK)
# * [DONE] define the channel, hook invocation task and hook invocation controller for this hook
# * [DONE] main request initiation message is "InitSession" (with Initialized/Failed responses)
# * [DONE] handle "AbortToolCall" requests from server
# * [DONE] handle "CallTool" requests from server (including sending "CallComplete"/"CallError" response)
# * [DONE] handle "DiscardSession" requests from server
# * [DONE] add controller API for tool call status and warning reporting
#
# Plugin config field definitions
# * define approach for specifying plugin config field constraints and style options (e.g. numeric sliders)
# * [usable] numeric: https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-kv-config/src/valueTypes.ts#L99
# * [usable] string
# * [usable] boolean
# * select (array of strings, or value/label string pairs)
# * string array
