#!/usr/bin/env python
"""Example script demonstrating agent use of multiple tools."""

import math
import lmstudio as lms

def add(a: int, b: int) -> int:
    """Given two numbers a and b, returns the sum of them."""
    return a + b

def is_prime(n: int) -> bool:
    """Given a number n, returns True if n is a prime number."""
    if n < 2:
        return False
    sqrt = int(math.sqrt(n))
    for i in range(2, sqrt):
        if n % i == 0:
            return False
    return True

chat = lms.Chat()
model = lms.llm("qwen2.5-7b-instruct-1m")
model.act(
    "Is the result of 12345 + 45668 a prime? Think step by step.",
    [add, is_prime],
    on_message=chat.append,
)
print(chat)
