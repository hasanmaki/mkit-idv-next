export type Server = {
  id: number;
  port: number;
  base_url: string;
  description: string | null;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string | null;
  device_id: string | null;
  created_at: string;
  updated_at: string;
};

export type ServerBulkItemResult = {
  port: number;
  base_url: string;
  status: "created" | "would_create" | "skipped" | "failed";
  reason: string | null;
  server: Server | null;
};

export type ServerBulkCreateResult = {
  dry_run: boolean;
  base_host: string;
  start_port: number;
  end_port: number;
  total_requested: number;
  total_created: number;
  total_skipped: number;
  total_failed: number;
  items: ServerBulkItemResult[];
};

export type ServerCreatePayload = {
  port: number;
  base_url: string;
  description: string | null;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string | null;
  device_id: string | null;
};

export type ServerBulkPayload = {
  base_host: string;
  start_port: number;
  end_port: number;
  description: string | null;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string | null;
  device_id: string | null;
};
