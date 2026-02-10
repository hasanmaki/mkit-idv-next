---
description: Describe when these instructions should be loaded
# applyTo: 'Describe when these instructions should be loaded' # when provided, instructions will automatically be added to the request context when the pattern matches an attached file
---

**Betul sekali, Maki!** 😅
Saya yang kurang tepat dalam framing-nya. Mari kita **perbaiki POV-nya** agar **100% sesuai realitasmu**:

---

# 📋 **Project Summary: MSISDN Binding & Voucher Exchange System**

## 🎯 **Apa Ini?**

Sistem internal untuk **mengelola 20 resource server** (bukan 20 MSISDN!).
Setiap server berjalan di port berbeda (`localhost:9900`–`localhost:9919`) dan **dapat dipasangkan dengan MSISDN apa pun**.

> 🔹 **Ada 20 resource tetap** (server/port)
> 🔹 **MSISDN bersifat sementara & habis pakai** → diganti setelah pulsanya habis
> 🔹 **Hanya 1 operator** (kamu) yang mengelola semua resource ini

---

## 🔄 **Alur Kerja Utama**

### **Siklus Hidup MSISDN di Satu Server**

1. **Pasang MSISDN baru** (account) ke server kosong/tersedia
2. **Jalankan proses login**:
   - Request OTP → Verifikasi OTP → Ambil token login → Cek saldo → Ambil token lokasi
3. **Verifikasi reseller**:
   - Cek daftar produk → jika tidak ada, MSISDN ini non-reseller
4. **Eksekusi transaksi**:
   - Transaksi pertama: butuh OTP khusus (tergantung device_id)
   - Transaksi berikutnya: otomatis sampai pulsa habis
5. **Logout & ganti MSISDN**:
   - Setelah pulsa habis, **logout** binding lama
   - **Pasang MSISDN baru** di server yang sama
   - Ulangi proses dari langkah 1

> 💡 **Server = aset tetap**
> 💡 **MSISDN = konsumsi habis pakai**

---

## 🏗️ **Arsitektur Sistem**

### **Resource Management**

- **20 server** → resource pool tetap yang kamu kelola
- **MSISDN tak terbatas** → kamu bisa ganti-ganti sesuai kebutuhan
- **Binding** = pemasangan sementara MSISDN ke salah satu server

### **Database Schema**

- **`servers`**: Daftar 20 resource server (port, konfigurasi, status)
- **`accounts`**: Daftar MSISDN + email, dikelompokkan per `batch_id` + status + reseller flag
- **`bindings`**: Sesi pemakaian account pada server (riwayat per sesi) + token login/location
- **`transactions`**: Riwayat transaksi per binding (audit lengkap)

### **State Management**

Setiap **binding** memiliki lifecycle:

```
BOUND
→ OTP_REQUESTED
→ OTP_VERIFICATION
→ OTP_VERIFIED
→ TOKEN_LOGIN_FETCHED
→ LOGGED_OUT
```

Ketika MSISDN diganti, binding lama di-`LOGGED_OUT`, binding baru dibuat di `BOUND`.

Token flow saat login:

```
OTP → token_login (verifyOtp) → balance_start → token_location
```

---

## ⚙️ **Proses Eksekusi**

### **Operasional Harian**

1. Pilih **server yang tersedia** (dari 20 resource)
2. **Pasang MSISDN baru** ke server tersebut
3. Jalankan **siklus lengkap**: login → verifikasi → transaksi massal
4. Saat pulsa habis, **logout** lalu **ganti MSISDN** di server yang sama
5. Ulangi proses untuk **semua 20 server secara paralel**

> ✅ **20 server bisa jalan bersamaan**
> ✅ **Setiap server mengelola MSISDN-nya sendiri**
> ✅ **Tidak ada batasan jumlah MSISDN** — hanya dibatasi oleh pulsa yang tersedia

---

## 🎯 **POV yang Benar**

- **Kamu memiliki 20 "mesin"** (server/port)
- **Setiap mesin bisa dipasang "kartu SIM"** (MSISDN)
- **Kartu SIM dipakai sampai habis, lalu diganti dengan yang baru**
- **Mesin tetap ada, kartu SIM yang berganti**

---

## ✅ **Catatan Model**

- `accounts` memakai **`batch_id`** untuk grouping input (misal 1000 nomor per batch).
- Rekap saldo per batch dihitung **on-demand** dari `bindings` dan `transactions`.
- `transactions` wajib menyimpan `msisdn/account`, `trx_id`, `pulsa_awal`, `pulsa_akhir`, dan detail transaksi lain.
- `servers.device_id` disimpan untuk kebutuhan OTP transaksi (belum diaktifkan logikanya).
- `bindings` menyimpan `token_login` dan `token_location` untuk debug.
