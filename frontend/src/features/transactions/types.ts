export type TransactionStatus =
  | "PROCESSING"
  | "PAUSED"
  | "RESUMED"
  | "SUKSES"
  | "SUSPECT"
  | "GAGAL";

export type TransactionOtpStatus = "PENDING" | "SUCCESS" | "FAILED";

export type Transaction = {
  id: number;
  trx_id: string;
  t_id: string | null;
  server_id: number;
  account_id: number;
  binding_id: number;
  batch_id: string;
  device_id: string | null;
  product_id: string | null;
  email: string | null;
  limit_harga: number | null;
  amount: number | null;
  voucher_code: string | null;
  status: TransactionStatus;
  is_success: number | null;
  error_message: string | null;
  otp_required: boolean;
  otp_status: TransactionOtpStatus | null;
  created_at: string;
  updated_at: string;
};

export type TransactionStartPayload = {
  binding_id: number;
  product_id: string;
  email: string;
  limit_harga: number;
  otp_required: boolean;
};

export const TRANSACTION_STATUSES: TransactionStatus[] = [
  "PROCESSING",
  "PAUSED",
  "RESUMED",
  "SUKSES",
  "SUSPECT",
  "GAGAL",
];

export type TransactionFilters = {
  status_filter: TransactionStatus | "";
  binding_id: string;
  account_id: string;
  server_id: string;
  batch_id: string;
};

export const defaultTransactionFilters: TransactionFilters = {
  status_filter: "",
  binding_id: "",
  account_id: "",
  server_id: "",
  batch_id: "",
};
