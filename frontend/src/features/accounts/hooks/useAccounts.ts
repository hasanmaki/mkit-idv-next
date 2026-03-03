import { useEffect, useState, useMemo, useCallback } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";
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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  const [isSingleDialogOpen, setIsSingleDialogOpen] = useState(false);
  const [isBulkDialogOpen, setIsBulkDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isBulkDeleteConfirmOpen, setIsBulkDeleteConfirmOpen] = useState(false);

  const [filters, setFilters] = useState<AccountFilters>(defaultAccountFilters);

  const [singleForm, setSingleForm] = useState<AccountSingleForm>({
    order_id: 0,
    msisdn: "",
    batch_id: "",
    email: "",
    pin: "",
    notes: "",
    is_reseller: false,
  });

  const [bulkForm, setBulkForm] = useState<AccountBulkForm>({
    order_id: 0,
    msisdns_text: "",
    batch_id: "",
    pin: "",
    email: "",
  });

  const [editForm, setEditForm] = useState<AccountEditForm | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingAccountId, setEditingAccountId] = useState<number | null>(null);
  const [pendingDeleteAccountId, setPendingDeleteAccountId] = useState<number | null>(null);

  const totalReseller = useMemo(() => accounts.filter((a) => a.is_reseller).length, [accounts]);
  const selectedCount = selectedAccountIds.length;
  const allSelected = accounts.length > 0 && selectedAccountIds.length === accounts.length;

  const loadAccounts = useCallback(async (): Promise<void> => {
    try {
      setIsLoadingAccounts(true);
      setErrorMessage(null);

      const params = new URLSearchParams();
      if (filters.order_id) params.set("order_id", filters.order_id.toString());
      if (filters.msisdn) params.set("msisdn", filters.msisdn);
      if (filters.email) params.set("email", filters.email);
      if (filters.status) params.set("status", filters.status);
      if (filters.batch_id) params.set("batch_id", filters.batch_id);
      if (filters.is_reseller) params.set("is_reseller", filters.is_reseller);

      const payload = await apiRequest<Account[]>(`/v1/accounts?${params.toString()}`, "GET");
      setAccounts(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat accounts.");
    } finally {
      setIsLoadingAccounts(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadAccounts();
  }, [loadAccounts]);

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
      setErrorMessage(null);

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
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat account.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createBulkAccounts(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const msisdns = bulkForm.msisdns_text.split(/[\n,]/).map(s => s.trim()).filter(Boolean);
      const payload = {
        order_id: bulkForm.order_id,
        msisdns,
        email_suffix: bulkForm.email, // Mapping to backend
        batch_id: bulkForm.batch_id,
        pin: bulkForm.pin,
      };

      await apiRequest<Account[]>("/v1/accounts/bulk", "POST", payload);
      setBulkForm({
        order_id: 0,
        msisdns_text: "",
        batch_id: "",
        pin: "",
        email: "",
      });
      setIsBulkDialogOpen(false);
      void loadAccounts();
      toast.success(`${msisdns.length} accounts berhasil dibuat.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat bulk accounts.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function openEditAccount(account: Account): void {
    setEditingAccountId(account.id);
    setEditForm({
      email: account.email,
      pin: account.pin || "",
      status: account.status,
      last_device_id: account.last_device_id || "",
      notes: account.notes || "",
      is_reseller: account.is_reseller,
    });
    setIsEditDialogOpen(true);
  }

  async function saveEditAccount(): Promise<void> {
    if (!editingAccountId || !editForm) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(editingAccountId, "edit");

      const payload: AccountUpdatePayload = {
        email: editForm.email || undefined,
        pin: editForm.pin || undefined,
        notes: editForm.notes || undefined,
        is_reseller: editForm.is_reseller,
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
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update account #${editingAccountId}.`);
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
      setErrorMessage(null);
      markRowAction(pendingDeleteAccountId, "delete");
      await apiRequest<void>(`/v1/accounts/${pendingDeleteAccountId}`, "DELETE");
      setAccounts((previous) => previous.filter((a) => a.id !== pendingDeleteAccountId));
      setSelectedAccountIds((previous) => previous.filter((id) => id !== pendingDeleteAccountId));
      setIsDeleteConfirmOpen(false);
      setPendingDeleteAccountId(null);
      toast.success("Account berhasil dihapus.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal menghapus account.");
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
      setErrorMessage(null);
      await apiRequest<void>("/v1/accounts/bulk-delete", "POST", { ids: selectedAccountIds });
      setAccounts((previous) => previous.filter((a) => !selectedAccountIds.includes(a.id)));
      setSelectedAccountIds([]);
      setIsBulkDeleteConfirmOpen(false);
      toast.success(`${selectedCount} accounts berhasil dihapus.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal menghapus selected accounts.");
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
    totalReseller,
    selectedCount,
    allSelected,
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
  };
}
