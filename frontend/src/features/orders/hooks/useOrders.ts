import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";
import type { Order, OrderCreatePayload } from "../types";

export function useOrders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrderIds, setSelectedOrderIds] = useState<number[]>([]);
  const [isLoadingOrders, setIsLoadingOrders] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isBulkDeleteConfirmOpen, setIsBulkDeleteConfirmOpen] = useState(false);

  const [createForm, setCreateForm] = useState({
    name: "",
    email: "",
    default_pin: "",
    msisdns: "",
    description: "",
    is_active: true,
    notes: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingDeleteOrderId, setPendingDeleteOrderId] = useState<number | null>(null);

  const totalActive = useMemo(
    () => orders.filter((order) => order.is_active).length,
    [orders],
  );
  const totalInactive = orders.length - totalActive;
  const selectedCount = selectedOrderIds.length;
  const allSelected = orders.length > 0 && selectedOrderIds.length === orders.length;

  useEffect(() => {
    void loadOrders();
  }, []);

  function markRowAction(orderId: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [orderId]: action }));
  }

  function clearRowAction(orderId: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[orderId];
      return next;
    });
  }

  function upsertOrder(nextOrder: Order): void {
    setOrders((previous) => {
      const idx = previous.findIndex((order) => order.id === nextOrder.id);
      if (idx < 0) {
        return [nextOrder, ...previous];
      }
      const cloned = [...previous];
      cloned[idx] = nextOrder;
      return cloned;
    });
  }

  function removeOrderFromState(orderId: number): void {
    setOrders((previous) => previous.filter((order) => order.id !== orderId));
    setSelectedOrderIds((previous) => previous.filter((id) => id !== orderId));
  }

  async function loadOrders(): Promise<void> {
    try {
      setIsLoadingOrders(true);
      setErrorMessage(null);
      const payload = await apiRequest<Order[]>("/v1/orders", "GET");
      setOrders(payload);
      setSelectedOrderIds((previous) =>
        previous.filter((id) => payload.some((order) => order.id === id)),
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat order list.");
    } finally {
      setIsLoadingOrders(false);
    }
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedOrderIds(checked ? orders.map((order) => order.id) : []);
  }

  function toggleSelectOrder(orderId: number, checked: boolean): void {
    if (checked) {
      setSelectedOrderIds((previous) => [...new Set([...previous, orderId])]);
      return;
    }
    setSelectedOrderIds((previous) => previous.filter((id) => id !== orderId));
  }

  async function createOrder(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      // Parse MSISDNs from comma-separated or newline-separated string
      const msisdnList = createForm.msisdns
        ? createForm.msisdns
            .split(/[\n,]+/)  // Split by newline OR comma
            .map((s) => s.trim())
            .filter((s) => s.length > 0)
        : undefined;

      const payload: OrderCreatePayload = {
        name: createForm.name.trim(),
        email: createForm.email.trim(),
        default_pin: createForm.default_pin || null,
        msisdns: msisdnList,
        description: createForm.description || null,
        is_active: createForm.is_active,
        notes: createForm.notes || null,
      };

      const created = await apiRequest<Order>("/v1/orders", "POST", payload);
      setCreateForm({
        name: "",
        email: "",
        default_pin: "",
        msisdns: "",
        description: "",
        is_active: true,
        notes: "",
      });
      setIsCreateDialogOpen(false);
      upsertOrder(created);
      toast.success("Order berhasil dibuat.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat order.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function openDeleteConfirm(orderId: number): void {
    setPendingDeleteOrderId(orderId);
    setIsDeleteConfirmOpen(true);
  }

  async function performDeleteOrder(orderId: number): Promise<void> {
    await apiRequest<void>(`/v1/orders/${orderId}`, "DELETE");
  }

  async function confirmDeleteSingle(): Promise<void> {
    if (!pendingDeleteOrderId) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(pendingDeleteOrderId, "delete");
      await performDeleteOrder(pendingDeleteOrderId);
      removeOrderFromState(pendingDeleteOrderId);
      setIsDeleteConfirmOpen(false);
      setPendingDeleteOrderId(null);
      toast.success("Order berhasil dihapus.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal menghapus order.");
    } finally {
      setIsSubmitting(false);
      if (pendingDeleteOrderId) {
        clearRowAction(pendingDeleteOrderId);
      }
    }
  }

  async function confirmDeleteSelected(): Promise<void> {
    if (selectedOrderIds.length === 0) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const failures: string[] = [];
      const deletedIds: number[] = [];
      for (const orderId of selectedOrderIds) {
        try {
          markRowAction(orderId, "delete");
          await performDeleteOrder(orderId);
          deletedIds.push(orderId);
        } catch (error) {
          failures.push(
            error instanceof Error
              ? `ID ${orderId}: ${error.message}`
              : `ID ${orderId}: unknown error`,
          );
        } finally {
          clearRowAction(orderId);
        }
      }
      setIsBulkDeleteConfirmOpen(false);
      for (const deletedId of deletedIds) {
        removeOrderFromState(deletedId);
      }
      if (failures.length > 0) {
        setErrorMessage(`Sebagian delete gagal. ${failures.join(" | ")}`);
        toast.warning(`Delete selesai dengan ${failures.length} kegagalan.`);
      } else {
        toast.success(`Berhasil menghapus ${deletedIds.length} order.`);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk delete gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function toggleOrderStatus(order: Order): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(order.id, "toggle");
      const updated = await apiRequest<Order>(`/v1/orders/${order.id}/status`, "PATCH", {
        is_active: !order.is_active,
      });
      upsertOrder(updated);
      toast.success(`Order #${order.id} ${updated.is_active ? "activated" : "deactivated"}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update status order #${order.id}.`);
    } finally {
      clearRowAction(order.id);
    }
  }

  return {
    orders,
    selectedOrderIds,
    isLoadingOrders,
    errorMessage,
    pendingRowActions,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isDeleteConfirmOpen,
    setIsDeleteConfirmOpen,
    isBulkDeleteConfirmOpen,
    setIsBulkDeleteConfirmOpen,
    createForm,
    setCreateForm,
    isSubmitting,
    totalActive,
    totalInactive,
    selectedCount,
    allSelected,
    loadOrders,
    toggleSelectAll,
    toggleSelectOrder,
    createOrder,
    openDeleteConfirm,
    confirmDeleteSingle,
    confirmDeleteSelected,
    toggleOrderStatus,
  };
}
