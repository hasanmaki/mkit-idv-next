import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";

import {
  defaultBindingFilters,
  type AccountOption,
  type Binding,
  type BindingBulkPayload,
  type BindingBulkResult,
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
  const [selectedBindingIds, setSelectedBindingIds] = useState<number[]>([]);
  const [serverOptions, setServerOptions] = useState<ServerOption[]>([]);
  const [accountOptions, setAccountOptions] = useState<AccountOption[]>([]);
  const [filters, setFilters] = useState<BindingFilters>(defaultBindingFilters);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});
  const [bulkResult, setBulkResult] = useState<BindingBulkResult | null>(null);

  useEffect(() => {
    void loadBindings();
    void loadBindingOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeCount = useMemo(
    () => bindings.filter((item) => item.unbound_at === null).length,
    [bindings],
  );
  const selectedCount = selectedBindingIds.length;
  const allSelected =
    bindings.length > 0 && selectedBindingIds.length === bindings.length;

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
      setSelectedBindingIds((previous) =>
        previous.filter((id) => payload.some((item) => item.id === id)),
      );
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

  function toggleSelectAll(checked: boolean): void {
    setSelectedBindingIds(checked ? bindings.map((binding) => binding.id) : []);
  }

  function toggleSelectBinding(bindingId: number, checked: boolean): void {
    if (checked) {
      setSelectedBindingIds((previous) => [...new Set([...previous, bindingId])]);
      return;
    }
    setSelectedBindingIds((previous) => previous.filter((id) => id !== bindingId));
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

  async function checkBalanceBinding(bindingId: number): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "check_balance");
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/check-balance`, "POST");
      toast.success(`Balance checked for binding #${bindingId}.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Check balance binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function refreshTokenLocationBinding(bindingId: number): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "refresh_token");
      await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/refresh-token-location`,
        "POST",
      );
      toast.success(`token_loc refreshed for binding #${bindingId}.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Refresh token_loc binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function verifyResellerBinding(bindingId: number): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(bindingId, "verify_reseller");
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/verify-reseller`, "POST");
      toast.success(`Reseller verified for binding #${bindingId}.`);
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Verify reseller binding #${bindingId} gagal.`);
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
      setSelectedBindingIds((previous) => previous.filter((id) => id !== bindingId));
      toast.success(`Binding #${bindingId} deleted.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Delete binding #${bindingId} gagal.`);
    } finally {
      clearRowAction(bindingId);
    }
  }

  async function dryRunBulkBindings(payload: BindingBulkPayload): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const result = await apiRequest<BindingBulkResult>(
        "/v1/bindings/bulk/dry-run",
        "POST",
        payload,
      );
      setBulkResult(result);
      toast.success("Dry run bulk binding selesai.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Dry run bulk binding gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createBulkBindings(payload: BindingBulkPayload): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const result = await apiRequest<BindingBulkResult>(
        "/v1/bindings/bulk",
        "POST",
        payload,
      );
      setBulkResult(result);
      toast.success(
        `Bulk binding selesai. Created ${result.total_created}, failed ${result.total_failed}.`,
      );
      await loadBindings();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Create bulk binding gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function runBulkSelected(
    actionName: string,
    runner: (bindingId: number) => Promise<void>,
  ): Promise<void> {
    if (selectedBindingIds.length === 0) {
      return;
    }
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const failures: string[] = [];
      for (const bindingId of selectedBindingIds) {
        try {
          await runner(bindingId);
        } catch (error) {
          failures.push(
            error instanceof Error
              ? `ID ${bindingId}: ${error.message}`
              : `ID ${bindingId}: unknown error`,
          );
        }
      }
      if (failures.length > 0) {
        setErrorMessage(`Bulk ${actionName} sebagian gagal. ${failures.join(" | ")}`);
        toast.warning(`Bulk ${actionName} selesai dengan ${failures.length} gagal.`);
      } else {
        toast.success(`Bulk ${actionName} selesai.`);
      }
      await loadBindings();
    } finally {
      setIsSubmitting(false);
    }
  }

  async function bulkCheckBalance(): Promise<void> {
    await runBulkSelected("check balance", async (bindingId) => {
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/check-balance`, "POST");
    });
  }

  async function bulkRefreshTokenLocation(): Promise<void> {
    await runBulkSelected("refresh token", async (bindingId) => {
      await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/refresh-token-location`,
        "POST",
      );
    });
  }

  async function bulkRequestLogin(pin: string | null): Promise<void> {
    await runBulkSelected("request login", async (bindingId) => {
      await apiRequest(`/v1/bindings/${bindingId}/request-login`, "POST", { pin });
    });
  }

  async function bulkLogout(payload: BindingLogoutPayload): Promise<void> {
    await runBulkSelected("logout", async (bindingId) => {
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/logout`, "POST", payload);
    });
  }

  async function bulkDelete(): Promise<void> {
    await runBulkSelected("delete", async (bindingId) => {
      await apiRequest<void>(`/v1/bindings/${bindingId}`, "DELETE");
    });
    setSelectedBindingIds([]);
  }

  async function bulkVerifyReseller(): Promise<void> {
    await runBulkSelected("verify reseller", async (bindingId) => {
      await apiRequest<Binding>(`/v1/bindings/${bindingId}/verify-reseller`, "POST");
    });
  }

  return {
    bindings,
    selectedBindingIds,
    serverOptions,
    accountOptions,
    filters,
    setFilters,
    errorMessage,
    isLoading,
    isSubmitting,
    bulkResult,
    pendingRowActions,
    activeCount,
    selectedCount,
    allSelected,
    loadBindings,
    loadBindingOptions,
    applyFilters,
    resetFilters,
    toggleSelectAll,
    toggleSelectBinding,
    createBinding,
    dryRunBulkBindings,
    createBulkBindings,
    requestBindingLogin,
    checkBalanceBinding,
    refreshTokenLocationBinding,
    verifyResellerBinding,
    verifyBinding,
    logoutBinding,
    deleteBinding,
    bulkCheckBalance,
    bulkRefreshTokenLocation,
    bulkRequestLogin,
    bulkLogout,
    bulkDelete,
    bulkVerifyReseller,
  };
}
