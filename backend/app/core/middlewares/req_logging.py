"""for logging HTTP requests."""

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

SLOW_REQUEST_MS = 1000


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests with duration and status."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        """Log the HTTP request details."""
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.bind(
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            ).exception("REQUEST_FAILED")
            raise

        duration_ms = int((time.perf_counter() - start) * 1000)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "-")

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "user_agent": user_agent,
        }

        # Gunakan trace_id dari context (sudah di-set oleh TraceIDMiddleware)
        bound = logger.bind(**log_data)

        if duration_ms > SLOW_REQUEST_MS:
            bound.warning("SLOW_REQUEST")
        elif 400 <= response.status_code < 500:
            bound.warning("CLIENT_ERROR_REQUEST")
        elif response.status_code >= 500:
            bound.error("SERVER_ERROR_REQUEST")
        else:
            bound.info("REQUEST")

        return response
