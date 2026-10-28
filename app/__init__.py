"""Root proxy package forwarding 'app' imports to 'backend/app'."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Extend package search path to point directly to backend/app
BACKEND_APP_DIR = BACKEND_DIR / "app"
__path__ = [str(BACKEND_APP_DIR)]
