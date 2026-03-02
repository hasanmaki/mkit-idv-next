import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";
import type { Session, SessionCreatePayload, SessionUpdatePayload } from "../types";

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSessionIds, setSelectedSessionIds] = useState<number[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingRowActions, setPendingRowActions] = useState<Record<number, string>>({});

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isBulkDeleteConfirmOpen, setIsBulkDeleteConfirmOpen] = useState(false);

  const [createForm, setCreateForm] = useState({
    name: "",
    email: "",
    description: "",
    is_active: true,
    notes: "",
  });
  const [editForm, setEditForm] = useState<{
    name: string;
    email: string;
    description: string | null;
    is_active: boolean;
    notes: string | null;
  } | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState<number | null>(null);
  const [pendingDeleteSessionId, setPendingDeleteSessionId] = useState<number | null>(null);

  const totalActive = useMemo(
    () => sessions.filter((session) => session.is_active).length,
    [sessions],
  );
  const totalInactive = sessions.length - totalActive;
  const selectedCount = selectedSessionIds.length;
  const allSelected = sessions.length > 0 && selectedSessionIds.length === sessions.length;

  useEffect(() => {
    void loadSessions();
  }, []);

  function markRowAction(sessionId: number, action: string): void {
    setPendingRowActions((previous) => ({ ...previous, [sessionId]: action }));
  }

  function clearRowAction(sessionId: number): void {
    setPendingRowActions((previous) => {
      const next = { ...previous };
      delete next[sessionId];
      return next;
    });
  }

  function upsertSession(nextSession: Session): void {
    setSessions((previous) => {
      const idx = previous.findIndex((session) => session.id === nextSession.id);
      if (idx < 0) {
        return [nextSession, ...previous];
      }
      const cloned = [...previous];
      cloned[idx] = nextSession;
      return cloned;
    });
  }

  function removeSessionFromState(sessionId: number): void {
    setSessions((previous) => previous.filter((session) => session.id !== sessionId));
    setSelectedSessionIds((previous) => previous.filter((id) => id !== sessionId));
  }

  async function loadSessions(): Promise<void> {
    try {
      setIsLoadingSessions(true);
      setErrorMessage(null);
      const payload = await apiRequest<Session[]>("/v1/sessions", "GET");
      setSessions(payload);
      setSelectedSessionIds((previous) =>
        previous.filter((id) => payload.some((session) => session.id === id)),
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat session list.");
    } finally {
      setIsLoadingSessions(false);
    }
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedSessionIds(checked ? sessions.map((session) => session.id) : []);
  }

  function toggleSelectSession(sessionId: number, checked: boolean): void {
    if (checked) {
      setSelectedSessionIds((previous) => [...new Set([...previous, sessionId])]);
      return;
    }
    setSelectedSessionIds((previous) => previous.filter((id) => id !== sessionId));
  }

  async function createSession(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const payload: SessionCreatePayload = {
        name: createForm.name.trim(),
        email: createForm.email.trim().toLowerCase(),
        description: createForm.description.trim() || null,
        is_active: createForm.is_active,
        notes: createForm.notes.trim() || null,
      };

      const created = await apiRequest<Session>("/v1/sessions", "POST", payload);
      setCreateForm({
        name: "",
        email: "",
        description: "",
        is_active: true,
        notes: "",
      });
      setIsCreateDialogOpen(false);
      upsertSession(created);
      toast.success("Session berhasil dibuat.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal membuat session.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function toggleSessionStatus(session: Session): Promise<void> {
    try {
      setErrorMessage(null);
      markRowAction(session.id, "toggle");
      const updated = await apiRequest<Session>(`/v1/sessions/${session.id}/status`, "PATCH", {
        is_active: !session.is_active,
      });
      upsertSession(updated);
      toast.success(`Session #${session.id} ${updated.is_active ? "activated" : "deactivated"}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update status session #${session.id}.`);
    } finally {
      clearRowAction(session.id);
    }
  }

  function openEditSession(session: Session): void {
    setEditingSessionId(session.id);
    setEditForm({
      name: session.name,
      email: session.email,
      description: session.description,
      is_active: session.is_active,
      notes: session.notes,
    });
    setIsEditDialogOpen(true);
  }

  async function saveEditSession(): Promise<void> {
    if (!editingSessionId || !editForm) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(editingSessionId, "edit");
      const payload: SessionUpdatePayload = {
        name: editForm.name.trim() || undefined,
        email: editForm.email.trim().toLowerCase() || undefined,
        description: editForm.description?.trim() ?? null,
        is_active: editForm.is_active,
        notes: editForm.notes?.trim() ?? null,
      };
      const updated = await apiRequest<Session>(
        `/v1/sessions/${editingSessionId}`,
        "PATCH",
        payload,
      );
      setIsEditDialogOpen(false);
      setEditingSessionId(null);
      setEditForm(null);
      upsertSession(updated);
      toast.success(`Session #${editingSessionId} berhasil diupdate.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Gagal update session #${editingSessionId}.`);
    } finally {
      setIsSubmitting(false);
      if (editingSessionId) {
        clearRowAction(editingSessionId);
      }
    }
  }

  function openDeleteConfirm(sessionId: number): void {
    setPendingDeleteSessionId(sessionId);
    setIsDeleteConfirmOpen(true);
  }

  async function performDeleteSession(sessionId: number): Promise<void> {
    await apiRequest<void>(`/v1/sessions/${sessionId}`, "DELETE");
  }

  async function confirmDeleteSingle(): Promise<void> {
    if (!pendingDeleteSessionId) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      markRowAction(pendingDeleteSessionId, "delete");
      await performDeleteSession(pendingDeleteSessionId);
      removeSessionFromState(pendingDeleteSessionId);
      setIsDeleteConfirmOpen(false);
      setPendingDeleteSessionId(null);
      toast.success("Session berhasil dihapus.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal menghapus session.");
    } finally {
      setIsSubmitting(false);
      if (pendingDeleteSessionId) {
        clearRowAction(pendingDeleteSessionId);
      }
    }
  }

  async function confirmDeleteSelected(): Promise<void> {
    if (selectedSessionIds.length === 0) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const failures: string[] = [];
      const deletedIds: number[] = [];
      for (const sessionId of selectedSessionIds) {
        try {
          markRowAction(sessionId, "delete");
          await performDeleteSession(sessionId);
          deletedIds.push(sessionId);
        } catch (error) {
          failures.push(
            error instanceof Error
              ? `ID ${sessionId}: ${error.message}`
              : `ID ${sessionId}: unknown error`,
          );
        } finally {
          clearRowAction(sessionId);
        }
      }
      setIsBulkDeleteConfirmOpen(false);
      for (const deletedId of deletedIds) {
        removeSessionFromState(deletedId);
      }
      if (failures.length > 0) {
        setErrorMessage(`Sebagian delete gagal. ${failures.join(" | ")}`);
        toast.warning(`Delete selesai dengan ${failures.length} kegagalan.`);
      } else {
        toast.success(`Berhasil menghapus ${deletedIds.length} session.`);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Bulk delete gagal.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    sessions,
    selectedSessionIds,
    isLoadingSessions,
    errorMessage,
    pendingRowActions,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    isDeleteConfirmOpen,
    setIsDeleteConfirmOpen,
    isBulkDeleteConfirmOpen,
    setIsBulkDeleteConfirmOpen,
    createForm,
    setCreateForm,
    editForm,
    setEditForm,
    isSubmitting,
    totalActive,
    totalInactive,
    selectedCount,
    allSelected,
    loadSessions,
    toggleSelectAll,
    toggleSelectSession,
    createSession,
    toggleSessionStatus,
    openEditSession,
    saveEditSession,
    openDeleteConfirm,
    confirmDeleteSingle,
    confirmDeleteSelected,
  };
}
