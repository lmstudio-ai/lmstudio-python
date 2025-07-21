# Plugin runner doesn't actually care these type hints are incorrect
# It *does* care that the returned "user message" has no content
async def preprocess_prompt(_ctl: None, _message: None) -> dict[None, None]:
    return {}
