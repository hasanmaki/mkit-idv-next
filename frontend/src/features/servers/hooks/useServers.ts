import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";
import type {
  Server,
  ServerBulkCreateResult,
  ServerBulkPayload,
  ServerCreatePayload,
  ServerUpdatePayload,
} from "@/types/server";

import {
  defaultBulkForm,
  defaultSingleForm,
  toEditServerForm,
  type BulkServerForm,
  type EditServerForm,
  type SingleServerForm,
} from "../types";

export function useServers() {
  const [servers, setServers] = useState<Server[]>([]);
  const [selectedServerIds, setSelectedServerIds] = useState<number[]>([]);
  const [isLoadingServers, setIsLoadingServers] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  const [isSingleDialogOpen, setIsSingleDialogOpen] = useState(false);
  const [isBulkDialogOpen, setIsBulkDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isBulkDeleteConfirmOpen, setIsBulkDeleteConfirmOpen] = useState(false);

  const [singleForm, setSingleForm] = useState<SingleServerForm>(defaultSingleForm);
  const [bulkForm, setBulkForm] = useState<BulkServerForm>(defaultBulkForm);
  const [editForm, setEditForm] = useState<EditServerForm | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingServerId, setEditingServerId] = useState<number | null>(null);
  const [pendingDeleteServerId, setPendingDeleteServerId] = useState<number | null>(null);
  const [bulkResult, setBulkResult] = useState<ServerBulkCreateResult | null>(null);

  const totalActive = useMemo(
    () => servers.filter((server) => server.is_active).length,
    [servers],
  );
  const totalInactive = servers.length - totalActive;
  const selectedCount = selectedServerIds.length;
  const allSelected = servers.length > 0 && selectedServerIds.length === servers.length;

  useEffect(() => {
    void loadServers();
  }, []);

  function markRowAction(serverId: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [serverId]: action }));
  }

  function clearRowAction(serverId: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[serverId];
      return next;
    });
  }

  function upsertServer(nextServer: Server): void {
    setServers((previous) => {
      const idx = previous.findIndex((server) => server.id === nextServer.id);
      if (idx < 0) {
        return [nextServer, ...previous];
      }
      const cloned = [...previous];
      cloned[idx] = nextServer;
      return cloned;
    });
  }

  function removeServerFromState(serverId: number): void {
    setServers((previous) => previous.filter((server) => server.id !== serverId));
    setSelectedServerIds((previous) => previous.filter((id) => id !== serverId));
  }

  async function loadServers(): Promise<void> {
    try {
      setIsLoadingServers(true);
      setErrorMessage(null);
      const payload = await apiRequest<Server[]>("/v1/servers", "GET");
      setServers(payload);
      setSelectedServerIds((previous) =>
        previous.filter((id) => payload.some((server) => server.id === id)),
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat server list.");
    } finally {
      setIsLoadingServers(false);
    }
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedServerIds(checked ? servers.map((server) => server.id) : []);
  }

  function toggleSelectServer(serverId: number, checked: boolean): void {
    if (checked) {
      setSelectedServerIds((previous) => [...new Set([...previous, serverId])]);
      return;
    }
    setSelectedServerIds((previous) => previous.filter((id) => id !== serverId));
  }

  async function createSingleServer(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const normalizedHost = singleForm.host.trim().replace(/\/+$/, "");
      const payload: ServerCreatePayload = {
        port: singleForm.port,
        base_url: `${normalizedHost}:${singleForm.port}`,
        description: singleForm.description || null,
        timeout: singleForm.timeout,
        retries: singleForm.retries,
        wait_between_retries: singleForm.wait_between_retries,
        max_requests_queued: singleForm.max_requests_queued,
        is_active: singleForm.is_active,
        notes: singleForm.notes || null,
      };

      const created = await apiRequest<Server>("/v1/servers", "POST", payload);
      setSingleForm(defaultSingleForm);
      setIsSingleDialogOpen(false);
      upsertServer(created);
      toast.success("Server berhasil dibuat.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat server.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function buildBulkPayload(): ServerBulkPayload {
    return {
      ...bulkForm,
      base_host: bulkForm.base_host.trim().replace(/\/+$/, ""),
      description: bulkForm.description || null,
      notes: bulkForm.notes || null,
    };
  }

  async function runBulkDryRun(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const result = await apiRequest<ServerBulkCreateResult>(
        "/v1/servers/bulk/dry-run",
        "POST",
        buildBulkPayload(),
      );
      setBulkResult(result);
      toast.success("Dry run selesai.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Dry run gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createBulkServers(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const result = await apiRequest<ServerBulkCreateResult>(
        "/v1/servers/bulk",
        "POST",
        buildBulkPayload(),
      );
      setBulkResult(result);
      setIsBulkDialogOpen(false);
      const createdServers = result.items
        .filter((item) => item.server !== null && item.status === "created")
        .map((item) => item.server as Server);
      if (createdServers.length > 0) {
        setServers((previous) => {
          const mapById = new Map<number, Server>();
          for (const server of previous) {
            mapById.set(server.id, server);
          }
          for (const server of createdServers) {
            mapById.set(server.id, server);
          }
          return Array.from(mapById.values()).sort((a, b) => a.id - b.id);
        });
      }
      toast.success(
        `Bulk selesai. Created ${result.total_created}, skipped ${result.total_skipped}.`,
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk create gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function toggleServerStatus(server: Server): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(server.id, "toggle");
      const updated = await apiRequest<Server>(`/v1/servers/${server.id}/status`, "PATCH", {
        is_active: !server.is_active,
      });
      upsertServer(updated);
      toast.success(`Server #${server.id} ${updated.is_active ? "activated" : "deactivated"}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update status server #${server.id}.`);
    } finally {
      clearRowAction(server.id);
    }
  }

  function openEditServer(server: Server): void {
    setEditingServerId(server.id);
    setEditForm(toEditServerForm(server));
    setIsEditDialogOpen(true);
  }

  async function saveEditServer(): Promise<void> {
    if (!editingServerId || !editForm) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(editingServerId, "edit");
      const payload: ServerUpdatePayload = {
        description: editForm.description || null,
        timeout: editForm.timeout,
        retries: editForm.retries,
        wait_between_retries: editForm.wait_between_retries,
        max_requests_queued: editForm.max_requests_queued,
        is_active: editForm.is_active,
        notes: editForm.notes || null,
      };
      const updated = await apiRequest<Server>(
        `/v1/servers/${editingServerId}`,
        "PATCH",
        payload,
      );
      setIsEditDialogOpen(false);
      setEditingServerId(null);
      setEditForm(null);
      upsertServer(updated);
      toast.success(`Server #${editingServerId} berhasil diupdate.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update server #${editingServerId}.`);
    } finally {
      setIsSubmitting(false);
      if (editingServerId) {
        clearRowAction(editingServerId);
      }
    }
  }

  function openDeleteConfirm(serverId: number): void {
    setPendingDeleteServerId(serverId);
    setIsDeleteConfirmOpen(true);
  }

  async function performDeleteServer(serverId: number): Promise<void> {
    await apiRequest<void>(`/v1/servers/${serverId}`, "DELETE");
  }

  async function confirmDeleteSingle(): Promise<void> {
    if (!pendingDeleteServerId) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(pendingDeleteServerId, "delete");
      await performDeleteServer(pendingDeleteServerId);
      removeServerFromState(pendingDeleteServerId);
      setIsDeleteConfirmOpen(false);
      setPendingDeleteServerId(null);
      toast.success("Server berhasil dihapus.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal menghapus server.");
    } finally {
      setIsSubmitting(false);
      if (pendingDeleteServerId) {
        clearRowAction(pendingDeleteServerId);
      }
    }
  }

  async function confirmDeleteSelected(): Promise<void> {
    if (selectedServerIds.length === 0) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const failures: string[] = [];
      const deletedIds: number[] = [];
      for (const serverId of selectedServerIds) {
        try {
          markRowAction(serverId, "delete");
          await performDeleteServer(serverId);
          deletedIds.push(serverId);
        } catch (error) {
          failures.push(
            error instanceof Error
              ? `ID ${serverId}: ${error.message}`
              : `ID ${serverId}: unknown error`,
          );
        } finally {
          clearRowAction(serverId);
        }
      }
      setIsBulkDeleteConfirmOpen(false);
      for (const deletedId of deletedIds) {
        removeServerFromState(deletedId);
      }
      if (failures.length > 0) {
        setErrorMessage(`Sebagian delete gagal. ${failures.join(" | ")}`);
        toast.warning(`Delete selesai dengan ${failures.length} kegagalan.`);
      } else {
        toast.success(`Berhasil menghapus ${deletedIds.length} server.`);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk delete gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    servers,
    selectedServerIds,
    isLoadingServers,
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
    bulkResult,
    totalActive,
    totalInactive,
    selectedCount,
    allSelected,
    loadServers,
    toggleSelectAll,
    toggleSelectServer,
    createSingleServer,
    runBulkDryRun,
    createBulkServers,
    toggleServerStatus,
    openEditServer,
    saveEditServer,
    openDeleteConfirm,
    confirmDeleteSingle,
    confirmDeleteSelected,
  };
}
