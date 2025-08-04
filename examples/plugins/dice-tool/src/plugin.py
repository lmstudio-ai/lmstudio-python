"""Example plugin that provide dice rolling tools."""

import time

from random import randint
from typing import TypedDict

from lmstudio.plugin import (
    BaseConfigSchema,
    ToolsProviderController,
    config_field,
    get_tool_call_context,
)
from lmstudio import ToolDefinition


# Assigning ConfigSchema = SomeOtherSchemaClass also works
class ConfigSchema(BaseConfigSchema):
    """The name 'ConfigSchema' implicitly registers this as the per-chat plugin config schema."""

    enable_inplace_status_demo: bool = config_field(
        label="Enable in-place status demo",
        hint="The plugin will run an in-place task status updating demo when invoked",
        default=True,
    )
    inplace_status_duration: float = config_field(
        label="In-place status total duration (s)",
        hint="The number of seconds to spend displaying the in-place task status update",
        default=5.0,
    )
    restrict_die_types: bool = config_field(
        label="Require polyhedral dice",
        hint="Require conventional polyhedral dice (4, 6, 8, 10, 12, 20, or 100 sides)",
        default=True,
    )


# This example plugin has no global configuration settings defined.
# For a type hinted plugin with no configuration settings of a given type,
# BaseConfigSchema may be used in the hook controller type hint.
# Defining a config schema subclass with no fields is also a valid approach.


# When reporting multiple values from a tool call, dictionaries
# are the preferred format, as the field names allow the LLM
# to potentially interpret the result correctly.
# Unlike parameter details, no return value schema is sent to the server,
# so relevant information needs to be part of the JSON serialisation.
class DiceRollResult(TypedDict):
    """The result of a dice rolling request."""

    rolls: list[int]
    total: int


# Assigning list_provided_tools = some_other_callable also works
async def list_provided_tools(
    ctl: ToolsProviderController[ConfigSchema, BaseConfigSchema],
) -> list[ToolDefinition]:
    """Naming the function 'list_provided_tools' implicitly registers it."""
    config = ctl.plugin_config
    if config.enable_inplace_status_demo:
        inplace_status_duration = config.inplace_status_duration
    else:
        inplace_status_duration = 0
    if config.restrict_die_types:
        permitted_sides = {4, 6, 8, 10, 12, 20, 100}
    else:
        permitted_sides = None

    # Return value may be any iterable, but a list will typically be simplest
    # Tool definitions may use any of the formats described in
    # https://lmstudio.ai/docs/python/agent/tools
    def roll_dice(count: int, sides: int) -> DiceRollResult:
        """Roll a specified number of dice with specified number of faces.

        For example, to roll 2 six-sided dice (i.e. 2d6), you should call the function
        `roll_dice` with the parameters { count: 2, sides: 6 }.
        """
        if inplace_status_duration:
            tcc = get_tool_call_context()
            status_updates = (
                (tcc.notify_status, "Display status update in UI."),
                (tcc.notify_warning, "Display task warning in UI."),
                (tcc.notify_status, "Post-warning status update in UI."),
            )
            status_duration = inplace_status_duration / len(status_updates)
            for send_notification, status_text in status_updates:
                time.sleep(status_duration)
                send_notification(status_text)
            # TODO: Add a tool calling UI status/warning demo here
            time.sleep(inplace_status_duration)
        if permitted_sides and sides not in permitted_sides:
            expected_die_types = ",".join(map(str, sorted(permitted_sides)))
            err_msg = f"{sides} is not a conventional polyhedral die type ({expected_die_types})"
            raise ValueError(err_msg)
        rolls = [randint(1, sides) for _ in range(count)]
        return DiceRollResult(rolls=rolls, total=sum(rolls))

    return [roll_dice]


print(f"{__name__} initialized from {__file__}")
