import type { Server } from "@/types/server";

export type SingleServerForm = {
  host: string;
  port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string;
};

export const defaultSingleForm: SingleServerForm = {
  host: "http://10.0.0.3",
  port: 9900,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  is_active: true,
  notes: "",
};

export type BulkServerForm = {
  base_host: string;
  start_port: number;
  end_port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string;
};

export const defaultBulkForm: BulkServerForm = {
  base_host: "http://10.0.0.3",
  start_port: 9900,
  end_port: 9909,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  is_active: true,
  notes: "",
};

export type EditServerForm = {
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string;
};

export function toEditServerForm(server: Server): EditServerForm {
  return {
    description: server.description ?? "",
    timeout: server.timeout,
    retries: server.retries,
    wait_between_retries: server.wait_between_retries,
    max_requests_queued: server.max_requests_queued,
    is_active: server.is_active,
    notes: server.notes ?? "",
  };
}
