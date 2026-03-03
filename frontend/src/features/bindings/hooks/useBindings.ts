import { useEffect, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";
import type {
  BalanceStartPayload,
  BindAccountPayload,
  Binding,
  BulkBindPayload,
  RequestOTPPayload,
  VerifyOTPPayload,
} from "../types";

export function useBindings() {
  const [bindings, setBindings] = useState<Binding[]>([]);
  const [selectedBindingIds, setSelectedBindingIds] = useState<number[]>([]);
  const [isLoadingBindings, setIsLoadingBindings] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

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
    priority: 1,
    description: "",
    notes: "",
  });

  const [bulkBindForm, setBulkBindForm] = useState({
    order_id: 0,
    server_id: 0,
    account_ids: "" as string | number[],
    priority: 1,
    description: "",
    notes: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeBindingId, setActiveBindingId] = useState<number | null>(null);
  const [pendingReleaseBindingId, setPendingReleaseBindingId] = useState<number | null>(null);

  useEffect(() => {
    void loadBindings();
    void loadDropdownOptions();
  }, []);

  async function loadDropdownOptions(): Promise<void> {
    try {
      setIsLoadingOptions(true);
      // Load orders and servers for dropdowns
      const [ordersData, serversData] = await Promise.all([
        apiRequest<{ id: number; name: string }[]>("/v1/orders?selectable=true", "GET").catch(() => []),
        apiRequest<{ id: number; name: string; port: number }[]>("/v1/bindings/servers/active", "GET").catch(() => []),
      ]);
      setOrders(ordersData);
      setServers(serversData);
    } catch (error) {
      console.error("Failed to load dropdown options:", error);
    } finally {
      setIsLoadingOptions(false);
    }
  }

  async function loadAccountsForOrder(orderId: number): Promise<void> {
    try {
      const accountsData = await apiRequest<{ id: number; msisdn: string }[]>(
        `/v1/bindings/accounts/by-order/${orderId}`,
        "GET",
      );
      setAccounts(accountsData);
    } catch (error) {
      console.error("Failed to load accounts:", error);
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

  async function loadBindings(): Promise<void> {
    try {
      setIsLoadingBindings(true);
      setErrorMessage(null);
      const payload = await apiRequest<Binding[]>("/v1/bindings", "GET");
      setBindings(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat bindings.");
    } finally {
      setIsLoadingBindings(false);
    }
  }

  async function bindAccount(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const payload: BindAccountPayload = {
        order_id: bindForm.order_id,
        server_id: bindForm.server_id,
        account_id: bindForm.account_id,
        priority: bindForm.priority,
        description: bindForm.description || null,
        notes: bindForm.notes || null,
      };

      const created = await apiRequest<Binding>("/v1/bindings", "POST", payload);
      setBindForm({
        order_id: 0,
        server_id: 0,
        account_id: 0,
        priority: 1,
        description: "",
        notes: "",
      });
      setAccounts([]); // Clear accounts
      setIsBindDialogOpen(false);
      upsertBinding(created);
      toast.success("Binding berhasil dibuat.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(error instanceof Error ? error.message : "Gagal membuat binding.");
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
      setErrorMessage(null);

      const accountIds =
        typeof bulkBindForm.account_ids === "string"
          ? bulkBindForm.account_ids.split(",").map((s) => parseInt(s.trim(), 10))
          : bulkBindForm.account_ids;

      const payload: BulkBindPayload = {
        order_id: bulkBindForm.order_id,
        server_id: bulkBindForm.server_id,
        account_ids: accountIds,
        priority: bulkBindForm.priority,
        description: bulkBindForm.description || null,
        notes: bulkBindForm.notes || null,
      };

      const created = await apiRequest<Binding[]>("/v1/bindings/bulk", "POST", payload);
      setBulkBindForm({
        order_id: 0,
        server_id: 0,
        account_ids: "",
        priority: 1,
        description: "",
        notes: "",
      });
      setIsBulkBindDialogOpen(false);
      created.forEach((b) => upsertBinding(b));
      toast.success(`${created.length} bindings berhasil dibuat.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(error instanceof Error ? error.message : "Gagal membuat bulk bindings.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function requestOTP(bindingId: number, pin: string): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(bindingId, "request_otp");

      const payload: RequestOTPPayload = { pin };
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/request-otp`,
        "POST",
        payload,
      );
      upsertBinding(updated);
      setIsOTPDialogOpen(false);
      setActiveBindingId(null);
      toast.success("OTP berhasil diminta.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal meminta OTP.");
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function verifyOTP(bindingId: number, otp: string): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(bindingId, "verify_otp");

      const payload: VerifyOTPPayload = { otp };
      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/verify-otp`,
        "POST",
        payload,
      );
      upsertBinding(updated);
      setIsOTPDialogOpen(false);
      setActiveBindingId(null);
      toast.success("OTP berhasil diverifikasi.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memverifikasi OTP.");
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function markVerified(bindingId: number): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(bindingId, "mark_verified");

      const updated = await apiRequest<Binding>(
        `/v1/bindings/${bindingId}/mark-verified`,
        "POST",
      );
      upsertBinding(updated);
      toast.success("Binding marked as verified.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal mark verified.");
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
      setErrorMessage(null);
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
      toast.success("Balance start berhasil diupdate.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal update balance start.");
    } finally {
      setIsSubmitting(false);
      clearRowAction(bindingId);
    }
  }

  async function releaseBinding(bindingId: number): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(bindingId, "release");

      await apiRequest(`/v1/bindings/${bindingId}/release`, "POST");
      removeBindingFromState(bindingId);
      setIsReleaseConfirmOpen(false);
      setPendingReleaseBindingId(null);
      toast.success("Binding berhasil di-release.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal release binding.");
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
    markVerified,
    setBalanceStart,
    releaseBinding,
    openOTPDialog,
    openBalanceDialog,
    openReleaseConfirm,
    handleOrderChange,
  };
}
