"""Example plugin that provide dice rolling tools."""

from lmstudio.plugin import BaseConfigSchema, ToolsProviderController
from lmstudio import ToolDefinition

from random import randint
from typing import TypedDict

# For a type hinted plugin with no configuration settings,
# BaseConfigSchema may be used in the hook controller type hint.
# It's also acceptable to define subclasses with no fields.


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
    ctl: ToolsProviderController[BaseConfigSchema, BaseConfigSchema],
) -> list[ToolDefinition]:
    """Naming the function 'list_provided_tools' implicitly registers it."""

    # Return value may be any iterable, but a list will typically be simplest
    # Tool definitions may use any of the formats described in
    # https://lmstudio.ai/docs/python/agent/tools
    def roll_dice(count: int, sides: int) -> DiceRollResult:
        """Roll a specified number of dice with specified number of faces.

        For example, to roll 2 six-sided dice (i.e. 2d6), you should call the function
        `roll_dice` with the parameters { count: 2, sides: 6 }.
        """
        rolls = [randint(1, sides) for _ in range(count)]
        return DiceRollResult(rolls=rolls, total=sum(rolls))

    return [roll_dice]


print(f"{__name__} initialized from {__file__}")
