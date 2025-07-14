"""Example plugin that adds a prefix to all user prompts."""
import asyncio

from lmstudio.plugin import BaseConfigSchema, ConfigString, PromptPreprocessorController
from lmstudio import AnyChatMessage, AnyChatMessageDict, TextDataDict

class ConfigSchema(BaseConfigSchema):
    """Naming the class 'ConfigSchematic' implicitly registers it."""
    # Assigning ConfigSchematic = SomeOtherSchemaClass also works
    prefix: ConfigString = ConfigString(
        label="Prefix to insert",
        hint="This text will be inserted at the start of all user prompts",
        default="And now for something completely different: ",
    )

# TODO: Add a global config schema that controls whether the plugin runs
#       the in-place status update demonstration, and how long it delays
#       (needs boolean field and numeric field support in the config API)

async def preprocess_prompt(ctl: PromptPreprocessorController, message: AnyChatMessage) -> AnyChatMessageDict|None:
    """Naming the function 'preprocess_prompt' implicitly registers it."""
    # Assigning preprocess_prompt = some_other_callable also works
    if message.role != "user":
        return None
    print(f"Running prompt preprocessor hook from {__file__} with {ctl.plugin_config}")
    if True:
        # Run an in-place status prompt update demonstration
        status_block = await ctl.notify_start("Starting task (shows a static icon).")
        await asyncio.sleep(2)
        await status_block.notify_working("Task in progress (shows a dynamic icon).")
        await asyncio.sleep(2)
        await status_block.notify_error("Reporting an error status.")
        await asyncio.sleep(2)
        await status_block.notify_canceled("Reporting cancellation.")
        await asyncio.sleep(2)
        await status_block.notify_done("In-place status update demonstration completed.")
    modified_message = message.to_dict()
    # Add a prefix to all user messages
    prefix_text = ctl.plugin_config["prefix"]
    prefix: TextDataDict = {
        "type": "text",
        "text": prefix_text,
    }
    modified_message["content"] = [prefix, *modified_message["content"]]
    # Demonstrate simple completion status reporting for non-blocking operations
    await ctl.notify_done(f"Added prefix {prefix_text!r} to user message.")
    return modified_message

print(f"{__name__} initialized from {__file__}")
