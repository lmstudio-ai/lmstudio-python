"""Runtime test suite configuration"""

import pytest


# Ensure support module assertions provide failure details
pytest.register_assert_rewrite("tests.support")

# Session-scoped fixture for required model loading
import asyncio
import sys

@pytest.fixture(scope="session", autouse=True)
def load_required_models():
    """Load required models at the start of the test session."""
    # Only run if LM Studio is accessible
    try:
        from tests.load_models import reload_models
        asyncio.run(reload_models())
    except Exception as e:
        print(f"[Fixture] Skipping model loading: {e}", file=sys.stderr)
    yield
    # Optionally unload models at the end of the session
    try:
        from tests.unload_models import unload_models
        asyncio.run(unload_models())
    except Exception as e:
        print(f"[Fixture] Skipping model unloading: {e}", file=sys.stderr)
