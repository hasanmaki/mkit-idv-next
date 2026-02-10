"""main entry point for the FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import route_servers  # , bindings
from app.core.exceptions.handlers import register_exception_handlers
from app.core.log_config import configure_logging
from app.core.middlewares import RequestLoggingMiddleware, TraceIDMiddleware
from app.core.settings import get_app_settings
from app.database.session import sessionmanager
from app.database.tables import create_tables

settings = get_app_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Lifespan context manager for FastAPI app."""
    # Startup: create tables
    await create_tables()
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

app.include_router(route_servers.router, prefix="/v1/servers")
# app.include_router(bindings.router, prefix="/v1/bindings")

# Register exception handlers setelah middleware
register_exception_handlers(app)
