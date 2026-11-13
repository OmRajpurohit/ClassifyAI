"""Main FastAPI Application Entrypoint for ClassifyAI.
"""

import os
import sys
from pathlib import Path

# Ensure 'backend' directory is always in sys.path regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router

# Parse allowed origins from environment with sensible local dev defaults
env_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
)
allowed_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]

app = FastAPI(
    title="ClassifyAI — Intelligent Classifier Selection Agent",
    description=(
        "An autonomous, rule-based machine learning agent API that analyzes tabular datasets, "
        "builds anti-leakage preprocessing pipelines, evaluates multiple classification algorithms "
        "via Stratified Cross-Validation, and deterministically ranks models to identify the optimal classifier."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local React development without permitting arbitrary origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root() -> dict:
    """Root entry point providing basic API info and interactive documentation link."""
    return {
        "project": "ClassifyAI — Intelligent Classifier Selection Agent",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler to intercept unhandled errors and return structured JSON."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error_message": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
