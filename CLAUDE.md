# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack voucher management system with IDV integration.

**Backend**: FastAPI application for managing Indosat voucher (IDV) transactions. Handles server management, account bindings, and transaction processing with comprehensive audit logging and retry mechanisms for external service calls.

**Frontend**: React + Vite + TypeScript + Tailwind CSS + shadcn/ui for the dashboard interface.

## Development Commands

### Frontend

All commands should be run from the `frontend/` directory.

```bash
cd frontend

# Install dependencies
npm install

# Run dev server (proxies API to backend at localhost:9914)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

The Vite dev server proxies API requests to the backend:
- `/v1/*` → backend API routes
- `/health` → backend health check

Configure `VITE_PROXY_TARGET` env var to change the proxy target (default: `http://127.0.0.1:8000`).

### Backend

All commands should be run from the `backend/` directory.

### Docker Development

For containerized development with hot-reload on frontend:

```bash
# Development mode (frontend Vite dev + backend)
docker compose -f docker-compose.dev.yml up --build

# Production-like mode (static frontend + backend)
docker compose up --build
```

Frontend dev server: http://localhost:5173
Backend API: http://localhost:9914

**Hot reload**: File changes are volume-mounted. Backend (uvicorn --reload) and orchestrator auto-restart on Python file changes. Frontend Vite dev server HMR's automatically.

### Running the Application

```bash
cd backend
fastapi dev app/main.py
# Or with uvicorn directly:
uvicorn app.main:app --reload
```

### Testing

```bash
# Run all tests with coverage
cd backend
pytest

# Run specific test markers
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests
pytest -m api              # API tests
pytest -m database         # Database tests

# Run single test file
pytest tests/api/test_servers_routes.py

# Run with specific verbosity
pytest -v tests/services/

# Run in parallel (faster)
pytest -n auto
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history
```

### Code Quality

```bash
cd backend

# Format and lint (auto-fix)
ruff check --fix
ruff format

# Lint only (no fix)
ruff check

# Check docstring coverage (minimum 80% required)
interrogate app -c pyproject.toml
# Or from repo root:
interrogate backend/app -c backend/pyproject.toml
```

## Architecture

### Overview

The system is a full-stack voucher management application with a worker orchestration layer:
- **Backend**: FastAPI service managing servers, accounts, bindings, and transactions with external IDV API integration
- **Frontend**: React dashboard for CRUD operations and monitoring
- **Orchestrator**: Redis-backed worker service that runs automated voucher purchase loops on bindings

### Frontend Architecture

**Feature-based organization** ([frontend/src/features/](frontend/src/features/))

Each feature domain (servers, accounts, bindings, transactions) is self-contained with:
- `components/` - Feature-specific React components
- `hooks/` - Custom React hooks managing state and API calls
- `types.ts` - TypeScript types for the domain

**Shared UI components** ([frontend/src/components/](frontend/src/components/))

- `ui/` - shadcn/ui components (Button, Dialog, Input, Table, etc.)
- Shared components use the `@/components/ui` import alias

**API layer** ([frontend/src/lib/api.ts](frontend/src/lib/api.ts))

- `apiRequest<T>(path, method, body)` - Generic fetch wrapper
- Centralized error handling with toast notifications (via `sonner`)
- `VITE_API_BASE_URL` env var for API base URL (empty in dev with proxy)

**Types** ([frontend/src/types/](frontend/src/types/))

- Domain types mirror backend Pydantic schemas (e.g., `Server`, `Account`)
- Payload types for create/update operations
- Result types for bulk operations

**Build system**: Vite with React plugin, Tailwind CSS v4 via `@tailwindcss/vite`, TypeScript strict mode

### Backend Architecture

The codebase follows a clean layered architecture:

**API Layer** ([app/api/](backend/app/api/))

- Thin route handlers using FastAPI routers
- Input validation via Pydantic schemas
- Dependency injection for database sessions
- Routes: `route_servers.py`, `route_accounts.py`, `route_bindings.py`, `route_transactions.py`

**Service Layer** ([app/services/](backend/app/services/))

- Business logic and validation
- Each domain has its own service module (servers, accounts, bindings, transactions, idv)
- Services instantiate repositories and coordinate operations
- Pattern: `ServiceName(session: AsyncSession)` constructor
- Contains both service classes and Pydantic schemas for each domain

**Repository Layer** ([app/repos/](backend/app/repos/))

- Data access abstraction built on `BaseRepository` generic class
- CRUD operations: `get()`, `get_by()`, `get_multi()`, `create()`, `update()`, `delete()`
- All methods accept `commit: bool = False` parameter for transaction control
- Repositories take SQLAlchemy model type in constructor: `repo = ServerRepository(Servers)`

**Model Layer** ([app/models/](backend/app/models/))

- SQLAlchemy ORM models (tables)
- All models inherit from `Base` and typically `TimestampMixin` (adds created_at/updated_at)
- Tables: `servers`, `accounts`, `bindings`, `transactions`, `transaction_statuses`

**Core** ([app/core/](backend/app/core/))

- `settings.py`: Pydantic settings with env var support (CORS, HTTPX, Database config)
- `clients.py`: `BaseHTTPClient` with httpx-retries for external API calls
- `exceptions/`: Custom exceptions (`AppNotFoundError`, `AppValidationError`, etc.) with structured error responses
- `middlewares/`: `TraceIDMiddleware` (must be added before logging), `RequestLoggingMiddleware`
- `log_config.py`: Loguru configuration with trace ID context and layer-based logging

**Database** ([app/database/](backend/app/database/))

- `session.py`: `DatabaseSessionManager` singleton, `get_db_session()` dependency
- `tables.py`: `create_tables()` called at app startup
- SQLite with aiosqlite by default (configured via `DB__DB_URL` env var)

### Request Flow

1. FastAPI route receives request
2. Route depends on `get_db_session()` for database access
3. Route instantiates service: `service = ServerService(session)`
4. Service validates business rules and calls repository methods
5. Repository performs database operations via SQLAlchemy
6. Service may use `BaseHTTPClient` for external API calls
7. Response returns through service → route → FastAPI response model

### Database Sessions

- Sessions auto-commit on successful request completion
- Sessions auto-rollback on exceptions
- Repositories can flush without committing by using `commit=False` (default)
- Service layer coordinates multi-step operations within a single transaction
- Alembic migrations run automatically at app startup (see `lifespan()` in main.py)

### Frontend Hook Pattern

Custom hooks in `features/*/hooks/` encapsulate all business logic for a feature:
- State management (servers, dialogs, forms, selections)
- API calls via `apiRequest()`
- Toast notifications via `sonner`
- Optimistic updates and error handling
- Return object with state, setters, and action handlers

Example: `useServers()` hook manages all server CRUD operations, dialogs, form state, and selection state.

### Orchestrator Service

The orchestrator (`app/orchestrator_main.py`) manages worker loops for automated voucher transactions:
- Redis-backed state management for worker coordination (locks, heartbeats, status)
- Workers bind to specific bindings and execute transaction flows (balance → product purchase → OTP)
- Control endpoints: start, pause, resume, stop workers (under `/v1/orchestration/`)
- Monitor endpoint: `/v1/orchestration/monitor` returns worker state and heartbeat status
- Hot-reload: orchestrator container auto-restarts on code changes during development

## Important Patterns

### API Route Decoration Pattern

**CRITICAL**: List endpoints must be decorated with BOTH `""` AND `"/"` to handle requests with and without trailing slashes:

```python
@router.get("", response_model=list[ModelRead])
@router.get("/", response_model=list[ModelRead], include_in_schema=False)
async def list_items(...):
```

- First decorator handles `/v1/resource` (no trailing slash)
- Second decorator handles `/v1/resource/` (with trailing slash)
- `include_in_schema=False` prevents duplicate OpenAPI docs

Without both decorators, requests without trailing slash return 404. See `route_servers.py` and `route_accounts.py` for reference.

### Logging

- Use `get_logger(name)` from `app.core.log_config`
- Structured logging with extra context: `logger.info("message", extra={"key": "value"})`
- Every request has a `trace_id` automatically added via middleware
- Layer-based logging (API, service, repo, db) configured in `mlog.yaml`

### Error Handling

- Custom exceptions in `app/core/exceptions/` with structured error codes
- All exceptions have `message`, `error_code`, and optional `context` dict
- Global exception handlers registered in `main.py`
- HTTP client wraps timeouts/errors as `AppExternalServiceTimeoutError`

### External HTTP Calls

- Always use `BaseHTTPClient` from `app.core.clients`
- Automatic retries with exponential backoff (configured in settings)
- Structured logging of requests/responses with trace IDs
- Timeout handling with clear error messages

### Docstrings

- **Mandatory**: All modules, classes, and public methods require Google-style docstrings
- Minimum 80% coverage enforced by `interrogate`
- Test files excluded from docstring requirements
- Run `interrogate app` before committing to verify coverage

## Configuration

Settings loaded from environment variables with fallback defaults:

- `DB__DB_URL`: Database URL (default: sqlite+aiosqlite:///./application.db)
- `CORS__ALLOW_ORIGINS`: List of allowed origins
- `HTTPX__TIMEOUT_SECONDS`: HTTP client timeout (default: 10.0)
- `HTTPX__RETRIES`: Number of retry attempts (default: 3)

Nested settings use double underscore: `DB__DB_URL`, `CORS__ALLOW_ORIGINS`

## Testing Standards

- All test files in `backend/tests/` mirror the `app/` structure
- Test markers: `unit`, `integration`, `api`, `database`, `e2e`
- Use `pytest-asyncio` for async tests (asyncio_mode = "auto")
- Coverage reports generated in `.reports/coverage/`
- HTML test reports in `.reports/tests/report.html`
- Tests should not require docstrings (excluded via ruff config)

## Code Style

### Frontend

- ESLint with `eslint.config.js` for React and TypeScript
- Prettier-style formatting via Vite
- Path alias: `@/` → `src/` (configured in `vite.config.ts`)
- Import sorting via `isort` equivalent

### Backend

Enforced by Ruff:

- Line length: 88 characters
- Quote style: double quotes
- Google-style docstrings required
- Type hints required (flake8-annotations)
- Import sorting (isort)
- Modern Python syntax (pyupgrade for 3.13+)

Ignored rules:

- E501: Line length (handled by formatter)
- D107: `__init__` docstrings
- ANN201/ANN202: Return types for `cls`/`self`
- ANN401: `Any` type allowed
- TRY003: Long exception messages allowed
