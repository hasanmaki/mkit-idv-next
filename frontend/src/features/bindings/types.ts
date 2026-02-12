export type BindingStep =
  | "bound"
  | "otp_requested"
  | "otp_verification"
  | "otp_verified"
  | "token_login_fetched"
  | "logged_out";

export type AccountStatus = "new" | "active" | "exhausted" | "disabled";

export type Binding = {
  id: number;
  server_id: number;
  account_id: number;
  batch_id: string;
  step: BindingStep;
  is_reseller: boolean;
  balance_start: number | null;
  balance_last: number | null;
  last_error_code: string | null;
  last_error_message: string | null;
  token_login: string | null;
  token_location: string | null;
  token_location_refreshed_at: string | null;
  device_id: string | null;
  bound_at: string;
  unbound_at: string | null;
  created_at: string;
  updated_at: string;
  server_base_url?: string | null;
  server_port?: number | null;
  server_is_active?: boolean | null;
  server_device_id?: string | null;
  account_msisdn?: string | null;
  account_email?: string | null;
  account_status?: "new" | "active" | "exhausted" | "disabled" | null;
  account_batch_id?: string | null;
};

export type ServerOption = {
  id: number;
  base_url: string;
  is_active: boolean;
  device_id: string | null;
};

export type AccountOption = {
  id: number;
  msisdn: string;
  batch_id: string;
  status: "new" | "active" | "exhausted" | "disabled";
  email: string;
};

export type BindingCreatePayload = {
  server_id: number;
  account_id: number;
  balance_start?: number | null;
};

export type BindingVerifyPayload = {
  otp: string;
};

export type BindingRequestLoginPayload = {
  pin?: string | null;
};

export type BindingBulkItemInput = {
  server_id?: number;
  account_id?: number;
  port?: number;
  msisdn?: string;
  batch_id?: string;
  balance_start?: number | null;
};

export type BindingBulkPayload = {
  items: BindingBulkItemInput[];
  stop_on_first_error: boolean;
};

export type BindingBulkItemResult = {
  index: number;
  status: "created" | "would_create" | "failed";
  reason: string | null;
  server_id: number | null;
  account_id: number | null;
  port: number | null;
  msisdn: string | null;
  batch_id: string | null;
  binding: Binding | null;
};

export type BindingBulkResult = {
  dry_run: boolean;
  total_requested: number;
  total_created: number;
  total_failed: number;
  items: BindingBulkItemResult[];
};

export type BindingLogoutPayload = {
  account_status?: AccountStatus | null;
  last_error_code?: string | null;
  last_error_message?: string | null;
};

export const BINDING_STEPS: BindingStep[] = [
  "bound",
  "otp_requested",
  "otp_verification",
  "otp_verified",
  "token_login_fetched",
  "logged_out",
];

export type BindingFilters = {
  server_id: string;
  account_id: string;
  batch_id: string;
  step: BindingStep | "";
  active_only: boolean;
};

export const defaultBindingFilters: BindingFilters = {
  server_id: "",
  account_id: "",
  batch_id: "",
  step: "",
  active_only: true,
};
