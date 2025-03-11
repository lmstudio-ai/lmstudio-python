"""Runtime test suite configuration"""

import pytest

# Ensure support module assertions provide failure details
pytest.register_assert_rewrite("tests.support")
