export type Account = {
  id: number;
  order_id: number;
  order_name: string;
  msisdn: string;
  email: string;
  pin: string | null;
  is_active: boolean;
  balance_last: number | null;
  card_active_until: string | null;
  grace_period_until: string | null;
  expires_info: string | null;
  used_count: number;
  last_used_at: string | null;
  last_balance_response: Record<string, any> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type AccountCreatePayload = {
  order_id: number;
  msisdn: string;
  email: string;
  pin?: string | null;
};

export type AccountUpdatePayload = {
  email?: string | null;
  pin?: string | null;
  is_active?: boolean;
  notes?: string | null;
};

export type AccountFilters = {
  order_id: number | null;
  msisdn: string;
  email: string;
  is_active: string;
};

export const defaultAccountFilters: AccountFilters = {
  order_id: null,
  msisdn: "",
  email: "",
  is_active: "",
};

export type AccountSingleForm = {
  order_id: number;
  msisdn: string;
  email: string;
  pin: string;
  notes: string;
  is_reseller: boolean;
};

export type AccountBulkForm = {
  order_id: number;
  msisdns_text: string;
  pin: string;
  email: string;
};

export type AccountEditForm = {
  email: string;
  pin: string;
  is_active: boolean;
  notes: string;
};
