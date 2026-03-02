export type Session = {
  id: number;
  name: string;
  email: string;
  description: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type SessionCreatePayload = {
  name: string;
  email: string;
  description?: string | null;
  is_active?: boolean;
  notes?: string | null;
};

export type SessionUpdatePayload = {
  name?: string | null;
  email?: string | null;
  description?: string | null;
  is_active?: boolean;
  notes?: string | null;
};
