export type Binding = {
  id: number;
  order_id: number;
  server_id: number;
  account_id: number;
  step: "BINDED" | "REQUEST_OTP" | "VERIFY_OTP" | "VERIFIED" | "CHECK_BALANCE" | "COMPLETED" | "LOGGED_OUT";
  is_reseller: boolean;
  token_location: string | null;
  device_id: string | null;
  is_active: boolean;
  priority: number;
  balance_start: number | null;
  balance_source: "MANUAL" | "AUTO_CHECK" | null;
  description: string | null;
  notes: string | null;
  last_used_at: string | null;
  created_at: string;
  updated_at: string;
};

export type BindAccountPayload = {
  order_id: number;
  server_id: number;
  account_id: number;
  is_reseller?: boolean;
  priority?: number;
  description?: string | null;
  notes?: string | null;
};

export type BulkBindPayload = {
  order_id: number;
  server_id: number;
  account_ids: number[];
  is_reseller?: boolean;
  priority?: number;
  description?: string | null;
  notes?: string | null;
};

export type RequestOTPPayload = {
  pin: string;
};

export type VerifyOTPPayload = {
  otp: string;
};

export type WorkflowStepPayload = {
  step: string;
  token_location?: string | null;
  notes?: string | null;
};

export type BalanceStartPayload = {
  balance_start: number;
  source: "MANUAL" | "AUTO_CHECK";
};
