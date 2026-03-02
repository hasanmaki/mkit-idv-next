export type Binding = {
  id: number;
  session_id: number;
  server_id: number;
  account_id: number;
  step: "BINDED" | "REQUEST_OTP" | "VERIFY_OTP" | "VERIFIED" | "LOGGED_OUT";
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
  session_id: number;
  server_id: number;
  account_id: number;
  priority?: number;
  description?: string | null;
  notes?: string | null;
};

export type BulkBindPayload = {
  session_id: number;
  server_id: number;
  account_ids: number[];
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

export type BalanceStartPayload = {
  balance_start: number;
  source: "MANUAL" | "AUTO_CHECK";
};
