# MKIT-IDV-NEXT - Project Context Memory

## 📋 Project Overview

**Name:** mkit-idv-next  
**Type:** Voucher Management System with IDV Integration  
**Architecture:** Full-stack (FastAPI + React)  
**Design Pattern:** Domain-Driven Design (DDD)  
**Status:** Active Development - Phase 1 Complete  

---

## 🎯 Business Concept

### Core Analogy: Laundry System
```
Server    = Mesin cuci (physical device)
Account   = Pakaian (MSISDN being processed)
Session   = Grup laundry (user/operator group)
Binding   = Tiket yang mengikat 1 pakaian ke 1 mesin untuk 1 grup
```

### Business Rules
1. **1 Session** → dapat memiliki **multiple Accounts** (grup punya banyak pakaian)
2. **1 Account** → hanya bisa di-bind ke **1 Server** pada 1 waktu (pakaian hanya di 1 mesin)
3. **1 Server** → dapat handle **multiple Accounts** secara sequential (mesin cuci banyak pakaian, antri)
4. **Session lain** → tidak boleh pakai Account yang sedang di-bind (pakaian orang lain tidak bisa dicampur)

---

## 🏗️ Architecture

### Tech Stack
```
Frontend: React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui
Backend:  FastAPI + SQLAlchemy (Async) + Pydantic
Database: SQLite (dev) / PostgreSQL (prod)
Cache:    Redis (orchestration runtime)
Logging:  Loguru
```

### DDD Layer Structure
```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (Thin)                      │
│  route_*.py - HTTP handlers, request/response mapping   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Application Layer (Use Cases)               │
│  handlers.py - Command/Query handlers (CQRS)            │
│  commands.py - Write operations (CUD)                    │
│  queries.py  - Read operations (R)                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                Domain Layer (Business Logic)             │
│  entities.py      - Rich domain models with behavior    │
│  value_objects.py - Immutable value types               │
│  events.py        - Domain events                       │
│  exceptions.py    - Domain exceptions                   │
│  services.py      - Domain services                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│             Infrastructure Layer (Persistence)           │
│  repos/*.py     - Repository implementations            │
│  models/*.py    - SQLAlchemy ORM models                 │
└─────────────────────────────────────────────────────────┘
```

### File Structure
```
backend/app/
├── domain/
│   ├── common/              # Base classes (Entity, ValueObject, Event)
│   ├── servers/             # Servers domain
│   ├── sessions/            # Sessions domain
│   └── bindings/            # Bindings domain
│
├── application/
│   ├── servers/
│   ├── sessions/
│   └── bindings/
│
├── api/
│   ├── route_*.py
│   └── schemas/
│
├── models/                  # SQLAlchemy models
├── repos/                   # Repository implementations
└── services/                # Legacy services (being replaced)

frontend/src/
└── features/
    ├── servers/
    ├── sessions/
    ├── bindings/
    ├── accounts/
    └── transactions/
```

---

## ✅ Completed Domains

### 1. Servers Domain ✅
**Purpose:** Manage IDV provider servers (mesin cuci)

**Key Features:**
- User-friendly `name` field (unique)
- `delay_per_hit` for rate limiting (0-10000ms)
- Single & Bulk creation
- Active/Inactive status

**Data Model:**
```python
class Servers(Base):
    id: int
    name: str (unique)              # NEW: "Server Production 1"
    port: int (unique)
    base_url: str (unique)
    delay_per_hit: int              # NEW: Rate limiting
    timeout, retries, max_requests_queued
    is_active: bool
    description, notes
```

**API Endpoints:**
- `POST /v1/servers` - Create single
- `POST /v1/servers/bulk` - Bulk create
- `POST /v1/servers/bulk/dry-run` - Preview
- `GET /v1/servers` - List
- `PATCH /v1/servers/{id}` - Update
- `DELETE /v1/servers/{id}` - Delete

**Frontend:**
- Page: `features/servers/pages/ServersPage.tsx`
- Components: ServerForms, ServersTable
- Features: Single/Bulk create, Edit, Toggle status, Delete

---

### 2. Sessions Domain ✅
**Purpose:** Manage user/operator sessions (grup laundry)

**Key Features:**
- Session as independent entity
- Can have multiple bindings
- Simple CRUD operations

**Data Model:**
```python
class Sessions(Base):
    id: int
    name: str
    email: str (unique)
    is_active: bool
    description, notes
```

**API Endpoints:**
- `POST /v1/sessions` - Create
- `GET /v1/sessions` - List
- `PATCH /v1/sessions/{id}` - Update
- `DELETE /v1/sessions/{id}` - Delete

**Frontend:**
- Page: `features/sessions/pages/SessionsPage.tsx`
- Components: SessionForms, SessionsTable

