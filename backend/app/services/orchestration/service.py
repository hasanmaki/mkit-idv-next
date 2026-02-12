"""Control service for orchestration runtime operations."""

from __future__ import annotations

from app.services.orchestration.registry import WorkerState
from app.services.orchestration.runtime import runtime, validate_binding_startable
from app.services.orchestration.schemas import (
    OrchestrationControlRequest,
    OrchestrationControlResult,
    OrchestrationItemResult,
    OrchestrationStartRequest,
    OrchestrationStatusItem,
    OrchestrationStatusResult,
)


class OrchestrationControlService:
    """Service wrapper for start/pause/resume/stop/status actions."""

    async def start(self, payload: OrchestrationStartRequest) -> OrchestrationControlResult:
        """Start worker loops for given bindings."""
        items: list[OrchestrationItemResult] = []
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

            ok, msg = await runtime.start_worker(
                binding_id,
                product_id=payload.product_id,
                email=payload.email,
                limit_harga=payload.limit_harga,
                interval_ms=payload.interval_ms,
                max_retry_status=payload.max_retry_status,
                cooldown_on_error_ms=payload.cooldown_on_error_ms,
            )
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )

        return OrchestrationControlResult(action="start", items=items)

    async def pause(self, payload: OrchestrationControlRequest) -> OrchestrationControlResult:
        """Pause selected workers."""
        items: list[OrchestrationItemResult] = []
        for binding_id in payload.binding_ids:
            ok, msg = await runtime.pause_worker(binding_id, payload.reason)
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )
        return OrchestrationControlResult(action="pause", items=items)

    async def resume(
        self, payload: OrchestrationControlRequest
    ) -> OrchestrationControlResult:
        """Resume selected workers."""
        items: list[OrchestrationItemResult] = []
        for binding_id in payload.binding_ids:
            ok, msg = await runtime.resume_worker(binding_id)
            items.append(
                OrchestrationItemResult(binding_id=binding_id, ok=ok, message=msg)
            )
        return OrchestrationControlResult(action="resume", items=items)

    async def stop(self, payload: OrchestrationControlRequest) -> OrchestrationControlResult:
        """Stop selected workers cooperatively."""
        items: list[OrchestrationItemResult] = []
        for binding_id in payload.binding_ids:
            ok, msg = await runtime.stop_worker(binding_id, payload.reason)
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
