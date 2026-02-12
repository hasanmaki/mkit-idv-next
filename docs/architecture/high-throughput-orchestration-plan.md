# High Throughput Orchestration Plan

Dokumen plan sebelum implementasi orchestration transaksi skala tinggi.

## 1) Objective

- Menjalankan transaksi kontinu dengan aman dan cepat pada banyak binding/server.
- Menjamin kontrol `start/pause/resume/stop` konsisten.
- Menjaga audit trail transaksi/snapshot tetap utuh.

## 2) Target Topology

Komponen runtime:

1. `API Service` (FastAPI, multi-worker)
- fokus: endpoint UI/API, CRUD, control command

2. `Orchestrator Service` (dedicated process, 1 replica awal)
- fokus: worker loop transaksi per binding

3. `Redis`
- shared runtime state + distributed lock + command channel

4. `Database`
- source of truth transaksi/snapshot/domain data

## 3) Core Rules

1. 1 binding = maksimal 1 worker aktif.
2. Hard stop bersifat cooperative:
- tidak memotong HTTP call aktif
- dieksekusi di loop boundary sebelum iterasi berikutnya
3. Stop condition wajib:
- manual stop
- `insufficient_balance_before_start`

## 4) WorkerRegistry Contract (Abstraction)

Interface minimal:

- `start(binding_id, config) -> bool`
- `pause(binding_id) -> bool`
- `resume(binding_id) -> bool`
- `stop(binding_id, reason) -> bool`
- `get_state(binding_id) -> WorkerState`
- `acquire_lock(binding_id, owner, ttl) -> bool`
- `refresh_lock(binding_id, owner, ttl) -> bool`
- `release_lock(binding_id, owner) -> bool`
- `heartbeat(binding_id, payload) -> None`

Implementasi:

- `RedisWorkerRegistry` (single source of runtime truth)

## 5) Redis Key Design (Draft)

- `wrk:state:{binding_id}` -> hash (`state`, `reason`, `updated_at`)
- `wrk:cfg:{binding_id}` -> hash (`interval_ms`, `max_retry_status`, dst)
- `wrk:lock:{binding_id}` -> string owner (SET NX EX)
- `wrk:hb:{binding_id}` -> heartbeat timestamp
- `wrk:cmd` -> stream/list command queue (optional)

## 6) Concurrency Plan (Initial Defaults)

Global:

- `max_concurrent_calls = 50`

Per-server:

- `max_concurrent_per_server = 2`

Loop:

- `interval_ms = 300-800` (configurable)
- `status_retry = 2-3` (short retry)
- `cooldown_on_error_ms = 1000-3000`

Catatan:

- angka ini baseline awal, tuning dari metric runtime.

## 7) Transaction Loop (Per Binding)

1. cek state + lock ownership
2. jika `paused`: sleep pendek, ulang
3. jika `stopped`: exit worker
4. jalankan 1 cycle:
- `start_transaction` (sudah ada precheck saldo)
- evaluasi status:
  - `SUKSES` -> next cycle
  - `PROCESSING` -> OTP queue / continue policy
  - `GAGAL`:
    - reason `insufficient_balance_before_start` -> set stop
    - reason lain -> cooldown lalu next cycle
5. sebelum next cycle: cek stop flag (hard-stop boundary)

## 8) OTP Handling Plan

- transaksi yang menunggu OTP masuk queue per binding.
- UI kirim OTP via endpoint existing.
- worker membaca hasil OTP dan lanjut flow.
- timeout OTP -> mark gagal, lanjut/stop sesuai policy.

## 9) Observability Minimum

Metric:

- success/fail rate per binding/server
- in-flight calls global + per server
- average latency per endpoint provider
- stop reason distribution

Log field wajib:

- `binding_id`, `server_id`, `account_id`, `trx_id`, `cycle`, `action`, `result`

## 10) Rollout Phases

Phase A:

- finalize `WorkerRegistry` interface
- implement `RedisWorkerRegistry`
- implement orchestrator runner (single process)

Phase B:

- active deployment API `workers=4+` + orchestrator dedicated
- tuning lock/heartbeat TTL and failure recovery

Phase C:

- tuning concurrency and retry
- add dashboard + alert basic

## 11) Acceptance Criteria

1. Tidak ada double worker pada binding yang sama.
2. `stop` tidak memutus call aktif, tapi mencegah iterasi berikutnya.
3. Transaksi tetap tercatat audit-complete (header + snapshot).
4. Pada saldo kurang, worker berhenti konsisten dengan reason terstandar.
5. API multi-worker tidak menyebabkan state drift orchestration.