---

### 3. Bindings Domain ✅
**Purpose:** Bind accounts to servers for sessions (tiket laundry)

**Key Features:**
- `session_id` FK untuk ownership
- `account_id` unique constraint (1 account = 1 binding)
- Simplified workflow: BINDED → REQUEST_OTP → VERIFY_OTP → VERIFIED → LOGGED_OUT
- Balance tracking (manual/auto-check)
- Priority-based queue

**Data Model:**
```python
class Bindings(Base):
    id: int
    session_id: int (FK → sessions)    # Owner session
    server_id: int (FK → servers)
    account_id: int (FK → accounts, UNIQUE)
    
    step: str  # BINDED, REQUEST_OTP, VERIFY_OTP, VERIFIED, LOGGED_OUT
    device_id: str | None
    
    is_active: bool
    priority: int
    
    balance_start: int | None
    balance_source: str | None  # MANUAL or AUTO_CHECK
    
    description, notes, last_used_at
```

**Workflow State Machine:**
```
BINDED → REQUEST_OTP → VERIFY_OTP → VERIFIED → LOGGED_OUT
   ↑           ↑            ↑           ↑
   └───────────┴────────────┴───────────┘
         (can transition back)
```

**API Endpoints:**
- `POST /v1/bindings` - Bind single account
- `POST /v1/bindings/bulk` - Bulk bind
- `POST /v1/bindings/{id}/request-otp` - Request OTP
- `POST /v1/bindings/{id}/verify-otp` - Verify OTP
- `POST /v1/bindings/{id}/mark-verified` - Mark verified
- `POST /v1/bindings/{id}/release` - Release/logout
- `PATCH /v1/bindings/{id}/balance` - Set balance
- `GET /v1/bindings` - List bindings
- `GET /v1/bindings/session/{session_id}` - List by session

**Frontend:**
- Page: `features/bindings/pages/BindingsPage.tsx`
- Components: BindingForms, BindingsTable
- Features: Bind, OTP workflow, Balance tracking, Release

---

## 📊 Database Schema

```sql
-- Sessions (User/Operator Groups)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    description VARCHAR(255),
    notes VARCHAR(500),
    created_at DATETIME,
    updated_at DATETIME
);

-- Servers (Physical Devices)
CREATE TABLE servers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    port INTEGER UNIQUE NOT NULL,
    base_url VARCHAR(255) UNIQUE NOT NULL,
    delay_per_hit INTEGER DEFAULT 0,
    timeout INTEGER DEFAULT 10,
    retries INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    description VARCHAR(255),
    notes VARCHAR(500),
    created_at DATETIME,
    updated_at DATETIME
);

-- Bindings (Tickets)
CREATE TABLE bindings (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    server_id INTEGER REFERENCES servers(id) ON DELETE RESTRICT,
    account_id INTEGER REFERENCES accounts(id) ON DELETE RESTRICT UNIQUE,
    step VARCHAR(50) DEFAULT 'BINDED',
    device_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    balance_start INTEGER,
    balance_source VARCHAR(20),
    description VARCHAR(255),
    notes VARCHAR(500),
    last_used_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    UNIQUE(account_id)
);

-- Accounts (MSISDN)
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    msisdn VARCHAR(20),
    email VARCHAR(255),
    batch_id VARCHAR(50),
    status VARCHAR(50),
    is_reseller BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME,
    UNIQUE(msisdn, batch_id)
);
```

---

## 🔧 Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (optional, for Redis)

### Installation
```bash
# Backend
cd backend
uv sync
uv run fastapi dev app/main.py --port 9914

# Frontend
cd frontend
npm install
npm run dev
```

### One Command
```bash
make dev  # Runs both backend + frontend
```

### Ports
- Frontend: http://localhost:5173
- Backend API: http://localhost:9914
- API Docs: http://localhost:9914/docs
- Redis: 6379 (if using Docker)

---

## 📝 API Conventions

### Response Format
```typescript
// Success
{
  id: number,
  // ... fields
  created_at: string,
  updated_at: string
}

// Error
{
  error_code: string,
  message: string,
  context?: object
}
```

### Status Codes
- `200` - Success (GET, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)
- `400` - Bad Request (Validation error)
- `404` - Not Found
- `500` - Internal Server Error

---

## 🎯 Design Patterns

### 1. Rich Domain Model
```python
# BEFORE (Anemic)
class Binding(Base):
    id: int
    step: str
    # Just data

# AFTER (Rich)
class Binding(Entity):
    def request_otp(self, device_id: str) -> None:
        """Business rule: can only request OTP from BINDED state"""
        self._ensure_can_transition_to("REQUEST_OTP")
        self.step = "REQUEST_OTP"
        self.device_id = device_id
        self._record_event(OTPRequestedEvent(...))
```

