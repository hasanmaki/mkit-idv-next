"""Worker registry contracts for transaction orchestration runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class WorkerState(StrEnum):
    """Runtime state of a binding worker."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass(slots=True)
class WorkerConfig:
    """Configuration attached to a worker."""

    interval_ms: int
    max_retry_status: int
    cooldown_on_error_ms: int
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class WorkerStateRecord:
    """Persisted worker state snapshot."""

    binding_id: int
    state: WorkerState
    reason: str | None
    updated_at: datetime
    owner: str | None = None


@dataclass(slots=True)
class WorkerHeartbeat:
    """Worker heartbeat payload."""

    binding_id: int
    owner: str
    cycle: int
    last_action: str
    updated_at: datetime


class WorkerRegistry(Protocol):
    """Abstraction for orchestration worker runtime state and locking."""

    async def start(
        self, binding_id: int, *, owner: str, config: WorkerConfig
    ) -> bool:
        """Set worker state to running and store config."""

    async def pause(self, binding_id: int, *, reason: str | None = None) -> bool:
        """Set worker state to paused."""

    async def resume(self, binding_id: int) -> bool:
        """Set worker state to running from paused state."""

    async def stop(self, binding_id: int, *, reason: str | None = None) -> bool:
        """Set worker state to stopped."""

    async def get_state(self, binding_id: int) -> WorkerStateRecord | None:
        """Return current state record for binding worker."""

    async def get_config(self, binding_id: int) -> WorkerConfig | None:
        """Return worker config for binding."""

    async def acquire_lock(self, binding_id: int, *, owner: str) -> bool:
        """Acquire distributed lock for worker ownership."""

    async def refresh_lock(self, binding_id: int, *, owner: str) -> bool:
        """Extend lock ttl if lock is still owned."""

    async def release_lock(self, binding_id: int, *, owner: str) -> bool:
        """Release lock only when owned by caller."""

    async def heartbeat(self, payload: WorkerHeartbeat) -> None:
        """Persist heartbeat for runtime liveness tracking."""

