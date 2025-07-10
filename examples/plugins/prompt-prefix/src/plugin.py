"""Example plugin that adds a prefix to all user prompts."""

from lmstudio.plugin import BaseConfig, ConfigString, PromptPreprocessorController
from lmstudio import AnyChatMessage, AnyChatMessageDict, TextDataDict

class ConfigSchematic(BaseConfig):
    """Naming the class 'ConfigSchematic' implicitly registers it."""
    # Assigning ConfigSchematic = SomeOtherSchemaClass also works
    prefix: ConfigString = ConfigString(
        label="Prefix to insert",
        hint="This text will be inserted at the start of all user prompts",
        default="And now for something completely different: ",
    )

async def preprocess_prompt(_ctl: PromptPreprocessorController, message: AnyChatMessage) -> AnyChatMessageDict|None:
    """Naming the function 'preprocess_prompt' implicitly registers it."""
    # Assigning preprocess_prompt = some_other_callable also works
    if message.role != "user":
        return None
    modified_message = message.to_dict()
    # Add a prefix to all user messages
    prefix: TextDataDict = {
        "type": "text",
        "text": "And now for something completely different:",
    }
    modified_message["content"] = [prefix, *modified_message["content"]]
    return modified_message
