"""Support for implementing LM Studio plugins in Python."""

# Using wildcard imports to export API symbols is acceptable
# ruff: noqa: F403

from .sdk_api import *
from .config_schemas import *
from .runner import *

# Initial Python plugin SDK TODO list
#
# General tasks
# * refactor hook channel and controller definitions out to a submodule
# * refactor hook registration to be data driven instead of hardcoded in the runner
# * refactor to allow "Abort" request handling to be common across hook invocation tasks
# * refactor to allow hook invocation error handling to be common across hook invocation tasks
# * add common controller APIs for hook invocation status reporting
#
# Prompt preprocessing hook
# * emit a status notification block when the demo plugin fires
# * handle "Abort" requests from server (including sending "Aborted" responses)
# * catch hook invocation failures and send "Error" responses
# * this includes adding runtime checks for the hook returning the wrong type
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
# * add example plugin or plugins for this (probably both dice rolling and Wikipedia lookup)
# * define the channel, hook invocation task and hook invocation controller for this hook
# * main request initiation message is "InitSession" (with Initialized/Failed responses)
# * handle "Abort" requests from server (including sending "Aborted" responses)
# * handle "CallTool" requests from server (including sending "CallComplete"/"CallError" response)
# * handle "DiscardSession" requests from server
# * add controller API for tool call status and warning reporting
#
# Plugin config field definitions
# * define approach for specifying plugin config field constraints and style options (e.g. numeric sliders)
# * numeric: https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-kv-config/src/valueTypes.ts#L99
# * string
# * select (array of strings, or value/label string pairs)
# * boolean
# * string array
