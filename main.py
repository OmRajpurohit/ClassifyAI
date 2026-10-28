"""Root entrypoint launcher for ClassifyAI Backend.

Run directly from root:
    python main.py
"""
import os
import sys
from pathlib import Path
import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Also export PYTHONPATH for any spawned reload processes
current_pythonpath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = (
    f"{str(BACKEND_DIR)}{os.pathpsep}{current_pythonpath}"
    if current_pythonpath
    else str(BACKEND_DIR)
)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ClassifyAI Backend Server at http://{host}:{port} ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True, app_dir=str(BACKEND_DIR))
