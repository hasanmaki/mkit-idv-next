# Domain-Driven Design Refactoring Guide

## Overview

This document describes the DDD refactoring pattern applied to the mkit-idv-next project, using the **Servers domain** as the reference implementation.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Thin)                          │
│  route_servers.py - HTTP handlers, request/response mapping │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Application Layer (Use Cases)                   │
│  handlers.py - Command/Query handlers, orchestration        │
│  commands.py - Write operations (CUD)                        │
│  queries.py  - Read operations (R)                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Domain Layer (Business Logic)                 │
│  entities.py      - Rich domain models with behavior        │
│  value_objects.py - Immutable value types                   │
│  events.py        - Domain events                           │
│  exceptions.py    - Domain exceptions                       │
│  services.py      - Domain services                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             Infrastructure Layer (Persistence)               │
│  repos/*.py     - Repository implementations               │
│  models/*.py    - SQLAlchemy ORM models                    │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
backend/app/
├── domain/
│   ├── common/
│   │   ├── entities.py         # Base Entity class
│   │   ├── value_objects.py    # Base ValueObject class
│   │   ├── events.py           # Base DomainEvent class
│   │   └── exceptions.py       # Base DomainException class
│   └── servers/
│       ├── __init__.py
│       ├── entities.py         # Server aggregate root
│       ├── value_objects.py    # ServerId, ServerUrl, ServerConfig
│       ├── events.py           # Server domain events
│       ├── exceptions.py       # Server exceptions
│       └── services.py         # Server domain service
│
├── application/
│   └── servers/
│       ├── __init__.py
│       ├── commands.py         # CreateServerCommand, etc.
│       ├── queries.py          # GetServerQuery, etc.
│       ├── handlers.py         # ServerCommandHandler
│       └── query_handlers.py   # ServerQueryHandler
│
├── api/
│   ├── route_servers.py        # Refactored thin controller
│   └── schemas/
│       └── servers.py          # API request/response schemas
│
└── infrastructure/ (implicit)
    ├── repos/
    │   └── server_repo.py      # Repository implementation
    └── models/
        └── servers.py          # SQLAlchemy model
```

## Key Concepts

### 1. Rich Domain Model (Entity)

```python
# BEFORE: Anemic model
class Servers(Base):
    id: int
    port: int
    base_url: str
    is_active: bool
    # Just data, no behavior

# AFTER: Rich domain model with behavior
class Server(Entity):
    @classmethod
    def create(cls, port: int, base_url: str, ...) -> "Server":
        """Factory method that records ServerCreatedEvent"""
        server = cls(...)
        server._record_event(ServerCreatedEvent(...))
        return server

    def update(self, **kwargs) -> list[str]:
        """Update with validation and event recording"""
        self._record_event(ServerUpdatedEvent(...))
        return updated_fields

    def toggle_status(self, is_active: bool) -> None:
        """Business rule: records status change event"""
        self._record_event(ServerStatusToggledEvent(...))

    def validate_uniqueness(self, existing_by_port, existing_by_url) -> None:
        """Business rule: validates uniqueness constraints"""
```

### 2. Value Objects

```python
class ServerUrl(ValueObject):
    """Immutable value object with validation"""
    value: str = Field(..., min_length=10, max_length=255)

    @field_validator("value")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        if not v.startswith("http://") or ":" not in v:
            raise ValueError("Invalid URL format")
        return v

    @property
    def port(self) -> int:
        """Derived property"""
        return int(self.value.split(":")[1])
```

### 3. Domain Events

```python
class ServerCreatedEvent(DomainEvent):
    """Captures meaningful domain occurrence"""
    server_id: int
    port: int
    base_url: str

# Usage in entity
server = Server.create(...)
events = server.pop_events()  # [ServerCreatedEvent(...)]
# Can be published to event bus for side effects
```

### 4. Commands & Queries (CQRS)

```python
# Commands (write operations)
@dataclass
class CreateServerCommand:
    port: int
    base_url: str
    description: str | None = None

# Queries (read operations)
@dataclass
class GetServerQuery:
    server_id: int
```

### 5. Application Services (Handlers)

```python
class ServerCommandHandler:
    """Orchestrates between domain and infrastructure"""

    async def handle_create(self, command: CreateServerCommand) -> Server:
        # 1. Create domain entity
        server = Server.create(...)

        # 2. Validate business rules
        await self.domain_service.validate_server_uniqueness(...)

        # 3. Persist
        persisted = await self.repo.create(...)

        # 4. Process domain events
        events = server.pop_events()
        # Could dispatch to event bus here

        return persisted
```

### 6. Thin API Controllers

```python
@router.post("", response_model=ServerResponse)
async def create_server(
    payload: ServerCreateRequest,
    handler: ServerCommandHandler = Depends(_get_command_handler),
) -> ServerResponse:
    """Thin controller - just delegation"""
    command = CreateServerCommand(...)
    server = await handler.handle_create(command)
    return ServerResponse.model_validate(server)
```

## Benefits

### 1. Separation of Concerns
- **Domain**: Pure business logic, no infrastructure dependencies
- **Application**: Use case orchestration
- **API**: HTTP concerns only
- **Infrastructure**: Technical implementation details

### 2. Testability
```python
# Unit test domain logic without database
def test_server_creation():
    server = Server.create(port=9900, base_url="http://localhost:9900")
    assert server.port == 9900
    events = server.pop_events()
    assert len(events) == 1
```

### 3. Business Language (Ubiquitous Language)
```python
# Expressive domain methods
server.activate()
server.deactivate()
server.validate_uniqueness(...)
```

### 4. Immutability for Value Objects
```python
# Value objects are frozen (immutable)
url = ServerUrl(value="http://localhost:9900")
# url.value = "http://localhost:9901"  # Error!
```

### 5. Event-Driven Architecture Ready
```python
# Domain events can trigger side effects
events = server.pop_events()
for event in events:
    await event_bus.publish(event)  # Send emails, logs, etc.
```

## Testing Strategy

### Unit Tests (Domain Layer)
```python
# tests/domain/servers/test_entities.py
def test_server_create_records_event():
    server = Server.create(...)
    events = server.pop_events()
    assert isinstance(events[0], ServerCreatedEvent)
```

### Integration Tests (Application Layer)
```python
# tests/application/servers/test_handlers.py
@pytest.mark.asyncio
async def test_create_server_handler(session):
    handler = ServerCommandHandler(session)
    command = CreateServerCommand(...)
    server = await handler.handle_create(command)
    assert server.port == 9900
```

### E2E Tests (API Layer)
```python
# tests/api/test_servers.py
async def test_create_server_api(client):
    response = await client.post("/v1/servers", json={...})
    assert response.status_code == 201
    assert response.json()["port"] == 9900
```

## Migration Guide

### For Existing Domains (Accounts, Bindings, Transactions)

1. **Create domain layer structure**
   ```bash
   mkdir -p app/domain/accounts
   touch app/domain/accounts/{entities,value_objects,events,exceptions,services}.py
   ```

2. **Extract business logic from service layer**
   - Move validation rules to entities
   - Create value objects for primitives
   - Define domain events for state changes

3. **Create application layer**
   - Define commands and queries
   - Implement handlers that orchestrate domain + infrastructure

4. **Refactor API routes**
   - Make controllers thin (just delegation)
   - Use command/query handlers

5. **Add tests**
   - Unit tests for domain logic
   - Integration tests for application services
   - E2E tests for API

## Next Steps

Apply this pattern to:
1. ✅ **Servers** (completed - reference implementation)
2. ⏳ **Accounts** (next candidate)
3. ⏳ **Bindings** (complex - workflow state machine)
4. ⏳ **Transactions** (most complex - IDV integration)

## Lessons Learned

1. **Start simple**: Servers domain is a good starting point (CRUD + bulk)
2. **Don't over-engineer**: Only add complexity where business logic warrants it
3. **Keep data models**: Existing SQLAlchemy models can stay in infrastructure
4. **Frontend unchanged**: API contract remains the same
5. **Incremental migration**: Can coexist with old service layer during transition

## References

- "Domain-Driven Design Distilled" by Vaughn Vernon
- "Implementing Domain-Driven Design" by Vaughn Vernon
- https://martinfowler.com/tags/domain_driven_design.html
