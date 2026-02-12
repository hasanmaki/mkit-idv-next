# Transaction Orchestration Architecture

Dokumen ini merangkum pendekatan auto transaksi yang akan dipakai di atas service transaksi yang saat ini masih `1 transaksi per call`.

## Current Baseline

Service yang sudah ada:

- `POST /v1/transactions/start`
- `POST /v1/transactions/{id}/otp`
- `POST /v1/transactions/{id}/continue`
- `POST /v1/transactions/{id}/pause`
- `POST /v1/transactions/{id}/resume`
- `POST /v1/transactions/{id}/stop`
- `POST /v1/transactions/{id}/check`

Karakter:

- setiap endpoint memproses 1 transaksi
- belum ada loop otomatis lintas transaksi

## Target Design

Tambahkan layer orchestration: **worker per binding**.

Komponen:

1. `Control API`
- start worker untuk sekumpulan binding
- pause/resume/stop worker

2. `Worker Runtime`
- 1 worker = 1 `binding_id`
- loop: start transaksi -> evaluasi hasil -> lanjut/menunggu/berhenti

3. `OTP Queue`
- transaksi status `PROCESSING` + butuh OTP masuk antrian
- UI submit OTP per transaksi

## Loop Rule (Ringkas)

Untuk worker `binding_id=X`:

1. cek control state (`running|paused|stopped`)
2. panggil `start_transaction`
3. evaluasi hasil:
- `SUKSES`: lanjut iterasi berikutnya
- `PROCESSING`: tunggu OTP atau lanjut `continue`
- `GAGAL`:
  - jika reason `insufficient_balance_before_start`: **stop worker**
  - reason lain: lanjut iterasi sesuai policy retry/cooldown

## Hard Stop Conditions

Worker harus berhenti saat:

1. user menekan stop
2. saldo awal sebelum beli tidak cukup (`insufficient_balance_before_start`)

## Hard Stop Execution Model

Hard stop dieksekusi dengan model **stop-at-loop-boundary**:

- stop tidak memutus HTTP request yang sedang berjalan (`trx_idv`, `status_idv`, dll)
- stop dievaluasi setelah step selesai dan saat mencapai ujung iterasi
- iterasi berikutnya tidak boleh dimulai jika stop flag aktif

Implikasi implementasi:

1. setiap iterasi harus punya checkpoint kontrol (before-next-iteration check)
2. update status/snapshot dalam iterasi aktif tetap harus dituntaskan agar konsisten
3. jangan pakai model force-cancel task di tengah call provider

## Why This Design

- memisahkan business logic transaksi dari loop runtime
- endpoint transaksi tetap sederhana dan testable
- start/pause/resume/stop jadi konsisten di UI dan backend
