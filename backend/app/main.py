"""main entry point for the FastAPI application."""

import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    route_accounts,
    route_bindings,
    route_servers,
    route_tools,
    route_transactions,
)
from app.core.exceptions.handlers import register_exception_handlers
from app.core.log_config import configure_logging, get_logger
from app.core.middlewares import RequestLoggingMiddleware, TraceIDMiddleware
from app.core.settings import get_app_settings
from app.database.session import sessionmanager

settings = get_app_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Lifespan context manager for FastAPI app."""
    # Startup: run database migrations
    logger = get_logger("lifespan")

    try:
        # backend root directory
        backend_root = Path(__file__).resolve().parents[1]
        alembic_ini = backend_root / "alembic.ini"

        if not alembic_ini.exists():
            logger.warning(
                "Alembic configuration not found, skipping migrations",
                extra={"alembic_ini": str(alembic_ini)},
            )
        else:
            # Run alembic upgrade using subprocess with explicit config
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(alembic_ini),
                    "upgrade",
                    "head",
                ],
                cwd=str(backend_root),
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info("Database migrations completed successfully")
            else:
                logger.warning(
                    "Migration run completed with warnings",
                    extra={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                    },
                )
    except Exception as e:
        logger.error("Failed to run migrations: {}", e)
        raise

    yield
    # Shutdown: close database connection
    await sessionmanager.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

# Urutan penting: TraceID dulu, baru logging
app.add_middleware(TraceIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(route_servers.router, tags=["servers"], prefix="/v1/servers")
app.include_router(route_accounts.router, tags=["accounts"], prefix="/v1/accounts")
app.include_router(route_bindings.router, tags=["bindings"], prefix="/v1/bindings")
app.include_router(
    route_transactions.router, tags=["transactions"], prefix="/v1/transactions"
)

# New Tools Router

app.include_router(route_tools.router, tags=["tools"], prefix="/v1/tools")

# Register exception handlers setelah middleware
register_exception_handlers(app)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and orchestrators."""
    return {"status": "healthy"}


# Mount Static Files (Frontend)


# Fix: In Docker, frontend is at /app/frontend (one level up from /app/app)
# In development, it's at project_root/frontend (three levels up from app/app/main.py)
current_file_dir = os.path.dirname(__file__)  # /app/app
app_dir = os.path.dirname(current_file_dir)  # /app
frontend_path = os.path.join(app_dir, "frontend")  # /app/frontend

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
