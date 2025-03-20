#!/usr/bin/env python
"""Example script demonstrating structured responses."""

import json

import lmstudio as lms

class BookSchema(lms.BaseModel):
    """Structured information about a published book."""
    title: str
    author: str
    year: int

model = lms.llm()

result = model.respond("Tell me about The Hobbit", response_format=BookSchema)
book = result.parsed

print(json.dumps(book, indent=2))
