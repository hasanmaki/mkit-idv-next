# Copyright (c) 2026 okedigitalmedia/hasanmaki. All rights reserved.
"""Application settings and configuration management.

Provides Pydantic-based settings models (Google-style) used across the application,
including CORS, HTTPX, and database configuration. Use :func:`get_app_settings`
for a cached application settings instance.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class CorsConfig(BaseSettings):
    """CORS configuration settings."""

    model_config = {"env_prefix": "CORS_"}

    allow_origins: list[str] = ["http://localhost", "https://yourdomain.com"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = True


class HttpxConfig(BaseSettings):
    """HTTPX client configuration settings."""

    model_config = {"env_prefix": "HTTPX_"}

    timeout_seconds: float = 10.0
    max_connections: int = 100
    max_keepalive: int = 20
    retries: int = 3
    backoff_factor: float = 0.2


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = {"env_prefix": "DB_"}

    db_url: str = "sqlite+aiosqlite:///./application.db"


class RedisConfig(BaseSettings):
    """Redis configuration settings for orchestration runtime."""

    model_config = {"env_prefix": "REDIS_"}

    url: str = "redis://localhost:6379/0"
    lock_ttl_seconds: int = 30
    heartbeat_ttl_seconds: int = 90


class AppSettings(BaseSettings):
    """Application settings for FastAPI app."""

    app_name: str = "mkit-indosat voucher service"
    app_version: str = "0.1.0"
    debug: bool = True
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    httpx: HttpxConfig = Field(default_factory=HttpxConfig)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "env_nested_delimiter": "__",
    }


@lru_cache
def get_app_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()  # type: ignore
