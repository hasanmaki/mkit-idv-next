export type AccountStatus = "NEW" | "ACTIVE" | "EXHAUSTED" | "DISABLED";

export type Account = {
  id: number;
  order_id: number;
  msisdn: string;
  email: string;
  pin: string | null;
  status: AccountStatus;
  is_reseller: boolean;
  balance_last: number | null;
  used_count: number;
  last_used_at: string | null;
  last_device_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type AccountCreatePayload = {
  order_id: number;
  msisdn: string;
  email: string;
  pin?: string | null;
  is_reseller?: boolean;
};

export type AccountUpdatePayload = {
  email?: string | null;
  pin?: string | null;
  is_reseller?: boolean;
  notes?: string | null;
};

export type AccountFilters = {
  order_id: number | null;
  msisdn: string;
  email: string;
  status: AccountStatus | "";
  batch_id: string;
  is_reseller: string;
};

export const defaultAccountFilters: AccountFilters = {
  order_id: null,
  msisdn: "",
  email: "",
  status: "",
  batch_id: "",
  is_reseller: "",
};

export const ACCOUNT_STATUSES: AccountStatus[] = [
  "NEW",
  "ACTIVE",
  "EXHAUSTED",
  "DISABLED",
];

export type AccountSingleForm = {
  order_id: number;
  msisdn: string;
  batch_id: string;
  email: string;
  pin: string;
  notes: string;
  is_reseller: boolean;
};

export type AccountBulkForm = {
  order_id: number;
  msisdns_text: string;
  batch_id: string;
  pin: string;
  email: string;
};

export type AccountEditForm = {
  email: string;
  pin: string;
  status: AccountStatus;
  last_device_id: string;
  notes: string;
  is_reseller: boolean;
};
