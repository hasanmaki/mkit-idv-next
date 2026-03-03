## Qwen Added Memories
- Project: mkit-idv-next - Voucher Management System with IDV Integration. Architecture: Frontend (React+Vite+TypeScript+Tailwind+shadcn/ui) + Backend (FastAPI+SQLAlchemy Async+SQLite/PostgreSQL). Key features: Account management, Server management, Binding management, Transaction orchestration for IDV voucher purchases, OTP verification flows, Balance checking. Backend port: 9914, Frontend dev port: 5173. Uses Redis for orchestration runtime. Database migrations via Alembic. Main entities: Accounts, Servers, Bindings, Transactions, TransactionSnapshots, TransactionStatuses. Transaction flow: start → OTP (first device) → balance check → purchase → status check. Has pause/resume transaction functionality. Services layer follows repository pattern. Frontend organized by features (accounts, bindings, servers, transactions, orchestration).

## Recent Refactoring (2026-03-03)

### 1. Orders-Accounts Relationship
- **Orders**: Can create accounts via `msisdns` field (comma/newline separated)
- **Accounts**: Must belong to an order (order_id required, FK with CASCADE delete)
- **Bulk Account Creation**: `POST /v1/accounts/bulk` for adding multiple accounts to existing order
- **Frontend**: AddAccountsDialog uses bulk endpoint, single API call instead of parallel calls

### 2. Account Model Simplification
**Removed fields:**
- `status` (Enum: NEW, ACTIVE, EXHAUSTED, DISABLED)
- `is_reseller` (bool)
- `last_device_id` (str)

**Added fields:**
- `is_active` (bool) - Simple active flag
- `card_active_until` (str) - From balance check response
- `grace_period_until` (str) - From balance check response
- `expires_info` (str) - From balance check response
- `last_balance_response` (JSON) - Raw balance check response for debugging

**Balance Response Example:**
```json
{
  "req": {"username": "085715603254"},
  "res": {
    "cardactiveuntil": "02 Mar 2027",
    "balance": "5604",
    "graceperioduntil": "01 May 2027",
    "expires": "Berlaku hingga 02 Mar 27"
  }
}
```

### 3. UI Tab Order
Servers → Orders → Accounts → Bindings → Orchestration → Transactions

### 4. Orders Page Simplification
- Removed: Edit Order dialog, Add Account inline menu, Navigate to Accounts link
- Purpose: Orders page only for creating orders + optional accounts via msisdns field
- Account management moved to Accounts tab

### 5. Accounts Page Updates
- Table columns: ID, Order, MSISDN, Email, Balance, Active, Actions
- Removed: Status, Reseller columns
- Filter: MSISDN, Email, Active Status (All/Yes/No)
- Forms: Order dropdown selector (loads from /v1/orders)

### 6. Database Migration
- Migration file: `alembic/versions/abbbf70fc779_simplify_accounts_model.py`
- Applied successfully with `alembic upgrade head`

### Key Files Modified
- Backend: `models/accounts.py`, `api/schemas/accounts.py`, `services/accounts/service.py`
- Frontend: `features/accounts/**` (types, components, hooks, pages)
- Migration: Added/removed columns with proper indexes
