#!/usr/bin/env python
"""Example script demonstrating an interactive LLM chatbot."""

import json

import lmstudio as lm

class BookSchema(lm.BaseModel):
    """Structured information about a published book."""
    title: str
    author: str
    year: int

model = lm.llm()

result = model.respond("Tell me about The Hobbit", response_format=BookSchema)
book = result.parsed

print(json.dumps(book, indent=2))
