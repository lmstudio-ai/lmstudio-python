"""Allow execution of this subpackage as a script."""

import sys

from .cli import main

# Handle multiprocessing potentially re-running this module with a name other than `__main__`
if __name__ == "__main__":
    sys.exit(main())
