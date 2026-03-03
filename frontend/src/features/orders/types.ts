export type Order = {
  id: number;
  name: string;
  email: string;
  default_pin: string | null;
  description: string | null;
  is_active: boolean;
  notes: string | null;
  account_count: number;
  created_at: string;
  updated_at: string;
};

export type OrderCreatePayload = {
  name: string;
  email: string;
  default_pin?: string | null;
  msisdns?: string[];
  description?: string | null;
  is_active?: boolean;
  notes?: string | null;
};

export type OrderUpdatePayload = {
  name?: string | null;
  email?: string | null;
  default_pin?: string | null;
  description?: string | null;
  is_active?: boolean;
  notes?: string | null;
};
