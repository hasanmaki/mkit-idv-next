# Agent Instructions

FastAPI application for managing Indosat voucher (IDV) transactions. Uses layered architecture with async SQLAlchemy.

## Working Directory

All commands run from `backend/` directory.

## Build Commands

```bash
# Install dependencies
uv sync

# Run application
cd backend
fastapi dev app/main.py
# Or: uvicorn app.main:app --reload
```

## Test Commands

```bash
cd backend

# Run all tests
pytest

# Run single test file
pytest tests/api/test_servers_routes.py

# Run single test function
pytest tests/api/test_servers_routes.py::test_create_server_route -v

# Run by marker
pytest -m unit
pytest -m integration
pytest -m api
pytest -m database

# Run in parallel
pytest -n auto
```

## Lint Commands

```bash
cd backend

# Format and lint with auto-fix
ruff check --fix
ruff format

# Check only
ruff check

# Docstring coverage (min 80% required)
interrogate app -c pyproject.toml
```

## Code Style Guidelines

**General:**

- Python 3.13+ target
- Line length: 88 characters
- Double quotes for strings
- Google-style docstrings mandatory
- Type hints required

**Imports:**

```python
# Standard library
from collections.abc import Sequence
from typing import Any, Generic

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# Local
from app.database.session import get_db_session
from app.models.servers import Servers
```

**Naming Conventions:**

- Files: `snake_case.py` (e.g., `route_servers.py`, `server_repo.py`)
- Classes: `PascalCase` (e.g., `BaseRepository`, `ServerService`)
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Type Hints:**

- Use `|` for unions: `ModelType | None`
- Use `type[]` not `Type[]`
- Return types required except `self`, `cls`
- `Any` allowed (ANN401 ignored)

**Error Handling:**

- Use custom exceptions from `app.core.exceptions`
- `AppNotFoundError`, `AppValidationError`, etc.
- Wrap external calls with `BaseHTTPClient`

**Layer Patterns:**

Repository (`app/repos/`):

```python
class ServerRepository(BaseRepository[Servers]):
    def __init__(self):
        super().__init__(Servers)
```

Service (`app/services/`):

```python
class ServerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ServerRepository()
```

Routes (`app/api/`):

```python
@router.post("/", response_model=ServerResponse)
async def create_server(
    payload: ServerCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Servers:
    service = ServerService(session)
    return await service.create_server(payload)
```

**Logging:**

```python
from app.core.log_config import get_logger
logger = get_logger(__name__)
logger.info("message", extra={"key": "value"})
```

**Ruff Ignored Rules:**

- E501: Line length (handled by formatter)
- D107: `__init__` docstrings
- ANN201/202: Return types for `cls`/`self`
- ANN401: `Any` type allowed
- TRY003: Long exception messages OK

**Test Exclusions:**

- Tests don't require docstrings (D ignored)
- Tests don't require type hints (ANN ignored)
- Assertions allowed (S101 ignored)

**Configuration:**

- Settings via env vars with `__` separator (e.g., `DB__DB_URL`)
- Default DB: `sqlite+aiosqlite:///./application.db`

## Project Structure

```
backend/
  app/
    api/           # Route handlers
    services/      # Business logic
    repos/         # Data access
    models/        # SQLAlchemy models
    core/          # Settings, clients, exceptions, logging
    database/      # Session management
  tests/           # Mirror app structure
```
