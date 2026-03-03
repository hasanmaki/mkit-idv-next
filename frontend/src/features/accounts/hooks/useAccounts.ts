import { useEffect, useState, useMemo, useCallback } from "react";
import { toast } from "sonner";

import { apiRequest, ApiError } from "@/lib/api";
import { useApiError } from "@/hooks/useApiError";
import type {
  Account,
  AccountCreatePayload,
  AccountFilters,
  AccountUpdatePayload,
  AccountSingleForm,
  AccountBulkForm,
  AccountEditForm,
} from "../types";
import { defaultAccountFilters } from "../types";

export function useAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccountIds, setSelectedAccountIds] = useState<number[]>([]);
  const [isLoadingAccounts, setIsLoadingAccounts] = useState(false);
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

  const [isSingleDialogOpen, setIsSingleDialogOpen] = useState(false);
  const [isBulkDialogOpen, setIsBulkDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isBulkDeleteConfirmOpen, setIsBulkDeleteConfirmOpen] = useState(false);

  const [filters, setFilters] = useState<AccountFilters>(defaultAccountFilters);

  // Orders for dropdown
  const [orders, setOrders] = useState<{ id: number; name: string }[]>([]);
  const [isLoadingOrders, setIsLoadingOrders] = useState(false);

  const [singleForm, setSingleForm] = useState<AccountSingleForm>({
    order_id: 0,
    msisdn: "",
    email: "",
    pin: "",
    notes: "",
    is_reseller: false,
  });

  const [bulkForm, setBulkForm] = useState<AccountBulkForm>({
    order_id: 0,
    msisdns_text: "",
    pin: "",
    email: "",
  });

  const [editForm, setEditForm] = useState<AccountEditForm | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingAccountId, setEditingAccountId] = useState<number | null>(null);
  const [pendingDeleteAccountId, setPendingDeleteAccountId] = useState<number | null>(null);

  const selectedCount = selectedAccountIds.length;
  const allSelected = accounts.length > 0 && selectedAccountIds.length === accounts.length;

  // Load orders for dropdown
  const loadOrders = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingOrders(true);
      const ordersData = await apiRequest<{ id: number; name: string }[]>("/v1/orders", "GET");
      setOrders(ordersData);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingOrders(false);
    }
  }, [handleError]);

  const loadAccounts = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingAccounts(true);

      const params = new URLSearchParams();
      if (filters.order_id) params.set("order_id", filters.order_id.toString());
      if (filters.msisdn) params.set("msisdn", filters.msisdn);
      if (filters.email) params.set("email", filters.email);
      if (filters.status) params.set("status", filters.status);
      if (filters.is_reseller) params.set("is_reseller", filters.is_reseller);

      const payload = await apiRequest<Account[]>(`/v1/accounts?${params.toString()}`, "GET");
      setAccounts(payload);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingAccounts(false);
    }
  }, [filters, handleError]);

  // Initial load
  useEffect(() => {
    void loadAccounts();
    void loadOrders();
  }, [loadAccounts, loadOrders]);

  function applyFilters(): void {
    void loadAccounts();
  }

  function resetFilters(): void {
    setFilters(defaultAccountFilters);
    void loadAccounts();
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedAccountIds(checked ? accounts.map((a) => a.id) : []);
  }

  function toggleSelectAccount(accountId: number, checked: boolean): void {
    if (checked) {
      setSelectedAccountIds((previous) => [...new Set([...previous, accountId])]);
      return;
    }
    setSelectedAccountIds((previous) => previous.filter((id) => id !== accountId));
  }

  async function createSingleAccount(): Promise<void> {
    try {
      setIsSubmitting(true);

      const payload: AccountCreatePayload = {
        order_id: singleForm.order_id,
        msisdn: singleForm.msisdn.trim(),
        email: singleForm.email.trim(),
        pin: singleForm.pin || undefined,
        is_reseller: singleForm.is_reseller,
      };

      const created = await apiRequest<Account>("/v1/accounts", "POST", payload);
      setSingleForm({
        order_id: 0,
        msisdn: "",
        batch_id: "",
        email: "",
        pin: "",
        notes: "",
        is_reseller: false,
      });
      setIsSingleDialogOpen(false);
      setAccounts((previous) => [created, ...previous]);
      toast.success("Account berhasil dibuat.");
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createBulkAccounts(): Promise<void> {
    try {
      setIsSubmitting(true);

      const msisdns = bulkForm.msisdns_text.split(/[\n,]/).map(s => s.trim()).filter(Boolean);
      const payload = {
        order_id: bulkForm.order_id,
        accounts: msisdns.map((msisdn) => ({
          msisdn,
          email: bulkForm.email,
          pin: bulkForm.pin || undefined,
        })),
      };

      await apiRequest<Account[]>("/v1/accounts/bulk", "POST", payload);
      setBulkForm({
        order_id: 0,
        msisdns_text: "",
        pin: "",
        email: "",
      });
      setIsBulkDialogOpen(false);
      void loadAccounts();
      toast.success(`${msisdns.length} accounts berhasil dibuat.`);
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
    }
  }

  function openEditAccount(account: Account): void {
    setEditingAccountId(account.id);
    setEditForm({
      email: account.email,
      pin: account.pin || "",
      is_active: account.is_active,
      notes: account.notes || "",
    });
    setIsEditDialogOpen(true);
  }

  async function saveEditAccount(): Promise<void> {
    if (!editingAccountId || !editForm) {
      return;
    }

    try {
      setIsSubmitting(true);
      markRowAction(editingAccountId, "edit");

      const payload: AccountUpdatePayload = {
        email: editForm.email || undefined,
        pin: editForm.pin || undefined,
        notes: editForm.notes || undefined,
        is_active: editForm.is_active,
      };

      const updated = await apiRequest<Account>(
        `/v1/accounts/${editingAccountId}`,
        "PATCH",
        payload,
      );
      setIsEditDialogOpen(false);
      setEditingAccountId(null);
      setEditForm(null);
      setAccounts((previous) =>
        previous.map((a) => (a.id === editingAccountId ? updated : a)),
      );
      toast.success(`Account #${editingAccountId} berhasil diupdate.`);
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
      if (editingAccountId) {
        clearRowAction(editingAccountId);
      }
    }
  }

  function openDeleteConfirm(accountId: number): void {
    setPendingDeleteAccountId(accountId);
    setIsDeleteConfirmOpen(true);
  }

  async function confirmDeleteSingle(): Promise<void> {
    if (!pendingDeleteAccountId) {
      return;
    }

    try {
      setIsSubmitting(true);
      markRowAction(pendingDeleteAccountId, "delete");
      await apiRequest<void>(`/v1/accounts/${pendingDeleteAccountId}`, "DELETE");
      setAccounts((previous) => previous.filter((a) => a.id !== pendingDeleteAccountId));
      setSelectedAccountIds((previous) => previous.filter((id) => id !== pendingDeleteAccountId));
      setIsDeleteConfirmOpen(false);
      setPendingDeleteAccountId(null);
      toast.success("Account berhasil dihapus.");
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
      if (pendingDeleteAccountId) {
        clearRowAction(pendingDeleteAccountId);
      }
    }
  }

  async function confirmDeleteSelected(): Promise<void> {
    if (selectedAccountIds.length === 0) return;

    try {
      setIsSubmitting(true);
      await apiRequest<void>("/v1/accounts/bulk-delete", "POST", { ids: selectedAccountIds });
      setAccounts((previous) => previous.filter((a) => !selectedAccountIds.includes(a.id)));
      setSelectedAccountIds([]);
      setIsBulkDeleteConfirmOpen(false);
      toast.success(`${selectedCount} accounts berhasil dihapus.`);
    } catch (error) {
      handleError(error, { displayMode: "dialog" });
    } finally {
      setIsSubmitting(false);
    }
  }

  function markRowAction(accountId: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [accountId]: action }));
  }

  function clearRowAction(accountId: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[accountId];
      return next;
    });
  }

  return {
    accounts,
    selectedAccountIds,
    isLoadingAccounts,
    error,
    isDialogOpen,
    errorMessage,
    pendingRowActions,
    isSingleDialogOpen,
    setIsSingleDialogOpen,
    isBulkDialogOpen,
    setIsBulkDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    isDeleteConfirmOpen,
    setIsDeleteConfirmOpen,
    isBulkDeleteConfirmOpen,
    setIsBulkDeleteConfirmOpen,
    filters,
    setFilters,
    singleForm,
    setSingleForm,
    bulkForm,
    setBulkForm,
    editForm,
    setEditForm,
    isSubmitting,
    selectedCount,
    allSelected,
    orders,
    isLoadingOrders,
    loadAccounts,
    applyFilters,
    resetFilters,
    toggleSelectAll,
    toggleSelectAccount,
    createSingleAccount,
    createBulkAccounts,
    openEditAccount,
    saveEditAccount,
    openDeleteConfirm,
    confirmDeleteSingle,
    confirmDeleteSelected,
    handleError,
    clearError,
    closeDialog,
  };
}
