# Worker Runtime Storage: In-Memory vs Redis

Dokumen ini untuk keputusan penyimpanan state worker orchestration transaksi.

## Scope

Target operasi awal: `10-30` server dengan concurrency moderat.

State yang perlu disimpan:

- worker per `binding_id` (`running|paused|stopped`)
- config loop (`interval`, retry, cooldown)
- heartbeat / last activity
- OTP queue pointer (opsional)

## Option A: In-Memory Registry

Contoh: dictionary di process FastAPI.

Kelebihan:

- implementasi cepat
- dependency minim
- cocok untuk single-instance development

Kekurangan:

- hilang saat restart container/app
- tidak bisa share state antar instance
- rawan race condition saat scale-out

Rekomendasi:

- **aman untuk fase awal** jika deployment masih 1 instance.

## Option B: Redis Registry

Contoh struktur:

- `worker:{binding_id}` -> hash state
- `worker:control` -> command queue/pubsub

Kelebihan:

- state survive restart app (selama Redis up)
- mudah scale ke multi-instance
- cocok untuk distributed lock dan command broadcast

Kekurangan:

- butuh infra tambahan
- complexity lebih tinggi dibanding in-memory

Rekomendasi:

- gunakan saat masuk fase production/stabilitas tinggi.

## Practical Decision

Keputusan project ini: **langsung Redis sebagai default runtime store**.

Alasan:

1. API akan dijalankan dengan multi-worker (`workers=4+`)
2. throughput target tinggi dan butuh state konsisten lintas process
3. control `start/pause/resume/stop` harus reliable di semua instance

Implementasi tetap menjaga `WorkerRegistry` sebagai abstraction supaya backend tetap mudah diuji dan mudah diubah.