### 2. Value Objects
```python
class ServerUrl(ValueObject):
    value: str  # Immutable, validated
    
    @property
    def port(self) -> int:
        return int(self.value.split(":")[1])
```

### 3. Domain Events
```python
class BindingCreatedEvent(DomainEvent):
    binding_id: int
    session_id: int
    server_id: int
    account_id: int
```

### 4. CQRS (Command Query Responsibility Segregation)
```python
# Commands (Write)
@dataclass
class BindAccountCommand:
    session_id: int
    server_id: int
    account_id: int

# Queries (Read)
@dataclass
class GetBindingQuery:
    binding_id: int
```

### 5. Repository Pattern
```python
class BindingRepository(BaseRepository[Bindings]):
    async def get_by_account(self, account_id: int) -> Bindings | None
    async def get_by_session(self, session_id: int) -> list[Bindings]
```

---

## 🧪 Testing Strategy

### Unit Tests (Domain Layer)
```bash
uv run pytest tests/domain/servers/ -v
uv run pytest tests/domain/bindings/ -v
```

### Integration Tests (Application Layer)
```bash
uv run pytest tests/application/ -v
```

### E2E Tests (API Layer)
```bash
uv run pytest tests/api/ -v
```

---

## 📚 Documentation

### Created Documents
1. `DDD_REFACTORING_GUIDE.md` - Complete DDD pattern guide
2. `Servers_DOMAIN_COMPLETE.md` - Servers implementation guide
3. `SESSIONS_DOMAIN_COMPLETE.md` - Sessions implementation guide
4. `BINDINGS_DOMAIN_COMPLETE.md` - Bindings implementation guide (TODO)

### Code Comments
- Google-style docstrings
- Type hints everywhere
- Business rules explained in docstrings

---

## 🚧 Work in Progress / TODO

### Pending Domains
1. **Accounts Domain** - Medium complexity
   - CRUD + bulk operations
   - Status management
   
2. **Transactions Domain** - High complexity
   - IDV integration
   - RGU mode (future)
   - Complex workflow

### Future Enhancements
1. **Event Bus** - For domain event publishing
2. **CQRS Separation** - Separate read/write models
3. **Saga Pattern** - For distributed transactions
4. **Multi-tenancy** - Support multiple organizations

---

## 🐛 Known Issues & Technical Debt

1. **Legacy Services** - Old service layer still exists (being phased out)
2. **Mixed Patterns** - Some routes still use old pattern
3. **Test Coverage** - Domain tests need expansion
4. **Documentation** - API docs need update

---

## 📊 Progress Tracker

| Domain | Database | Domain Layer | App Layer | API | Frontend | Tests | Status |
|--------|----------|--------------|-----------|-----|----------|-------|--------|
| Servers | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| Sessions | ✅ | ✅ | ✅ | ✅ | ✅ | ⏳ | 90% |
| Bindings | ✅ | ✅ | ✅ | ✅ | ✅ | ⏳ | 90% |
| Accounts | ✅ | ⏳ | ⏳ | ✅ | ✅ | ⏳ | 40% |
| Transactions | ✅ | ⏳ | ⏳ | ✅ | ✅ | ⏳ | 30% |

---

## 🔑 Key Decisions & Rationale

### Why DDD?
- Complex business logic (workflow states, OTP, balance tracking)
- Need for clear separation of concerns
- Easier to test and maintain
- Better alignment with business domain

### Why Session → Binding → Server?
- Clear ownership model
- Resource isolation (account can't be shared)
- Flexible allocation (session can use multiple servers)
- Easy audit trail

### Why Simplified Workflow?
- Original workflow too complex (TOKEN_LOGIN, TOKEN_LOCATION, etc.)
- Separation of concerns: Bindings for auth, Transactions for business
- Easier to understand and maintain

---

## 📞 Contact & Team

**Developer:** [Your Name]  
**Project Start:** 2026-03-02  
**Current Phase:** Phase 1 - Core Domains Complete  

---

## 🎉 Milestones Achieved

### Phase 1: Core Infrastructure ✅
- [x] DDD structure established
- [x] Servers domain complete
- [x] Sessions domain complete
- [x] Bindings domain complete
- [x] Frontend integration
- [x] Database migrations

### Phase 2: Advanced Features ⏳
- [ ] Accounts domain refactor
- [ ] Transactions domain refactor
- [ ] IDV integration
- [ ] RGU mode support

### Phase 3: Production Ready ⏳
- [ ] Comprehensive test coverage
- [ ] Performance optimization
- [ ] Documentation complete
- [ ] Security audit

---

**Last Updated:** 2026-03-02  
**Memory Version:** 1.0  
**Next Review:** After Phase 2 completion
