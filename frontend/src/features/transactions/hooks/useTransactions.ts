import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";

import {
  defaultTransactionFilters,
  type Transaction,
  type TransactionFilters,
  type TransactionStartPayload,
} from "../types";

function buildQuery(filters: TransactionFilters): string {
  const params = new URLSearchParams();
  if (filters.status_filter) {
    params.set("status_filter", filters.status_filter);
  }
  if (filters.binding_id.trim()) {
    params.set("binding_id", filters.binding_id.trim());
  }
  if (filters.account_id.trim()) {
    params.set("account_id", filters.account_id.trim());
  }
  if (filters.server_id.trim()) {
    params.set("server_id", filters.server_id.trim());
  }
  if (filters.batch_id.trim()) {
    params.set("batch_id", filters.batch_id.trim());
  }
  const q = params.toString();
  return q ? `?${q}` : "";
}

export function useTransactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filters, setFilters] = useState<TransactionFilters>(defaultTransactionFilters);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  useEffect(() => {
    void loadTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const processingCount = useMemo(
    () =>
      transactions.filter(
        (item) => item.status === "PROCESSING" || item.status === "RESUMED",
      ).length,
    [transactions],
  );

  const successCount = useMemo(
    () => transactions.filter((item) => item.status === "SUKSES").length,
    [transactions],
  );

  function markRowAction(id: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [id]: action }));
  }

  function clearRowAction(id: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[id];
      return next;
    });
  }

  async function loadTransactions(
    nextFilters: TransactionFilters = filters,
  ): Promise<void> {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const payload = await apiRequest<Transaction[]>(
        `/v1/transactions${buildQuery(nextFilters)}`,
        "GET",
      );
      setTransactions(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat transaksi.");
    } finally {
      setIsLoading(false);
    }
  }

  async function applyFilters(): Promise<void> {
    await loadTransactions(filters);
  }

  async function resetFilters(): Promise<void> {
    setFilters(defaultTransactionFilters);
    await loadTransactions(defaultTransactionFilters);
  }

  async function startTransaction(payload: TransactionStartPayload): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      await apiRequest<Transaction>("/v1/transactions/start", "POST", payload);
      toast.success("Transaction started.");
      await loadTransactions();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Start transaction gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function runRowAction(
    transactionId: number,
    action: string,
    fn: () => Promise<void>,
  ): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(transactionId, action);
      await fn();
      await loadTransactions();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Action ${action} gagal untuk trx #${transactionId}.`);
    } finally {
      clearRowAction(transactionId);
    }
  }

  async function submitOtp(transactionId: number, otp: string): Promise<void> {
    await runRowAction(transactionId, "otp", async () => {
      await apiRequest<Transaction>(`/v1/transactions/${transactionId}/otp`, "POST", {
        otp,
      });
      toast.success(`OTP submitted for trx #${transactionId}.`);
    });
  }

  async function continueTransaction(transactionId: number): Promise<void> {
    await runRowAction(transactionId, "continue", async () => {
      await apiRequest<Transaction>(
        `/v1/transactions/${transactionId}/continue`,
        "POST",
      );
      toast.success(`Transaction #${transactionId} continued.`);
    });
  }

  async function checkTransaction(transactionId: number): Promise<void> {
    await runRowAction(transactionId, "check", async () => {
      await apiRequest(`/v1/transactions/${transactionId}/check`, "POST");
      toast.success(`Transaction #${transactionId} checked.`);
    });
  }

  async function pauseTransaction(transactionId: number, reason: string): Promise<void> {
    await runRowAction(transactionId, "pause", async () => {
      await apiRequest<Transaction>(`/v1/transactions/${transactionId}/pause`, "POST", {
        reason,
      });
      toast.success(`Transaction #${transactionId} paused.`);
    });
  }

  async function resumeTransaction(transactionId: number): Promise<void> {
    await runRowAction(transactionId, "resume", async () => {
      await apiRequest<Transaction>(`/v1/transactions/${transactionId}/resume`, "POST", {});
      toast.success(`Transaction #${transactionId} resumed.`);
    });
  }

  async function stopTransaction(transactionId: number, reason: string): Promise<void> {
    await runRowAction(transactionId, "stop", async () => {
      await apiRequest<Transaction>(`/v1/transactions/${transactionId}/stop`, "POST", {
        reason: reason.trim() || null,
      });
      toast.success(`Transaction #${transactionId} stopped.`);
    });
  }

  async function deleteTransaction(transactionId: number): Promise<void> {
    await runRowAction(transactionId, "delete", async () => {
      await apiRequest<void>(`/v1/transactions/${transactionId}`, "DELETE");
      setTransactions((previous) => previous.filter((item) => item.id !== transactionId));
      toast.success(`Transaction #${transactionId} deleted.`);
    });
  }

  return {
    transactions,
    filters,
    setFilters,
    errorMessage,
    isLoading,
    isSubmitting,
    pendingRowActions,
    processingCount,
    successCount,
    loadTransactions,
    applyFilters,
    resetFilters,
    startTransaction,
    submitOtp,
    continueTransaction,
    checkTransaction,
    pauseTransaction,
    resumeTransaction,
    stopTransaction,
    deleteTransaction,
  };
}
