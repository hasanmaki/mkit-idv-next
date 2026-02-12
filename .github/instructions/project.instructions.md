---
description: Project rules and current architecture for mkit-idv-next
---

# Project Context

Sistem ini mengelola resource server (umumnya `http://10.0.0.3:port`) untuk proses:

1. bind account (MSISDN) ke server
2. login + verify + reseller check
3. transaksi voucher

Model utama:

- `servers`: resource endpoint
- `accounts`: daftar MSISDN per `batch_id`
- `bindings`: sesi kerja account+server
- `transactions`: lifecycle transaksi

# Binding Lifecycle

State `bindings.step`:

`bound -> otp_requested -> otp_verification -> otp_verified -> token_login_fetched -> logged_out`

## Guard Matrix (Binding)

- `request_login`: allowed `bound`, `otp_requested`
- `verify_login`: allowed `otp_requested`
- `refresh_token_location`: allowed `otp_verified`, `token_login_fetched`
- `verify_reseller`: allowed `otp_verified`, `token_login_fetched`
- `check_balance`: allowed semua step aktif (kecuali `logged_out`)
- `logout`: allowed semua step aktif (kecuali `logged_out`)

Guard diimplementasikan di `WorkflowGuardService`.

# Transaction Lifecycle

Status `transactions.status`:

- `PROCESSING`
- `PAUSED`
- `RESUMED`
- `SUKSES`
- `SUSPECT`
- `GAGAL`

## Guard Matrix (Transaction)

- `start_transaction`: binding step harus `token_login_fetched`
- `submit_otp`: allowed `PROCESSING`, `RESUMED`
- `pause`: allowed `PROCESSING`, `RESUMED`
- `resume`: allowed `PAUSED`
- `continue`: allowed `PROCESSING`, `RESUMED`
- `check_balance_and_continue_or_stop`: allowed `PROCESSING`, `RESUMED`, `PAUSED`
- `stop`: allowed `PROCESSING`, `RESUMED`, `PAUSED`, `SUSPECT`

# Device ID Rule (Updated)

`device_id` **bukan input manual server**.

Source of truth:

- diambil dari response provider (`list_idv -> data.identifier.device_id`)
- disimpan ke `bindings.device_id` (saat verify flow)
- sinkron ke `accounts.last_device_id`

# Token Location Rule

Binding menyimpan:

- `token_location`
- `token_location_refreshed_at`

UI menampilkan badge `token_loc`:

- `Fresh` / `Stale` / `Empty`

# Implemented Binding Actions

Inline actions:

- request login (PIN optional, fallback ke `account.pin`)
- verify login (OTP)
- check balance
- refresh token location
- verify reseller
- logout
- delete

Bulk actions:

- bulk check balance
- bulk refresh token_loc
- bulk request login
- bulk verify reseller
- bulk logout
- bulk delete

OTP handling:

- gunakan `OTP Queue` (isi OTP per row untuk selected bindings dengan step `otp_requested`)

# Bulk Binding Input Modes

Supported:

1. `server_id,account_id`
2. `port,msisdn[,batch_id]`

API:

- `POST /v1/bindings/bulk/dry-run`
- `POST /v1/bindings/bulk`

Result per item: `would_create|created|failed` + reason.

# Endpoint Summary (Bindings)

- `POST /v1/bindings`
- `GET /v1/bindings`
- `GET /v1/bindings/view`
- `POST /v1/bindings/{id}/request-login`
- `POST /v1/bindings/{id}/verify-login`
- `POST /v1/bindings/{id}/check-balance`
- `POST /v1/bindings/{id}/refresh-token-location`
- `POST /v1/bindings/{id}/verify-reseller`
- `POST /v1/bindings/{id}/logout`
- `DELETE /v1/bindings/{id}`

