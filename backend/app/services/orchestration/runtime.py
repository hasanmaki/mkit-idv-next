"""Runtime worker loop manager for transaction orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from uuid import uuid4

from app.core.log_config import get_logger
from app.core.settings import get_app_settings
from app.database.session import sessionmanager
from app.models.bindings import Bindings
from app.models.steps import BindingStep
from app.models.transaction_statuses import TransactionStatus
from app.repos.binding_repo import BindingRepository
from app.services.orchestration.redis_registry import RedisWorkerRegistry
from app.services.orchestration.registry import (
    WorkerHeartbeat,
    WorkerState,
)
from app.services.transactions.schemas import TransactionStartRequest
from app.services.transactions.service import TransactionService

logger = get_logger("service.orchestration.runtime")


class OrchestrationRuntime:
    """In-process runtime manager backed by Redis shared state."""

    def __init__(self, registry_factory: Callable[[], RedisWorkerRegistry]):
        self._registry_factory = registry_factory
        self._tasks: dict[int, asyncio.Task[None]] = {}
        self._task_lock = asyncio.Lock()
        self._instance_id = uuid4().hex[:8]

    def registry(self) -> RedisWorkerRegistry:
        """Return a new registry instance from configured factory."""
        return self._registry_factory()

    async def ensure_local_worker(self, binding_id: int) -> bool:
        """Ensure a local task exists for a running/paused binding."""
        async with self._task_lock:
            existing = self._tasks.get(binding_id)
            if existing and not existing.done():
                return False

            owner = self._owner(binding_id)
            task = asyncio.create_task(self._worker_loop(binding_id=binding_id, owner=owner))
            self._tasks[binding_id] = task
            return True

    async def tick(self) -> None:
        """One reconcile cycle: spawn local workers for RUNNING/PAUSED states."""
        registry = self._registry_factory()
        states = await registry.list_states()
        for state in states:
            if state.state in {WorkerState.RUNNING, WorkerState.PAUSED}:
                await self.ensure_local_worker(state.binding_id)

    async def run_forever(self, interval_seconds: float = 1.0) -> None:
        """Run reconcile loop forever."""
        while True:
            try:
                await self.tick()
            except Exception:
                logger.exception("Orchestrator tick failed")
            await asyncio.sleep(interval_seconds)

    async def _worker_loop(self, *, binding_id: int, owner: str) -> None:
        """Run transaction cycles for one binding until stopped."""
        registry = self._registry_factory()
        lock_ok = await registry.acquire_lock(binding_id, owner=owner)
        if not lock_ok:
            async with self._task_lock:
                self._tasks.pop(binding_id, None)
            return

        cycle = 0
        try:
            cfg = await registry.get_config(binding_id)
            if cfg is None:
                await registry.stop(binding_id, reason="missing_worker_config")
                return
            while True:
                state_record = await registry.get_state(binding_id)
                if state_record is None:
                    break
                if state_record.state == WorkerState.STOPPED:
                    break

                await registry.refresh_lock(binding_id, owner=owner)
                await registry.heartbeat(
                    WorkerHeartbeat(
                        binding_id=binding_id,
                        owner=owner,
                        cycle=cycle,
                        last_action=f"state:{state_record.state.value}",
                        updated_at=state_record.updated_at,
                    )
                )

                if state_record.state == WorkerState.PAUSED:
                    await asyncio.sleep(0.5)
                    continue

                try:
                    result_status, result_error = await self._run_single_cycle(
                        binding_id=binding_id,
                        product_id=cfg.extra.get("product_id", ""),
                        email=cfg.extra.get("email", ""),
                        limit_harga=int(cfg.extra.get("limit_harga", "0")),
                    )
                    if (
                        result_status == TransactionStatus.GAGAL
                        and result_error
                        and "insufficient_balance_before_start" in result_error
                    ):
                        await registry.stop(binding_id, reason=result_error)
                        break
                except Exception as exc:
                    logger.exception(
                        "Worker cycle failed",
                        extra={"binding_id": binding_id, "owner": owner},
                    )
                    await registry.heartbeat(
                        WorkerHeartbeat(
                            binding_id=binding_id,
                            owner=owner,
                            cycle=cycle,
                            last_action=f"cycle_error:{exc.__class__.__name__}",
                            updated_at=state_record.updated_at,
                        )
                    )
                    await asyncio.sleep(cfg.cooldown_on_error_ms / 1000)
                    continue

                cycle += 1
                state_after = await registry.get_state(binding_id)
                if state_after and state_after.state == WorkerState.STOPPED:
                    break
                await asyncio.sleep(cfg.interval_ms / 1000)
        finally:
            await registry.release_lock(binding_id, owner=owner)
            async with self._task_lock:
                self._tasks.pop(binding_id, None)

    async def _run_single_cycle(
        self, *, binding_id: int, product_id: str, email: str, limit_harga: int
    ) -> tuple[TransactionStatus, str | None]:
        """Run one start/check cycle and return final status/error."""
        async with sessionmanager.session() as session:
            trx_service = TransactionService(session)
            trx = await trx_service.start_transaction(
                TransactionStartRequest(
                    binding_id=binding_id,
                    product_id=product_id,
                    email=email,
                    limit_harga=limit_harga,
                )
            )
            await session.commit()

        if trx.status == TransactionStatus.PROCESSING:
            async with sessionmanager.session() as session:
                trx_service = TransactionService(session)
                updated_trx, _ = await trx_service.check_balance_and_continue_or_stop(trx.id)
                await session.commit()
                return updated_trx.status, updated_trx.error_message

        return trx.status, trx.error_message

    def _owner(self, binding_id: int) -> str:
        """Build unique owner token for this process and binding."""
        return f"{self._instance_id}:{binding_id}"


def build_runtime() -> OrchestrationRuntime:
    """Build orchestration runtime with Redis registry factory."""
    settings = get_app_settings()

    def _registry_factory() -> RedisWorkerRegistry:
        return RedisWorkerRegistry.from_url(settings.redis)

    return OrchestrationRuntime(registry_factory=_registry_factory)


runtime = build_runtime()


async def validate_binding_startable(binding_id: int) -> tuple[bool, str]:
    """Validate binding eligibility before worker start."""
    async with sessionmanager.session() as session:
        repo = BindingRepository(Bindings)
        binding = await repo.get(session, binding_id)
        if not binding:
            return False, "binding_not_found"
        if binding.unbound_at is not None:
            return False, "binding_logged_out"
        if binding.step != BindingStep.TOKEN_LOGIN_FETCHED:
            return False, "binding_step_not_ready"
    return True, "ok"
