"""Middleware to handle trace IDs for requests."""

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.log_config import trace_id_ctx


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Inject trace_id into request context and response headers."""

    async def dispatch(self, request: Request, call_next):
        """Add or generate a trace_id for the request."""
        trace_id = (
            request.headers.get("X-Trace-Id")
            or request.headers.get("X-Request-Id")
            or uuid4().hex
        )
        request.state.trace_id = trace_id
        token = trace_id_ctx.set(trace_id)

        try:
            response = await call_next(request)
            response.headers["X-Trace-Id"] = trace_id
            return response
        finally:
            trace_id_ctx.reset(token)
