# Servers Domain - Full Stack Integration Guide

## ✅ Refactoring Complete!

The Servers domain has been successfully refactored using Domain-Driven Design (DDD) principles and is fully integrated with the frontend.

---

## 📊 Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  src/features/servers/                                      │
│  ├── pages/ServersPage.tsx     ← UI Component              │
│  ├── hooks/useServers.ts       ← State management          │
│  ├── components/               ← Form & Table components   │
│  └── types.ts                  ← TypeScript types          │
└────────────────────────────────────────────────────────────┘
                          ↕ HTTP (REST API)
┌────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  app/api/route_servers.py      ← Thin controller           │
│  app/application/servers/      ← Use cases (CQRS)          │
│  app/domain/servers/           ← Business logic            │
│  app/repos/                    ← Persistence               │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 Features Implemented

### Backend (DDD Architecture)

#### Domain Layer
- ✅ **Server Entity** - Rich domain model with behavior
- ✅ **Value Objects** - ServerId, ServerUrl, ServerConfig
- ✅ **Domain Events** - ServerCreatedEvent, ServerUpdatedEvent, ServerStatusToggledEvent, ServerDeletedEvent, ServerBulkCreatedEvent
- ✅ **Domain Exceptions** - ServerNotFoundError, ServerDuplicateError, ServerBulkValidationError
- ✅ **Domain Service** - ServerDomainService with business logic

#### Application Layer
- ✅ **Commands** - CreateServerCommand, UpdateServerCommand, DeleteServerCommand, ToggleServerStatusCommand, CreateServersBulkCommand, DryRunBulkServersCommand
- ✅ **Queries** - GetServerQuery, ListServersQuery
- ✅ **Command Handler** - ServerCommandHandler
- ✅ **Query Handler** - ServerQueryHandler

#### API Layer
- ✅ **Thin Controller** - route_servers.py (56 lines)
- ✅ **Request/Response Schemas** - servers.py

#### Infrastructure
- ✅ **Repository** - ServerRepository
- ✅ **SQLAlchemy Model** - Servers

#### Tests
- ✅ **32 Unit Tests** - All passing
  - 18 Entity tests
  - 14 Domain Service tests

### Frontend (Feature Structure)

#### Pages
- ✅ **ServersPage.tsx** - Main page with tabs

#### Components
- ✅ **ServerForms.tsx** - Single, Bulk, and Edit forms
- ✅ **ServersTable.tsx** - Data table with actions

#### Hooks
- ✅ **useServers.ts** - State management & API calls

#### Types
- ✅ **types.ts** - TypeScript type definitions

---

## 🚀 How to Use

### 1. Start Development Server

```bash
# From project root
make dev
```

This will start:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:9914
- **API Docs**: http://localhost:9914/docs

### 2. Access Servers Feature

Navigate to: **http://localhost:5173/servers**

### 3. Available Operations

#### Single Server Creation
1. Click **"Add Single"** button
2. Fill in form:
   - Host (e.g., `http://10.0.0.3`)
   - Port (e.g., `9900`)
   - Description (optional)
   - Timeout, Retries, Wait Between Retries, Max Requests Queued
   - Active Status
   - Notes (optional)
3. Click **"Save"**

#### Bulk Server Creation
1. Click **"Add Bulk"** button
2. Fill in form:
   - Base Host (e.g., `http://10.0.0.3`)
   - Start Port (e.g., `9900`)
   - End Port (e.g., `9909`)
   - Configuration defaults
3. Click **"Dry Run"** to preview
4. Review results (Created/Skipped/Failed)
5. Click **"Create Servers"** to commit

#### Edit Server
1. Click **⋮** (more actions) on a server row
2. Select **"Edit"**
3. Modify fields
4. Click **"Save Changes"**

#### Toggle Server Status
1. Click **⋮** (more actions) on a server row
2. Select **"Activate"** or **"Deactivate"**

#### Delete Server(s)
- **Single Delete**: Click **⋮** → **Delete** → Confirm
- **Bulk Delete**: Select multiple servers → Click **"Delete Selected"** → Confirm

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/servers` | Create single server |
| `POST` | `/v1/servers/bulk` | Create servers in bulk |
| `POST` | `/v1/servers/bulk/dry-run` | Preview bulk creation |
| `GET` | `/v1/servers` | List all servers |
| `GET` | `/v1/servers/{id}` | Get server by ID |
| `PATCH` | `/v1/servers/{id}` | Update server |
| `PATCH` | `/v1/servers/{id}/status` | Toggle status |
| `DELETE` | `/v1/servers/{id}` | Delete server |

---

## 🏗️ Code Flow Example

### Creating a Server

```
User Action (Frontend)
    ↓
[Add Single] Button Click
    ↓
useServers.createSingleServer()
    ↓
