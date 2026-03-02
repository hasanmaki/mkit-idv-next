import type { Server } from "@/types/server";

export type SingleServerForm = {
  name: string;
  host: string;
  port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  delay_per_hit: number;
  is_active: boolean;
  notes: string;
};

export const defaultSingleForm: SingleServerForm = {
  name: "Server 1",
  host: "http://10.0.0.3",
  port: 9900,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  delay_per_hit: 0,
  is_active: true,
  notes: "",
};

export type BulkServerForm = {
  base_name: string;
  base_host: string;
  start_port: number;
  end_port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  delay_per_hit: number;
  is_active: boolean;
  notes: string;
};

export const defaultBulkForm: BulkServerForm = {
  base_name: "Server",
  base_host: "http://10.0.0.3",
  start_port: 9900,
  end_port: 9909,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  delay_per_hit: 0,
  is_active: true,
  notes: "",
};

export type EditServerForm = {
  name: string;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  delay_per_hit: number;
  is_active: boolean;
  notes: string;
};

export function toEditServerForm(server: Server): EditServerForm {
  return {
    name: server.name,
    description: server.description ?? "",
    timeout: server.timeout,
    retries: server.retries,
    wait_between_retries: server.wait_between_retries,
    max_requests_queued: server.max_requests_queued,
    delay_per_hit: server.delay_per_hit,
    is_active: server.is_active,
    notes: server.notes ?? "",
  };
}
