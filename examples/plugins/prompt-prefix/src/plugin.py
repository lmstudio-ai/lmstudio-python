"""Example plugin that adds a prefix to all user prompts."""

import asyncio

from lmstudio.plugin import BaseConfigSchema, PromptPreprocessorController, config_field
from lmstudio import AnyChatMessage, AnyChatMessageDict, TextDataDict


# Assigning ConfigSchema = SomeOtherSchemaClass also works
class ConfigSchema(BaseConfigSchema):
    """The name 'ConfigSchema' implicitly registers this as the per-chat plugin config schema."""

    prefix: str = config_field(
        label="Prefix to insert",
        hint="This text will be inserted at the start of all user prompts",
        default="And now for something completely different: ",
    )


# Assigning GlobalConfigSchema = SomeOtherGlobalSchemaClass also works
class GlobalConfigSchema(BaseConfigSchema):
    """The name 'GlobalConfigSchema' implicitly registers this as the global plugin config schema."""

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


async def preprocess_prompt(
    ctl: PromptPreprocessorController[ConfigSchema, GlobalConfigSchema],
    message: AnyChatMessage,
) -> AnyChatMessageDict | None:
    """Naming the function 'preprocess_prompt' implicitly registers it."""
    # Assigning preprocess_prompt = some_other_callable also works
    if message.role != "user":
        return None
    print(f"Running prompt preprocessor hook from {__file__} with {ctl.plugin_config}")
    if ctl.global_config.enable_inplace_status_demo:
        # Run an in-place status prompt update demonstration
        status_block = await ctl.notify_start("Starting task (shows a static icon).")
        status_updates = (
            (status_block.notify_working, "Task in progress (shows a dynamic icon)."),
            (status_block.notify_error, "Reporting an error status."),
            (status_block.notify_canceled, "Reporting cancellation."),
            (
                status_block.notify_done,
                "In-place status update demonstration completed.",
            ),
        )
        status_duration = ctl.global_config.inplace_status_duration / len(
            status_updates
        )
        for notification, status_text in status_updates:
            await asyncio.sleep(status_duration)
            await notification(status_text)
    modified_message = message.to_dict()
    # Add a prefix to all user messages
    prefix_text = ctl.plugin_config.prefix
    prefix: TextDataDict = {
        "type": "text",
        "text": prefix_text,
    }
    modified_message["content"] = [prefix, *modified_message["content"]]
    # Demonstrate simple completion status reporting for non-blocking operations
    await ctl.notify_done(f"Added prefix {prefix_text!r} to user message.")
    return modified_message


print(f"{__name__} initialized from {__file__}")
