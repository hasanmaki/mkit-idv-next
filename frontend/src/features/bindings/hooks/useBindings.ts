import { useEffect, useState, useMemo, useCallback } from "react";
import { toast } from "sonner";

import { apiRequest, ApiError } from "@/lib/api";
import { useApiError } from "@/hooks/useApiError";
import type {
  BalanceStartPayload,
  BindAccountPayload,
  Binding,
  BulkBindPayload,
  RequestOTPPayload,
  VerifyOTPPayload,
  WorkflowStepPayload,
} from "../types";

export function useBindings() {
  const [bindings, setBindings] = useState<Binding[]>([]);
  const [selectedBindingIds, setSelectedBindingIds] = useState<number[]>([]);
  const [isLoadingBindings, setIsLoadingBindings] = useState(false);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  // Memoize options to prevent unstable handleError from useApiError
  const apiErrorOptions = useMemo(() => ({ displayMode: "toast" as const }), []);
  
  const {
    error,
    isDialogOpen,
    errorMessage,
    handleError,
    clearError,
    closeDialog,
  } = useApiError(apiErrorOptions);

  const [isBindDialogOpen, setIsBindDialogOpen] = useState(false);
  const [isBulkBindDialogOpen, setIsBulkBindDialogOpen] = useState(false);
  const [isOTPDialogOpen, setIsOTPDialogOpen] = useState(false);
  const [isBalanceDialogOpen, setIsBalanceDialogOpen] = useState(false);
  const [isReleaseConfirmOpen, setIsReleaseConfirmOpen] = useState(false);

  // Dropdown options
  const [orders, setOrders] = useState<{ id: number; name: string }[]>([]);
  const [servers, setServers] = useState<{ id: number; name: string; port: number }[]>([]);
  const [accounts, setAccounts] = useState<{ id: number; msisdn: string }[]>([]);
  const [isLoadingOptions, setIsLoadingOptions] = useState(false);

  const [bindForm, setBindForm] = useState({
    order_id: 0,
    server_id: 0,
    account_id: 0,
    is_reseller: false,
    priority: 1,
    description: "",
    notes: "",
  });

  const [bulkBindForm, setBulkBindForm] = useState({
    order_id: 0,
    server_id: 0,
    account_ids: "" as string | number[],
    is_reseller: false,
    priority: 1,
    description: "",
    notes: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeBindingId, setActiveBindingId] = useState<number | null>(null);
  const [pendingReleaseBindingId, setPendingReleaseBindingId] = useState<number | null>(null);

  const loadBindings = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingBindings(true);
      const payload = await apiRequest<Binding[]>("/v1/bindings", "GET");
      setBindings(payload);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingBindings(false);
    }
  }, [handleError]);

  const loadDropdownOptions = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingOptions(true);
      const [ordersData, serversData] = await Promise.all([
        apiRequest<{ id: number; name: string }[]>("/v1/orders?selectable=true", "GET").catch(() => []),
        apiRequest<{ id: number; name: string; port: number }[]>("/v1/bindings/servers/active", "GET").catch(() => []),
      ]);
      setOrders(ordersData);
      setServers(serversData);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingOptions(false);
    }
  }, [handleError]);

  useEffect(() => {
    void loadBindings();
    void loadDropdownOptions();
  }, [loadBindings, loadDropdownOptions]);

  async function loadAccountsForOrder(orderId: number): Promise<void> {
    try {
      const accountsData = await apiRequest<{ id: number; msisdn: string }[]>(
        `/v1/bindings/accounts/by-order/${orderId}`,
        "GET",
      );
      setAccounts(accountsData);
    } catch (error) {
      handleError(error);
      setAccounts([]);
    }
  }

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

  function upsertBinding(nextBinding: Binding): void {
    setBindings((previous) => {
      const idx = previous.findIndex((binding) => binding.id === nextBinding.id);
      if (idx < 0) {
        return [nextBinding, ...previous];
      }
      const cloned = [...previous];
      cloned[idx] = nextBinding;
      return cloned;
    });
  }

  function removeBindingFromState(bindingId: number): void {
    setBindings((previous) => previous.filter((binding) => binding.id !== bindingId));
    setSelectedBindingIds((previous) => previous.filter((id) => id !== bindingId));
  }

  async function bindAccount(): Promise<void> {
    try {
      setIsSubmitting(true);

      const payload: BindAccountPayload = {
        order_id: bindForm.order_id,
        server_id: bindForm.server_id,
        account_id: bindForm.account_id,
        is_reseller: bindForm.is_reseller,
        priority: bindForm.priority,
        description: bindForm.description || null,
        notes: bindForm.notes || null,
      };

      const created = await apiRequest<Binding>("/v1/bindings", "POST", payload);
      setBindForm({
        order_id: 0,
        server_id: 0,
        account_id: 0,
        is_reseller: false,
        priority: 1,
        description: "",
        notes: "",
      });
      setAccounts([]);
      setIsBindDialogOpen(false);
      upsertBinding(created);
      toast.success("Binding berhasil dibuat.");
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleOrderChange(orderId: number): void {
    setBindForm((prev) => ({ ...prev, order_id: orderId }));
    if (orderId > 0) {
      void loadAccountsForOrder(orderId);
    } else {
      setAccounts([]);
    }
  }

  async function bulkBindAccounts(): Promise<void> {
    try {
      setIsSubmitting(true);

      const accountIds =
        typeof bulkBindForm.account_ids === "string"
          ? bulkBindForm.account_ids.split(",").map((s) => parseInt(s.trim(), 10)).filter(n => !isNaN(n))
          : bulkBindForm.account_ids;

      const payload: BulkBindPayload = {
        order_id: bulkBindForm.order_id,
        server_id: bulkBindForm.server_id,
        account_ids: accountIds,
        is_reseller: bulkBindForm.is_reseller,
        priority: bulkBindForm.priority,
        description: bulkBindForm.description || null,
        notes: bulkBindForm.notes || null,
      };

      const created = await apiRequest<Binding[]>("/v1/bindings/bulk", "POST", payload);
      setBulkBindForm({
        order_id: 0,
        server_id: 0,
        account_ids: "",
        is_reseller: false,
        priority: 1,
        description: "",
        notes: "",
      });
      setIsBulkBindDialogOpen(false);
      // Refresh list to be sure
      void loadBindings();
      toast.success(`${created.length} bindings berhasil dibuat.`);
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
    }
  }

  async function requestOTP(bindingId: number, pin: string): Promise<void> {
    try {
      setIsSubmitting(true);
      markRowAction(bindingId, "request_otp");

      const payload: RequestOTPPayload = { pin };
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/otp/request`,
        "POST",
        payload,
      );
      upsertBinding(updated);
      setIsOTPDialogOpen(false);
      setActiveBindingId(null);
      toast.success("OTP berhasil diminta dari provider.");
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function verifyOTP(bindingId: number, otp: string): Promise<void> {
    try {
      setIsSubmitting(true);
      markRowAction(bindingId, "verify_otp");

      const payload: VerifyOTPPayload = { otp };
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/otp/verify`,
        "POST",
        payload,
      );
      upsertBinding(updated);
      setIsOTPDialogOpen(false);
      setActiveBindingId(null);
      toast.success("OTP berhasil diverifikasi. Saldo dan token telah diperbarui.");
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function updateWorkflowStep(
    bindingId: number, 
    step: string, 
    tokenLocation?: string | null
  ): Promise<void> {
    try {
      setIsSubmitting(true);
      markRowAction(bindingId, "update_step");

      const payload: WorkflowStepPayload = { 
        step, 
        token_location: tokenLocation 
      };
      
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/step`,
        "PATCH",
        payload,
      );
      upsertBinding(updated);
      toast.success(`Workflow step updated to ${step}.`);
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function setBalanceStart(
    bindingId: number,
    balance: number,
    source: "MANUAL" | "AUTO_CHECK",
  ): Promise<void> {
    try {
      setIsSubmitting(true);
      markRowAction(bindingId, "set_balance");

      const payload: BalanceStartPayload = { balance_start: balance, source };
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/balance`,
        "PATCH",
        payload,
      );
      upsertBinding(updated);
      setIsBalanceDialogOpen(false);
      setActiveBindingId(null);
      toast.success("Balance start berhasil diperbarui.");
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function releaseBinding(bindingId: number): Promise<void> {
    try {
      setIsSubmitting(true);
      markRowAction(bindingId, "release");

      await apiRequest(`/v1/bindings/${bindingId}/release`, "POST", {});
      removeBindingFromState(bindingId);
      setIsReleaseConfirmOpen(false);
      setPendingReleaseBindingId(null);
      toast.success("Binding berhasil di-release.");
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  function openOTPDialog(bindingId: number): void {
    setActiveBindingId(bindingId);
    setIsOTPDialogOpen(true);
  }

  function openBalanceDialog(bindingId: number): void {
    setActiveBindingId(bindingId);
    setIsBalanceDialogOpen(true);
  }

  function openReleaseConfirm(bindingId: number): void {
    setPendingReleaseBindingId(bindingId);
    setIsReleaseConfirmOpen(true);
  }

  return {
    bindings,
    selectedBindingIds,
    isLoadingBindings,
    error,
    isDialogOpen,
    errorMessage,
    pendingRowActions,
    isBindDialogOpen,
    setIsBindDialogOpen,
    isBulkBindDialogOpen,
    setIsBulkBindDialogOpen,
    isOTPDialogOpen,
    setIsOTPDialogOpen,
    isBalanceDialogOpen,
    setIsBalanceDialogOpen,
    isReleaseConfirmOpen,
    setIsReleaseConfirmOpen,
    isLoadingOptions,
    orders,
    servers,
    accounts,
    bindForm,
    setBindForm,
    bulkBindForm,
    setBulkBindForm,
    isSubmitting,
    activeBindingId,
    pendingReleaseBindingId,
    loadBindings,
    bindAccount,
    bulkBindAccounts,
    requestOTP,
    verifyOTP,
    updateWorkflowStep,
    setBalanceStart,
    releaseBinding,
    openOTPDialog,
    openBalanceDialog,
    openReleaseConfirm,
    handleOrderChange,
    handleError,
    clearError,
    closeDialog,
  };
}
