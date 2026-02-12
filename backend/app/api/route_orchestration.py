"""API routes for orchestration runtime controls."""

from fastapi import APIRouter

from app.services.orchestration.schemas import (
    OrchestrationControlRequest,
    OrchestrationControlResult,
    OrchestrationMonitorResult,
    OrchestrationStartRequest,
    OrchestrationStatusResult,
)
from app.services.orchestration.service import OrchestrationControlService

router = APIRouter()


@router.post("/start", response_model=OrchestrationControlResult)
async def start_workers(payload: OrchestrationStartRequest) -> OrchestrationControlResult:
    """Start worker loops for selected bindings."""
    service = OrchestrationControlService()
    return await service.start(payload)


@router.post("/pause", response_model=OrchestrationControlResult)
async def pause_workers(payload: OrchestrationControlRequest) -> OrchestrationControlResult:
    """Pause selected workers."""
    service = OrchestrationControlService()
    return await service.pause(payload)


@router.post("/resume", response_model=OrchestrationControlResult)
async def resume_workers(payload: OrchestrationControlRequest) -> OrchestrationControlResult:
    """Resume selected workers."""
    service = OrchestrationControlService()
    return await service.resume(payload)


@router.post("/stop", response_model=OrchestrationControlResult)
async def stop_workers(payload: OrchestrationControlRequest) -> OrchestrationControlResult:
    """Request cooperative stop for selected workers."""
    service = OrchestrationControlService()
    return await service.stop(payload)


@router.post("/status", response_model=OrchestrationStatusResult)
async def get_status(payload: OrchestrationControlRequest) -> OrchestrationStatusResult:
    """Fetch worker status snapshot for selected bindings."""
    service = OrchestrationControlService()
    return await service.status(payload.binding_ids)


@router.get("/monitor", response_model=OrchestrationMonitorResult)
async def get_monitor() -> OrchestrationMonitorResult:
    """Fetch compact monitor payload for active workers and heartbeat."""
    service = OrchestrationControlService()
    return await service.monitor()
