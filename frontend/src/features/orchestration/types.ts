import type { Binding } from "@/features/bindings/types";

export type WorkerState = "idle" | "running" | "paused" | "stopped";

export type OrchestrationStartPayload = {
  binding_ids: number[];
  product_id: string;
  email: string;
  limit_harga: number;
  interval_ms: number;
  max_retry_status: number;
  cooldown_on_error_ms: number;
};

export type OrchestrationControlPayload = {
  binding_ids: number[];
  reason?: string | null;
};

export type OrchestrationItemResult = {
  binding_id: number;
  ok: boolean;
  message: string;
};

export type OrchestrationControlResult = {
  action: string;
  items: OrchestrationItemResult[];
};

export type OrchestrationStatusItem = {
  binding_id: number;
  state: WorkerState;
  reason?: string | null;
  owner?: string | null;
  updated_at?: string | null;
};

export type OrchestrationStatusResult = {
  items: OrchestrationStatusItem[];
};

export type OrchestrationMonitorItem = {
  binding_id: number;
  state: WorkerState;
  reason?: string | null;
  state_updated_at?: string | null;
  lock_owner?: string | null;
  heartbeat_owner?: string | null;
  heartbeat_cycle?: number | null;
  heartbeat_last_action?: string | null;
  heartbeat_updated_at?: string | null;
};

export type OrchestrationMonitorResult = {
  total_workers: number;
  active_workers: number;
  items: OrchestrationMonitorItem[];
};

export type StartForm = {
  product_id: string;
  email: string;
  limit_harga: string;
  interval_ms: string;
  max_retry_status: string;
  cooldown_on_error_ms: string;
};

export const defaultStartForm: StartForm = {
  product_id: "650",
  email: "",
  limit_harga: "100000",
  interval_ms: "800",
  max_retry_status: "2",
  cooldown_on_error_ms: "1500",
};

export type BindingOption = Pick<
  Binding,
  "id" | "step" | "account_msisdn" | "batch_id" | "server_base_url" | "is_reseller"
>;

