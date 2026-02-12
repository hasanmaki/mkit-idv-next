"""Schemas for orchestration control APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.services.orchestration.registry import WorkerState


class OrchestrationStartRequest(BaseModel):
    """Start worker loops for selected bindings."""

    binding_ids: list[int] = Field(..., min_length=1, examples=[[1, 2, 3]])
    product_id: str = Field(..., examples=["650"])
    email: str = Field(..., examples=["user@example.com"])
    limit_harga: int = Field(..., examples=[100000])
    interval_ms: int = Field(800, ge=100, le=60000, examples=[800])
    max_retry_status: int = Field(2, ge=0, le=10, examples=[2])
    cooldown_on_error_ms: int = Field(1500, ge=100, le=120000, examples=[1500])


class OrchestrationControlRequest(BaseModel):
    """Pause/resume/stop workers by binding IDs."""

    binding_ids: list[int] = Field(..., min_length=1, examples=[[1, 2]])
    reason: str | None = Field(None, examples=["manual_stop"])


class OrchestrationItemResult(BaseModel):
    """Per-binding control action result."""

    binding_id: int
    ok: bool
    message: str


class OrchestrationControlResult(BaseModel):
    """Control action result payload."""

    action: str
    items: list[OrchestrationItemResult]


class OrchestrationStatusItem(BaseModel):
    """Runtime worker status snapshot."""

    binding_id: int
    state: WorkerState
    reason: str | None = None
    owner: str | None = None
    updated_at: str | None = None


class OrchestrationStatusResult(BaseModel):
    """Response for status query."""

    items: list[OrchestrationStatusItem]

