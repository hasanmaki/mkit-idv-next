import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";

import {
  defaultAccountBulkForm,
  defaultAccountSingleForm,
  toAccountEditForm,
  type Account,
  type AccountBulkForm,
  type AccountCreateBulkPayload,
  type AccountCreateSinglePayload,
  type AccountDeletePayload,
  type AccountEditForm,
  type AccountSingleForm,
  type AccountUpdatePayload,
} from "../types";

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

  const [singleForm, setSingleForm] = useState<AccountSingleForm>(defaultAccountSingleForm);
  const [bulkForm, setBulkForm] = useState<AccountBulkForm>(defaultAccountBulkForm);
  const [editForm, setEditForm] = useState<AccountEditForm | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingAccountId, setEditingAccountId] = useState<number | null>(null);
  const [pendingDeleteAccountId, setPendingDeleteAccountId] = useState<number | null>(null);

  const totalReseller = useMemo(
    () => accounts.filter((account) => account.is_reseller).length,
    [accounts],
  );
  const selectedCount = selectedAccountIds.length;
  const allSelected =
    accounts.length > 0 && selectedAccountIds.length === accounts.length;

  useEffect(() => {
    void loadAccounts();
  }, []);

  function upsertAccount(nextAccount: Account): void {
    setAccounts((previous) => {
      const idx = previous.findIndex((account) => account.id === nextAccount.id);
      if (idx < 0) {
        return [nextAccount, ...previous];
      }
      const cloned = [...previous];
      cloned[idx] = nextAccount;
      return cloned;
    });
  }

  function removeAccountFromState(accountId: number): void {
    setAccounts((previous) => previous.filter((account) => account.id !== accountId));
    setSelectedAccountIds((previous) => previous.filter((id) => id !== accountId));
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

  async function loadAccounts(): Promise<void> {
    try {
      setIsLoadingAccounts(true);
      setErrorMessage(null);
      const payload = await apiRequest<Account[]>("/v1/accounts", "GET");
      setAccounts(payload);
      setSelectedAccountIds((previous) =>
        previous.filter((id) => payload.some((account) => account.id === id)),
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat account list.");
    } finally {
      setIsLoadingAccounts(false);
    }
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedAccountIds(checked ? accounts.map((account) => account.id) : []);
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
      const payload: AccountCreateSinglePayload = {
        msisdn: singleForm.msisdn.trim(),
        email: singleForm.email.trim(),
        batch_id: singleForm.batch_id.trim(),
        pin: singleForm.pin.trim() || null,
        notes: singleForm.notes.trim() || null,
      };
      const created = await apiRequest<Account>("/v1/accounts", "POST", payload);
      upsertAccount(created);
      setSingleForm(defaultAccountSingleForm);
      setIsSingleDialogOpen(false);
      toast.success("Account berhasil dibuat.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat account.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function parseMsisdnText(value: string): string[] {
    return value
      .split(/[\r\n,;]+/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  }

  async function createBulkAccounts(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const payload: AccountCreateBulkPayload = {
        msisdns: parseMsisdnText(bulkForm.msisdns_text),
        email: bulkForm.email.trim(),
        batch_id: bulkForm.batch_id.trim(),
        pin: bulkForm.pin.trim() || null,
      };
      const created = await apiRequest<Account[]>("/v1/accounts/bulk", "POST", payload);
      if (created.length > 0) {
        setAccounts((previous) => [...created, ...previous]);
      }
      setBulkForm(defaultAccountBulkForm);
      setIsBulkDialogOpen(false);
      toast.success(`Bulk create berhasil: ${created.length} account.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk create account gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function openEditAccount(account: Account): void {
    setEditingAccountId(account.id);
    setEditForm(toAccountEditForm(account));
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
        email: editForm.email.trim(),
        pin: editForm.pin.trim() || null,
        notes: editForm.notes.trim() || null,
        status: editForm.status,
        is_reseller: editForm.is_reseller,
        last_device_id: editForm.last_device_id.trim() || null,
      };
      const updated = await apiRequest<Account>(
        `/v1/accounts/${editingAccountId}`,
        "PATCH",
        payload,
      );
      upsertAccount(updated);
      setIsEditDialogOpen(false);
      setEditForm(null);
      setEditingAccountId(null);
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

  async function deleteById(accountId: number): Promise<void> {
    const payload: AccountDeletePayload = { id: accountId };
    await apiRequest<void>("/v1/accounts", "DELETE", payload);
  }

  async function confirmDeleteSingle(): Promise<void> {
    if (!pendingDeleteAccountId) {
      return;
    }
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(pendingDeleteAccountId, "delete");
      await deleteById(pendingDeleteAccountId);
      removeAccountFromState(pendingDeleteAccountId);
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
    if (selectedAccountIds.length === 0) {
      return;
    }
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const failures: string[] = [];
      const deletedIds: number[] = [];
      for (const accountId of selectedAccountIds) {
        try {
          markRowAction(accountId, "delete");
          await deleteById(accountId);
          deletedIds.push(accountId);
        } catch (error) {
          failures.push(
            error instanceof Error
              ? `ID ${accountId}: ${error.message}`
              : `ID ${accountId}: unknown error`,
          );
        } finally {
          clearRowAction(accountId);
        }
      }
      setIsBulkDeleteConfirmOpen(false);
      for (const deletedId of deletedIds) {
        removeAccountFromState(deletedId);
      }
      if (failures.length > 0) {
        setErrorMessage(`Sebagian delete gagal. ${failures.join(" | ")}`);
        toast.warning(`Delete selesai dengan ${failures.length} kegagalan.`);
      } else {
        toast.success(`Berhasil menghapus ${deletedIds.length} account.`);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk delete account gagal.");
    } finally {
      setIsSubmitting(false);
    }
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
