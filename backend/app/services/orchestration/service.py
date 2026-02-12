"""Control service for orchestration runtime operations."""

from __future__ import annotations

from app.services.orchestration.registry import WorkerConfig, WorkerState
from app.services.orchestration.runtime import runtime, validate_binding_startable
from app.services.orchestration.schemas import (
    OrchestrationControlRequest,
    OrchestrationControlResult,
    OrchestrationItemResult,
    OrchestrationMonitorItem,
    OrchestrationMonitorResult,
    OrchestrationStartRequest,
    OrchestrationStatusItem,
    OrchestrationStatusResult,
)


class OrchestrationControlService:
    """Service wrapper for start/pause/resume/stop/status actions."""

    async def start(self, payload: OrchestrationStartRequest) -> OrchestrationControlResult:
        """Set selected bindings to running state and persist runtime config."""
        items: list[OrchestrationItemResult] = []
        registry = runtime.registry()
        for binding_id in payload.binding_ids:
            startable, reason = await validate_binding_startable(binding_id)
            if not startable:
                items.append(
                    OrchestrationItemResult(
                        binding_id=binding_id,
                        ok=False,
                        message=reason,
                    )
                )
                continue

            ok = await registry.start(
                binding_id,
                owner="controller",
                config=WorkerConfig(
                    interval_ms=payload.interval_ms,
                    max_retry_status=payload.max_retry_status,
                    cooldown_on_error_ms=payload.cooldown_on_error_ms,
                    extra={
                        "product_id": payload.product_id,
                        "email": payload.email,
                        "limit_harga": str(payload.limit_harga),
                    },
                ),
            )
            msg = "start_requested" if ok else "worker_already_running"
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )

        return OrchestrationControlResult(action="start", items=items)

    async def pause(self, payload: OrchestrationControlRequest) -> OrchestrationControlResult:
        """Pause selected workers."""
        items: list[OrchestrationItemResult] = []
        registry = runtime.registry()
        for binding_id in payload.binding_ids:
            ok = await registry.pause(binding_id, reason=payload.reason)
            msg = "pause_requested" if ok else "pause_failed"
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )
        return OrchestrationControlResult(action="pause", items=items)

    async def resume(
        self, payload: OrchestrationControlRequest
    ) -> OrchestrationControlResult:
        """Resume selected workers."""
        items: list[OrchestrationItemResult] = []
        registry = runtime.registry()
        for binding_id in payload.binding_ids:
            ok = await registry.resume(binding_id)
            msg = "resume_requested" if ok else "resume_failed"
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )
        return OrchestrationControlResult(action="resume", items=items)

    async def stop(self, payload: OrchestrationControlRequest) -> OrchestrationControlResult:
        """Stop selected workers cooperatively."""
        items: list[OrchestrationItemResult] = []
        registry = runtime.registry()
        for binding_id in payload.binding_ids:
            ok = await registry.stop(binding_id, reason=payload.reason)
            msg = "stop_requested" if ok else "stop_failed"
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )
        return OrchestrationControlResult(action="stop", items=items)

    async def status(self, binding_ids: list[int]) -> OrchestrationStatusResult:
        """Return worker status for selected bindings."""
        registry = runtime.registry()
        items: list[OrchestrationStatusItem] = []
        for binding_id in binding_ids:
            state = await registry.get_state(binding_id)
            if state is None:
                items.append(
                    OrchestrationStatusItem(
                        binding_id=binding_id,
                        state=WorkerState.IDLE,
                        reason="not_found",
                        owner=None,
                        updated_at=None,
                    )
                )
                continue
            items.append(
                OrchestrationStatusItem(
                    binding_id=binding_id,
                    state=state.state,
                    reason=state.reason,
                    owner=state.owner,
                    updated_at=state.updated_at.isoformat(),
                )
                )
        return OrchestrationStatusResult(items=items)

    async def monitor(self) -> OrchestrationMonitorResult:
        """Return lightweight monitor payload for all workers."""
        registry = runtime.registry()
        states = await registry.list_states()
        items: list[OrchestrationMonitorItem] = []
        active_workers = 0
        for state in states:
            heartbeat = await registry.get_heartbeat(state.binding_id)
            lock_owner = await registry.get_lock_owner(state.binding_id)
            if state.state in {WorkerState.RUNNING, WorkerState.PAUSED}:
                active_workers += 1
            items.append(
                OrchestrationMonitorItem(
                    binding_id=state.binding_id,
                    state=state.state,
                    reason=state.reason,
                    state_updated_at=state.updated_at.isoformat(),
                    lock_owner=lock_owner,
                    heartbeat_owner=heartbeat.owner if heartbeat else None,
                    heartbeat_cycle=heartbeat.cycle if heartbeat else None,
                    heartbeat_last_action=heartbeat.last_action if heartbeat else None,
                    heartbeat_updated_at=(
                        heartbeat.updated_at.isoformat() if heartbeat else None
                    ),
                )
            )

        return OrchestrationMonitorResult(
            total_workers=len(states),
            active_workers=active_workers,
            items=items,
        )
