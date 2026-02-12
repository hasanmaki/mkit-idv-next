import { useEffect, useState } from "react";
import { toast } from "sonner";

import { apiRequest } from "@/lib/api";

import {
  defaultStartForm,
  type BindingOption,
  type OrchestrationControlPayload,
  type OrchestrationControlResult,
  type OrchestrationMonitorResult,
  type OrchestrationStatusResult,
  type StartForm,
} from "../types";

export function useOrchestration() {
  const [bindings, setBindings] = useState<BindingOption[]>([]);
  const [selectedBindingIds, setSelectedBindingIds] = useState<number[]>([]);
  const [startForm, setStartForm] = useState<StartForm>(defaultStartForm);
  const [statusResult, setStatusResult] = useState<OrchestrationStatusResult | null>(null);
  const [monitorResult, setMonitorResult] = useState<OrchestrationMonitorResult | null>(null);
  const [lastControlResult, setLastControlResult] = useState<OrchestrationControlResult | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [monitorUpdatedAt, setMonitorUpdatedAt] = useState<string | null>(null);
  const [statusUpdatedAt, setStatusUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    void loadBindings();
    void loadMonitor();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      if (document.visibilityState !== "visible") {
        return;
      }
      void loadMonitor();
      if (selectedBindingIds.length > 0) {
        void fetchStatus(selectedBindingIds);
      }
    }, 2500);
    return () => window.clearInterval(timer);
  }, [selectedBindingIds]);

  async function loadBindings(): Promise<void> {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const payload = await apiRequest<BindingOption[]>("/v1/bindings/view?active_only=true", "GET");
      setBindings(payload);
      setSelectedBindingIds((prev) => prev.filter((id) => payload.some((item) => item.id === id)));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat binding options.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadMonitor(): Promise<void> {
    try {
      const payload = await apiRequest<OrchestrationMonitorResult>("/v1/orchestration/monitor", "GET");
      setMonitorResult(payload);
      setMonitorUpdatedAt(new Date().toISOString());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat monitor orchestration.");
    }
  }

  function toggleSelectBinding(bindingId: number, checked: boolean): void {
    if (checked) {
      setSelectedBindingIds((prev) => [...new Set([...prev, bindingId])]);
      return;
    }
    setSelectedBindingIds((prev) => prev.filter((id) => id !== bindingId));
  }

  function toggleSelectAll(checked: boolean): void {
    setSelectedBindingIds(checked ? bindings.map((item) => item.id) : []);
  }

  async function runControl(
    action: "start" | "pause" | "resume" | "stop",
    payload: OrchestrationControlPayload | Record<string, unknown>,
  ): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const result = await apiRequest<OrchestrationControlResult>(
        `/v1/orchestration/${action}`,
        "POST",
        payload,
      );
      setLastControlResult(result);
      toast.success(`Orchestration ${action} executed.`);
      await loadMonitor();
      if (selectedBindingIds.length > 0) {
        await fetchStatus(selectedBindingIds);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error(`Orchestration ${action} gagal.`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function startSelected(): Promise<void> {
    const limitHarga = Number(startForm.limit_harga);
    const intervalMs = Number(startForm.interval_ms);
    const maxRetryStatus = Number(startForm.max_retry_status);
    const cooldownOnErrorMs = Number(startForm.cooldown_on_error_ms);
    if (
      selectedBindingIds.length === 0 ||
      !startForm.product_id.trim() ||
      !startForm.email.trim() ||
      !Number.isFinite(limitHarga)
    ) {
      return;
    }

    await runControl("start", {
      binding_ids: selectedBindingIds,
      product_id: startForm.product_id.trim(),
      email: startForm.email.trim(),
      limit_harga: limitHarga,
      interval_ms: Number.isFinite(intervalMs) ? intervalMs : 800,
      max_retry_status: Number.isFinite(maxRetryStatus) ? maxRetryStatus : 2,
      cooldown_on_error_ms: Number.isFinite(cooldownOnErrorMs) ? cooldownOnErrorMs : 1500,
    });
  }

  async function pauseSelected(reason?: string): Promise<void> {
    await runControl("pause", {
      binding_ids: selectedBindingIds,
      reason: reason ?? "manual_pause",
    });
  }

  async function resumeSelected(): Promise<void> {
    await runControl("resume", {
      binding_ids: selectedBindingIds,
    });
  }

  async function stopSelected(reason?: string): Promise<void> {
    await runControl("stop", {
      binding_ids: selectedBindingIds,
      reason: reason ?? "manual_stop",
    });
  }

  async function fetchStatus(bindingIds: number[]): Promise<void> {
    if (bindingIds.length === 0) {
      setStatusResult(null);
      return;
    }
    try {
      setErrorMessage(null);
      const result = await apiRequest<OrchestrationStatusResult>("/v1/orchestration/status", "POST", {
        binding_ids: bindingIds,
      });
      setStatusResult(result);
      setStatusUpdatedAt(new Date().toISOString());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
      toast.error("Gagal memuat status orchestration.");
    }
  }

  return {
    bindings,
    selectedBindingIds,
    startForm,
    setStartForm,
    statusResult,
    monitorResult,
    lastControlResult,
    isLoading,
    isSubmitting,
    errorMessage,
    monitorUpdatedAt,
    statusUpdatedAt,
    toggleSelectBinding,
    toggleSelectAll,
    loadBindings,
    loadMonitor,
    fetchStatus,
    startSelected,
    pauseSelected,
    resumeSelected,
    stopSelected,
  };
}
