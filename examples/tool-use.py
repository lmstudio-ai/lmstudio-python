#!/usr/bin/env python
"""Example script demonstrating agent tool use."""

import lmstudio as lms

def multiply(a: float, b: float) -> float:
    """Given two numbers a and b. Returns the product of them."""
    return a * b

chat = lms.Chat()
model = lms.llm("qwen2.5-7b-instruct-1m")
model.act(
    "What is the result of 12345 multiplied by 54321?",
    [multiply],
    on_message=chat.append,
)
print(chat)
