"""for logging HTTP requests."""

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.log_config import trace_id_ctx

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
            # Try several sources for trace id: request.state, headers, or context var
            trace_id = (
                getattr(request.state, "trace_id", None)
                or request.headers.get("X-Trace-Id")
                or trace_id_ctx.get()
            )
            logger.bind(
                trace_id=trace_id,
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

        # Prefer a request-scoped logger if TraceIDMiddleware added it, otherwise bind trace id explicitly
        trace_id = (
            getattr(request.state, "trace_id", None)
            or request.headers.get("X-Trace-Id")
            or trace_id_ctx.get()
        )
        if hasattr(request.state, "logger"):
            bound = request.state.logger.bind(**log_data)
        else:
            bound = logger.bind(trace_id=trace_id, **log_data)

        if duration_ms > SLOW_REQUEST_MS:
            bound.warning("SLOW_REQUEST")
        elif 400 <= response.status_code < 500:
            bound.warning("CLIENT_ERROR_REQUEST")
        elif response.status_code >= 500:
            bound.error("SERVER_ERROR_REQUEST")
        else:
            bound.info("REQUEST")

        return response
