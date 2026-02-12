export type AccountStatus = "new" | "active" | "exhausted" | "disabled";

export type Account = {
  id: number;
  msisdn: string;
  email: string;
  batch_id: string;
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

export type AccountCreateSinglePayload = {
  msisdn: string;
  email: string;
  batch_id: string;
  pin: string | null;
  notes: string | null;
};

export type AccountCreateBulkPayload = {
  msisdns: string[];
  email: string;
  batch_id: string;
  pin: string | null;
};

export type AccountUpdatePayload = {
  email?: string | null;
  pin?: string | null;
  notes?: string | null;
  status?: AccountStatus | null;
  is_reseller?: boolean | null;
  last_device_id?: string | null;
};

export type AccountDeletePayload = {
  id?: number;
  msisdn?: string;
  batch_id?: string;
};

export type AccountSingleForm = {
  msisdn: string;
  email: string;
  batch_id: string;
  pin: string;
  notes: string;
};

export const defaultAccountSingleForm: AccountSingleForm = {
  msisdn: "",
  email: "",
  batch_id: "",
  pin: "",
  notes: "",
};

export type AccountBulkForm = {
  msisdns_text: string;
  email: string;
  batch_id: string;
  pin: string;
};

export const defaultAccountBulkForm: AccountBulkForm = {
  msisdns_text: "",
  email: "",
  batch_id: "",
  pin: "",
};

export type AccountEditForm = {
  email: string;
  pin: string;
  notes: string;
  status: AccountStatus;
  is_reseller: boolean;
  last_device_id: string;
};

export function toAccountEditForm(account: Account): AccountEditForm {
  return {
    email: account.email,
    pin: account.pin ?? "",
    notes: account.notes ?? "",
    status: account.status,
    is_reseller: account.is_reseller,
    last_device_id: account.last_device_id ?? "",
  };
}

export const ACCOUNT_STATUSES: AccountStatus[] = [
  "new",
  "active",
  "exhausted",
  "disabled",
];
