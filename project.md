# list perintah untuk servers

- Request OTP: <http://localhost:9914/otp?username=085777076575&pin=xxxxxxx>
- VerifyOTP: <http://localhost:9914/verifyOtp?username=085777076575&otp=xxxxxx>
- Logout: <http://localhost:9914/logout?username=085777076575>
- Balance Pulsa: <http://localhost:9914/balance_pulsa?username=085777076575>
- Get Token: <http://localhost:9914/token_location3?username=085777076575>
- List Produk: <http://localhost:9914/list_idv?username=085777076575>
- Trx Voucher IDV: <http://localhost:9914/trx_idv?username=085777076575&product_id=xxx&email=xxx@xxx.com&limit_harga=xxxxx> (product_id=xxxxx lhat di list produk)
- Otp Trx: <http://localhost:9914/otp_idv?username=085777076575&otp=xxxxx> (Hanya sekali saat login pada device baru)
- Status Trx IDV: <http://localhost:9914/status_idv?username=085777076575&trx_id=xxxxx> (trx_id=xxxxx> lihat di respon trx)

## flow login

1. request otp
2. verify otp ( ada token_login)
3. get balance pulsa
4. get token_location3
5. cek reseller by get list produk

## flow pembelian idv

### transaksi pertama

1. get trx voucher idv > return trx_id
2. otp trx idv > hanya sekali pada device baru
3. cek status trx idv dengan trx_id

### transaksi selanjutnya

1, get trx voucher idv > return trx_id
2. cek status trx idv dengan trx_id
