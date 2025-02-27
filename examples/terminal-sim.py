#!/usr/bin/env python
"""Example script demonstrating a simulated terminal command processor."""

import readline # Enables input line editing

import lmstudio as lms

model = lms.llm()
console_history = []

while True:
    try:
        user_command = input("$ ")
    except EOFError:
        print()
        break
    if user_command.strip() == "exit":
        break
    console_history.append(f"$ {user_command}")
    history_prompt = "\n".join(console_history)
    prediction_stream = model.complete_stream(
        history_prompt,
        config={ "stopStrings": ["$"] },
    )
    for fragment in prediction_stream:
        print(fragment.content, end="", flush=True)
    print()
    console_history.append(prediction_stream.result().content)
