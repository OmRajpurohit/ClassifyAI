"""Pytest configuration and environment fixture setup.

Automatically injects the `backend` directory into `sys.path` so that imports
of the `app` package work seamlessly regardless of whether pytest is invoked
from the project root, from inside the backend directory, or through an IDE test runner.
"""

import os
import sys
from pathlib import Path

# Resolve path to backend directory (one level up from tests/)
BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
