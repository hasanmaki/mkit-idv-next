# GEMINI.md

## Project Overview
**mkit-idv-next** is a high-throughput Voucher Management System with Identity Verification (IDV) integration. It orchestrates transactions across multiple bindings and servers while maintaining strict consistency and audit trails.

### Core Analogy: Laundry System
- **Server** = Mesin cuci (physical device/IDV provider)
- **Account** = Pakaian (MSISDN being processed)
- **Session** = Grup laundry (user/operator group)
- **Binding** = Tiket yang mengikat 1 pakaian ke 1 mesin untuk 1 grup

### Architecture & Patterns
- **Full-stack**: FastAPI (Backend) + React 19 (Frontend).
- **Domain-Driven Design (DDD)**:
  - **API Layer**: Thin HTTP handlers and request/response mapping.
  - **Application Layer**: Command/Query handlers (CQRS).
  - **Domain Layer**: Rich entities with behavior, value objects, and domain events.
  - **Infrastructure Layer**: Repositories and SQLAlchemy models.
- **Orchestration**: Dedicated worker (`app.orchestrator_main`) using **Redis** for distributed locking and state management.

---

## Building and Running

### Prerequisites
- Python 3.12+ (managed via `uv`)
- Node.js 18+
- Redis (required for orchestration)
- Docker (optional)

### Key Commands
- **Unified Dev**: `make dev` (Runs backend on :9914 and frontend on :5173)
- **Backend Only**: `cd backend && uv sync && uv run fastapi dev app/main.py --port 9914`
- **Frontend Only**: `cd frontend && npm install && npm run dev`
- **Orchestrator**: `python -m app.orchestrator_main`
- **Tests**: `pytest` (from `backend/` directory)

---

## Development Conventions

### Backend (Python)
- **Style**: Python 3.13 target, 88 char line length, double quotes.
- **Linting**: Enforced via **Ruff** (`ruff check --fix`).
- **Docstrings**: **Google-style mandatory** for all functions/classes (min 80% coverage via `interrogate`).
- **Type Hints**: Required for all declarations (checked via `pyright`). Use `|` for unions.
- **Database**: Use `AsyncSession`. Migrations via Alembic: `alembic revision --autogenerate`.
- **Error Handling**: Use custom exceptions from `app.core.exceptions`.
- **Logging**: Use `get_logger(__name__)` from `app.core.log_config`.

### Frontend (React)
- **Stack**: Vite, TypeScript, Tailwind CSS, shadcn/ui.
- **Structure**: Feature-based modules in `frontend/src/features/`.
- **Patterns**: Use React Hooks and custom API error handlers (`useApiError`).

---

## Domain Status & Business Rules
1. **1 Session** → multiple Accounts.
2. **1 Account** → bound to **exactly 1 Server** at a time.
3. **1 Server** → handles multiple Accounts **sequentially**.
4. **Isolation**: Accounts in use by one session cannot be used by another.

### Completed Domains
- **Servers**: Manage IDV provider devices (rate limiting, status).
- **Sessions**: Manage operator groups.
- **Bindings**: The link between account, server, and session (OTP workflow).
- **Accounts**: MSISDN management (WIP).
- **Transactions**: IDV execution and orchestration (WIP).
