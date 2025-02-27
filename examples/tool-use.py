#!/usr/bin/env python
"""Example script demonstrating agent tool use."""

import lmstudio as lm

def multiply(a: float, b: float) -> float:
    """Given two numbers a and b. Returns the product of them."""
    return a * b

model = lm.llm("qwen2.5-7b-instruct")
model.act(
    "What is the result of 12345 multiplied by 54321?",
    [multiply],
    on_message=print,
)
