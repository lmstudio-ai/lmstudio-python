# Plugin runner doesn't actually care these type hints are incorrect
# It *does* care that an exception is raised
class ExampleCustomException(Exception):
    pass


async def preprocess_prompt(_ctl: None, _message: None) -> dict[None, None]:
    raise ExampleCustomException("Example plugin hook failure")
