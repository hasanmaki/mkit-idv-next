# Stage 1: Frontend builder
FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy source and build
COPY frontend/ ./

# Build CSS with Tailwind
RUN npm run build

# Stage 2: Backend runtime
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=9914

# Copy dependency files
COPY backend/pyproject.toml ./

# Install dependencies
# Will create lockfile if missing, or use existing one
RUN uv sync --no-install-project

# Copy application source code
COPY backend/app ./app
COPY backend/mlog.yaml ./mlog.yaml

# Install the project package
RUN uv sync

# Copy built frontend assets from builder stage
# FastAPI serves this as static files at "/"
COPY --from=frontend-builder /build/frontend/dist /app/frontend

# Copy alembic migrations and config
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

# Expose port
EXPOSE ${PORT}

# Health check for orchestrators (Docker Compose, Kubernetes, etc.)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9914/health')" || exit 1

# Run with uv to activate the virtual environment
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9914"]
