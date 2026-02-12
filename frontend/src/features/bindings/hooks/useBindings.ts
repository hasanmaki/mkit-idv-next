import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";

import {
  defaultBindingFilters,
  type AccountOption,
  type Binding,
  type BindingCreatePayload,
  type BindingFilters,
  type BindingLogoutPayload,
  type BindingRequestLoginPayload,
  type BindingVerifyPayload,
  type ServerOption,
} from "../types";

function buildQuery(filters: BindingFilters): string {
  const params = new URLSearchParams();
  if (filters.server_id.trim()) {
    params.set("server_id", filters.server_id.trim());
  }
  if (filters.account_id.trim()) {
    params.set("account_id", filters.account_id.trim());
  }
  if (filters.batch_id.trim()) {
    params.set("batch_id", filters.batch_id.trim());
  }
  if (filters.step) {
    params.set("step", filters.step);
  }
  params.set("active_only", String(filters.active_only));
  const q = params.toString();
  return q ? `?${q}` : "";
}

export function useBindings() {
  const [bindings, setBindings] = useState<Binding[]>([]);
  const [serverOptions, setServerOptions] = useState<ServerOption[]>([]);
  const [accountOptions, setAccountOptions] = useState<AccountOption[]>([]);
  const [filters, setFilters] = useState<BindingFilters>(defaultBindingFilters);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  useEffect(() => {
    void loadBindings();
    void loadBindingOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeCount = useMemo(
    () => bindings.filter((item) => item.unbound_at === null).length,
    [bindings],
  );

  function markRowAction(bindingId: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [bindingId]: action }));
  }

  function clearRowAction(bindingId: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[bindingId];
      return next;
    });
  }

  async function loadBindings(nextFilters: BindingFilters = filters): Promise<void> {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const payload = await apiRequest<Binding[]>(
        `/v1/bindings/view${buildQuery(nextFilters)}`,
        "GET",
      );
      setBindings(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat bindings.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadBindingOptions(): Promise<void> {
    try {
      const [servers, accounts] = await Promise.all([
        apiRequest<ServerOption[]>("/v1/servers?is_active=true&limit=500", "GET"),
        apiRequest<AccountOption[]>("/v1/accounts?limit=500", "GET"),
      ]);
      setServerOptions(servers);
      setAccountOptions(accounts);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat option server/account.");
    }
  }

  async function applyFilters(): Promise<void> {
    await loadBindings(filters);
  }

  async function resetFilters(): Promise<void> {
    setFilters(defaultBindingFilters);
    await loadBindings(defaultBindingFilters);
  }

  async function createBinding(payload: BindingCreatePayload): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      await apiRequest<Binding>("/v1/bindings", "POST", payload);
      toast.success("Binding created.");
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Create binding gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function verifyBinding(
    bindingId: number,
    payload: BindingVerifyPayload,
  ): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "verify");
      await apiRequest(`/v1/bindings/${bindingId}/verify-login`, "POST", payload);
      toast.success(`Binding #${bindingId} verified.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Verify binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function requestBindingLogin(
    bindingId: number,
    payload: BindingRequestLoginPayload,
  ): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "request_login");
      await apiRequest(`/v1/bindings/${bindingId}/request-login`, "POST", payload);
      toast.success(`OTP requested for binding #${bindingId}.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Request login binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function logoutBinding(
    bindingId: number,
    payload: BindingLogoutPayload,
  ): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "logout");
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/logout`, "POST", payload);
      toast.success(`Binding #${bindingId} logged out.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Logout binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function deleteBinding(bindingId: number): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "delete");
      await apiRequest<void>(`/v1/bindings/${bindingId}`, "DELETE");
      setBindings((previous) => previous.filter((binding) => binding.id !== bindingId));
      toast.success(`Binding #${bindingId} deleted.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Delete binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  return {
    bindings,
    serverOptions,
    accountOptions,
    filters,
    setFilters,
    errorMessage,
    isLoading,
    isSubmitting,
    pendingRowActions,
    activeCount,
    loadBindings,
    loadBindingOptions,
    applyFilters,
    resetFilters,
    createBinding,
    requestBindingLogin,
    verifyBinding,
    logoutBinding,
    deleteBinding,
  };
}