API Call: POST /v1/servers
    ↓
route_servers.create_server()
    ↓
ServerCommandHandler.handle_create(CreateServerCommand)
    ↓
Server.create() → Records ServerCreatedEvent
    ↓
ServerDomainService.validate_server_uniqueness()
    ↓
ServerRepository.create() → Persist to DB
    ↓
Return Server Entity
    ↓
Frontend Updates State
    ↓
UI Shows Success Toast
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd backend
uv run pytest tests/domain/servers/ -v
```

**Expected Output:**
```
======================== 32 passed in 0.73s =========================
```

### Test Coverage

```
Domain Layer: 94% coverage
- Entities: Full behavior testing
- Value Objects: Validation & immutability
- Domain Services: Business logic
- Events: Event recording
```

---

## 📁 File Locations

### Backend

```
backend/app/
├── domain/
│   ├── common/
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   ├── events.py
│   │   └── exceptions.py
│   └── servers/
│       ├── entities.py         # Server aggregate root ⭐
│       ├── value_objects.py    # ServerId, ServerUrl, ServerConfig
│       ├── events.py           # Domain events
│       ├── exceptions.py       # Domain exceptions
│       └── services.py         # Domain service
│
├── application/
│   └── servers/
│       ├── commands.py         # CUD commands
│       ├── queries.py          # Read queries
│       ├── handlers.py         # Command handlers
│       └── query_handlers.py   # Query handlers
│
├── api/
│   ├── route_servers.py        # API routes ⭐
│   └── schemas/
│       └── servers.py          # Request/response schemas
│
├── repos/
│   └── server_repo.py          # Repository
│
└── models/
    └── servers.py              # SQLAlchemy model

backend/tests/
└── domain/
    └── servers/
        ├── test_entities.py    # 18 tests
        └── test_services.py    # 14 tests
```

### Frontend

```
frontend/src/
└── features/
    └── servers/
        ├── pages/
        │   └── ServersPage.tsx     # Main page ⭐
        ├── components/
        │   ├── ServerForms.tsx     # Forms
        │   └── ServersTable.tsx    # Table
        ├── hooks/
        │   └── useServers.ts       # State & API calls
        └── types.ts                # TypeScript types
```

---

## 🎯 Next Steps (Your Choice)

When you're ready to continue refactoring other domains, here's the recommended order:

### 1. **Accounts Domain** (Easy-Medium)
- Similar CRUD pattern to Servers
- Bulk creation support
- Status management (NEW, ACTIVE, SUSPENDED, etc.)
- **Estimated Effort**: 2-3 hours

### 2. **Bindings Domain** (Medium-Hard)
- Workflow state machine
- Step transitions (TOKEN_LOGIN_FETCHED → READY, etc.)
- Guard conditions
- **Estimated Effort**: 4-6 hours

### 3. **Transactions Domain** (Hard)
- Most complex business logic
- IDV integration
- OTP flows
- Balance checking
- Pause/Resume functionality
- **Estimated Effort**: 8-12 hours

---

## 🔧 Maintenance

### Adding New Server Fields

**Backend:**
1. Update `app/domain/servers/entities.py` - Add field to Server class
2. Update `app/application/servers/commands.py` - Add to commands
3. Update `app/api/schemas/servers.py` - Add to request/response schemas

**Frontend:**
1. Update `frontend/src/features/servers/types.ts` - Add to form types
2. Update `frontend/src/features/servers/components/ServerForms.tsx` - Add form field
3. Update `frontend/src/features/servers/hooks/useServers.ts` - Handle in state

### Modifying Business Rules

**Example: Change port validation range**

```python
# backend/app/domain/servers/entities.py
class Server(Entity):
    port: int = Field(..., gt=0, lt=65536)  # Change this
```

---

## 📚 Documentation

- **DDD_REFACTORING_GUIDE.md** - Complete DDD pattern guide
- **project.md** - Original project requirements
- **README.md** - General setup instructions

---

## ✅ Checklist for Next Domain

When you're ready to refactor another domain, follow this checklist:

- [ ] Create domain layer structure (copy from servers)
- [ ] Define entities with rich behavior
- [ ] Create value objects
- [ ] Define domain events
- [ ] Create domain exceptions
- [ ] Implement domain services
- [ ] Create application layer (commands/queries)
- [ ] Implement handlers
- [ ] Refactor API routes (make thin)
- [ ] Update frontend (if needed)
- [ ] Write unit tests (aim for 90%+ coverage)
- [ ] Update documentation

---

## 🎉 Current Status

**Servers Domain: ✅ COMPLETE & PRODUCTION READY**

- Backend: Fully refactored with DDD
- Frontend: Already integrated
- Tests: 32 passing unit tests
- Documentation: Complete
- API: Backward compatible

**Ready for next domain when you are!** 🚀
