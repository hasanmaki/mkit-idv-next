"""HTTP client with retry logic and structured logging."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from httpx_retries import Retry, RetryTransport

from app.core.exceptions import (
    AppExternalServiceError,
    AppExternalServiceTimeout,
)
from app.core.log_config import get_logger, trace_id_ctx
from app.core.settings import get_app_settings


class BaseHTTPClient:
    """Base HTTP client with retry and structured logging."""

    def __init__(
        self,
        base_url: str,
        timeout: float | None = None,
        retries: int | None = None,
        backoff_factor: float | None = None,
        max_connections: int | None = None,
        max_keepalive: int | None = None,
        service_name: str = "http_client",
    ):
        settings = get_app_settings()
        httpx_cfg = settings.httpx

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout if timeout is not None else httpx_cfg.timeout_seconds
        self.retries = retries if retries is not None else httpx_cfg.retries
        self.backoff_factor = (
            backoff_factor if backoff_factor is not None else httpx_cfg.backoff_factor
        )
        self.max_connections = (
            max_connections if max_connections is not None else httpx_cfg.max_connections
        )
        self.max_keepalive = (
            max_keepalive if max_keepalive is not None else httpx_cfg.max_keepalive
        )
        self.service_name = service_name
        self.logger = get_logger(f"client.{service_name}")

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[httpx.AsyncClient]:
        """Context manager for HTTP client lifecycle."""
        retry = Retry(total=self.retries, backoff_factor=self.backoff_factor)
        transport = RetryTransport(retry=retry)
        limits = httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive,
        )
        timeout = httpx.Timeout(self.timeout)
        client = httpx.AsyncClient(
            timeout=timeout,
            transport=transport,
            limits=limits,
        )
        try:
            yield client
        finally:
            await client.aclose()

    async def _make_request_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Make request with retry logic and structured logging."""
        url = f"{self.base_url}{endpoint}"
        trace_id = trace_id_ctx.get("no-trace")

        log_extra = {
            "method": method,
            "url": url,
            "service": self.service_name,
            "trace_id": trace_id,
        }
        self.logger.info("HTTP_REQUEST_INITIATED", extra=log_extra)

        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()

            success_extra = {
                **log_extra,
                "status_code": response.status_code,
            }
            self.logger.info("HTTP_REQUEST_SUCCESS", extra=success_extra)
            return response.json()

        except httpx.HTTPStatusError as e:
            error_extra = {
                **log_extra,
                "status_code": e.response.status_code,
                "error": str(e),
            }

            if 400 <= e.response.status_code < 500:
                self.logger.warning("HTTP_CLIENT_ERROR", extra=error_extra)
            else:
                self.logger.error("HTTP_SERVER_ERROR", extra=error_extra)

            raise AppExternalServiceError(
                message="Layanan eksternal mengembalikan respons error.",
                error_code="external_service_http_error",
                context=error_extra,
                original_exception=e,
            ) from e

        except httpx.TimeoutException as e:
            error_extra = {**log_extra, "error": str(e)}
            self.logger.warning("HTTP_TIMEOUT_ERROR", extra=error_extra)
            raise AppExternalServiceTimeout(
                message="Layanan eksternal timeout.",
                error_code="external_service_timeout",
                context=error_extra,
                original_exception=e,
            ) from e

        except httpx.NetworkError as e:
            error_extra = {**log_extra, "error": str(e)}
            self.logger.error("HTTP_NETWORK_ERROR", extra=error_extra)
            raise AppExternalServiceError(
                message="Gagal terhubung ke layanan eksternal.",
                error_code="external_service_network_error",
                context=error_extra,
                original_exception=e,
            ) from e

        except ValueError as e:
            error_extra = {**log_extra, "error": str(e)}
            self.logger.error("HTTP_RESPONSE_DECODE_ERROR", extra=error_extra)
            raise AppExternalServiceError(
                message="Respons layanan eksternal tidak valid.",
                error_code="external_service_invalid_response",
                context=error_extra,
                original_exception=e,
            ) from e

        except Exception as e:
            error_extra = {**log_extra, "error": str(e)}
            self.logger.error("HTTP_UNEXPECTED_ERROR", extra=error_extra)
            raise AppExternalServiceError(
                message="Kesalahan tak terduga pada layanan eksternal.",
                error_code="external_service_unexpected_error",
                context=error_extra,
                original_exception=e,
            ) from e

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Public helper for JSON requests."""
        async with self.get_client() as client:
            return await self._make_request_with_retry(
                client,
                method,
                endpoint,
                **kwargs,
            )
