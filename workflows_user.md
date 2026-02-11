Based on this comprehensive understanding of the codebase, design a UI plan for the mkit-idv dashboard.

## FULL WORKFLOW UNDERSTANDING

### Binding Lifecycle

1. Create binding (link account to server) → step: BOUND
2. verify_login_and_reseller() orchestrates EVERYTHING:
   - request_otp(msisdn, pin) → step: OTP_REQUESTED
   - verify_otp(msisdn, otp_code) → step: OTP_VERIFIED
   - get_token_location3() → step: TOKEN_LOGIN_FETCHED
   - get_balance_pulsa() → fetch balance
   - list_produk() → check reseller status
3. After verified, binding is ready for transactions
4. logout_binding() → step: LOGGED_OUT, account status: EXHAUSTED

### Transaction Lifecycle

1. start_transaction(binding_id, product_id, email, limit_harga) → creates transaction
   - Fetches balance_start
   - Calls trx_voucher_idv() → gets trx_id
   - Checks status_trx() immediately
   - If is_success==2 + voucher → SUKSES
   - If is_success==2 + no voucher → SUSPECT
   - Else → PROCESSING (may need OTP)
2. If otp_required (different device): submit_otp() → check status again
3. continue_transaction() → re-polls status
4. pause_transaction() → PAUSED
5. resume_transaction() → RESUMED (with balance check)
6. stop_transaction() → GAGAL
7. check_balance_and_continue_or_stop() → auto-decides

### Binding Steps enum

BOUND, OTP_REQUESTED, OTP_VERIFICATION, OTP_VERIFIED, TOKEN_LOGIN_FETCHED, LOGGED_OUT

### Transaction Statuses

PROCESSING, PAUSED, RESUMED, SUKSES, GAGAL, SUSPECT

### OTP Statuses: PENDING, SUCCESS, FAILED

## USER'S REQUIREMENTS

1. **Servers** - CRUD, rarely used
2. **Accounts** - Add/bulk import, occasionally used
3. **Bindings** - MOST FREQUENTLY USED. This is the main operational panel:
   - Create binding, verify login (OTP flow), start/stop/pause/resume transactions
   - The binding table should have INLINE control buttons
   - User switches between accounts/bindings frequently
4. **Transactions** - Static log table that grows as transactions occur

## USER'S UI VISION

- 3 main tabs (not sidebar): `| Servers | Accounts | Bindings & Transactions |`
- Bindings table at top with INLINE controls for the whole workflow
- Transactions table below as a growing log
- Fast interactions, minimal modal usage
- The binding row is the "command center" - from here you:
  - Verify login (OTP flow)
  - Start transactions
  - Control running transactions (pause/stop/resume)
  - Check balance
  - Logout when done

## DESIGN THE PLAN

Consider:

1. Tab-based layout (not sidebar) - 3 tabs at the top
2. Servers tab: Simple CRUD table
3. Accounts tab: Table with add/bulk import
4. Bindings & Transactions tab (the MAIN operational view):
   - Top: Bindings table with inline controls
   - Bottom: Transactions log table
5. For the bindings inline controls, think about what makes sense:
   - When step is BOUND → show "Verify" button (needs OTP input inline or small popover)
   - When step is TOKEN_LOGIN_FETCHED (fully verified) → show "Start Trx" button
   - When a transaction is PROCESSING → show "Pause/Stop" on the binding row
   - When a transaction needs OTP → show inline OTP input on binding row
   - When transaction is PAUSED → show "Resume/Stop"
6. The transaction table just shows history with status badges

Think about how to make this feel fast and operational. The user will be using this dashboard intensively, switching between accounts, creating bindings, running transactions. Minimize clicks, maximize inline actions.

Output a detailed implementation plan covering:

- HTML structure changes
- Alpine.js state management
- Which API calls map to which UI actions
- How inline controls work on binding rows
- How transaction log updates
- CSS/styling approach
