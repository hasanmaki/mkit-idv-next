"""Redis-backed worker registry implementation."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from redis.asyncio import Redis

from app.core.settings import RedisConfig
from app.services.orchestration.registry import (
    WorkerConfig,
    WorkerHeartbeat,
    WorkerState,
    WorkerStateRecord,
)


class RedisWorkerRegistry:
    """Redis implementation of worker runtime state and lock coordination."""

    def __init__(self, redis: Redis, config: RedisConfig):
        self.redis = redis
        self.config = config

    @classmethod
    def from_url(cls, config: RedisConfig) -> RedisWorkerRegistry:
        """Create registry from Redis URL config."""
        redis = Redis.from_url(config.url, decode_responses=True)
        return cls(redis=redis, config=config)

    async def start(
        self, binding_id: int, *, owner: str, config: WorkerConfig
    ) -> bool:
        """Set worker state to running and persist worker config."""
        state_key = self._state_key(binding_id)
        cfg_key = self._config_key(binding_id)
        now = self._now_iso()

        previous = await self.redis.hget(state_key, "state")
        if previous == WorkerState.RUNNING.value:
            return False

        await self.redis.hset(
            state_key,
            mapping={
                "binding_id": str(binding_id),
                "state": WorkerState.RUNNING.value,
                "reason": "",
                "updated_at": now,
                "owner": owner,
            },
        )
        await self.redis.hset(
            cfg_key,
            mapping={
                "interval_ms": str(config.interval_ms),
                "max_retry_status": str(config.max_retry_status),
                "cooldown_on_error_ms": str(config.cooldown_on_error_ms),
                "extra_json": json.dumps(config.extra),
            },
        )
        return True

    async def pause(self, binding_id: int, *, reason: str | None = None) -> bool:
        """Set worker state to paused."""
        return await self._set_state(
            binding_id, WorkerState.PAUSED, reason=reason or "manual_pause"
        )

    async def resume(self, binding_id: int) -> bool:
        """Set worker state to running."""
        return await self._set_state(binding_id, WorkerState.RUNNING, reason=None)

    async def stop(self, binding_id: int, *, reason: str | None = None) -> bool:
        """Set worker state to stopped."""
        return await self._set_state(
            binding_id, WorkerState.STOPPED, reason=reason or "manual_stop"
        )

    async def get_state(self, binding_id: int) -> WorkerStateRecord | None:
        """Return current worker state record."""
        raw = await self.redis.hgetall(self._state_key(binding_id))
        if not raw:
            return None

        state_value = raw.get("state", WorkerState.IDLE.value)
        reason_value = raw.get("reason") or None
        updated_at_raw = raw.get("updated_at")
        owner = raw.get("owner") or None
        parsed_updated_at = self._parse_datetime(updated_at_raw)

        return WorkerStateRecord(
            binding_id=binding_id,
            state=WorkerState(state_value),
            reason=reason_value,
            updated_at=parsed_updated_at,
            owner=owner,
        )

    async def get_config(self, binding_id: int) -> WorkerConfig | None:
        """Return worker config for binding."""
        raw = await self.redis.hgetall(self._config_key(binding_id))
        if not raw:
            return None

        extra_json = raw.get("extra_json", "{}")
        try:
            extra = json.loads(extra_json)
            if not isinstance(extra, dict):
                extra = {}
        except json.JSONDecodeError:
            extra = {}

        return WorkerConfig(
            interval_ms=int(raw.get("interval_ms", "500")),
            max_retry_status=int(raw.get("max_retry_status", "2")),
            cooldown_on_error_ms=int(raw.get("cooldown_on_error_ms", "1500")),
            extra={str(k): str(v) for k, v in extra.items()},
        )

    async def acquire_lock(self, binding_id: int, *, owner: str) -> bool:
        """Acquire worker lock with ttl."""
        lock_key = self._lock_key(binding_id)
        acquired = await self.redis.set(
            lock_key,
            owner,
            ex=self.config.lock_ttl_seconds,
            nx=True,
        )
        return bool(acquired)

    async def refresh_lock(self, binding_id: int, *, owner: str) -> bool:
        """Refresh lock ttl only when caller owns current lock."""
        lua = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
          return redis.call('EXPIRE', KEYS[1], ARGV[2])
        else
          return 0
        end
        """
        refreshed = await self.redis.eval(
            lua,
            1,
            self._lock_key(binding_id),
            owner,
            str(self.config.lock_ttl_seconds),
        )
        return bool(refreshed)

    async def release_lock(self, binding_id: int, *, owner: str) -> bool:
        """Release lock only when caller owns current lock."""
        lua = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
          return redis.call('DEL', KEYS[1])
        else
          return 0
        end
        """
        deleted = await self.redis.eval(lua, 1, self._lock_key(binding_id), owner)
        return bool(deleted)

    async def heartbeat(self, payload: WorkerHeartbeat) -> None:
        """Persist worker heartbeat with ttl."""
        key = self._heartbeat_key(payload.binding_id)
        await self.redis.hset(
            key,
            mapping={
                "binding_id": str(payload.binding_id),
                "owner": payload.owner,
                "cycle": str(payload.cycle),
                "last_action": payload.last_action,
                "updated_at": payload.updated_at.astimezone(UTC).isoformat(),
            },
        )
        await self.redis.expire(key, self.config.heartbeat_ttl_seconds)

    async def get_lock_owner(self, binding_id: int) -> str | None:
        """Return lock owner string for binding."""
        owner = await self.redis.get(self._lock_key(binding_id))
        return owner if owner else None

    async def get_heartbeat(self, binding_id: int) -> WorkerHeartbeat | None:
        """Return last heartbeat payload for binding."""
        raw = await self.redis.hgetall(self._heartbeat_key(binding_id))
        if not raw:
            return None
        return WorkerHeartbeat(
            binding_id=binding_id,
            owner=raw.get("owner", ""),
            cycle=int(raw.get("cycle", "0")),
            last_action=raw.get("last_action", ""),
            updated_at=self._parse_datetime(raw.get("updated_at")),
        )

    async def list_states(self) -> list[WorkerStateRecord]:
        """List all worker state records stored in Redis."""
        items: list[WorkerStateRecord] = []
        async for key in self.redis.scan_iter(match="wrk:state:*", count=200):
            raw = await self.redis.hgetall(key)
            if not raw:
                continue
            binding_raw = raw.get("binding_id")
            if not binding_raw:
                continue
            binding_id = int(binding_raw)
            items.append(
                WorkerStateRecord(
                    binding_id=binding_id,
                    state=WorkerState(raw.get("state", WorkerState.IDLE.value)),
                    reason=raw.get("reason") or None,
                    updated_at=self._parse_datetime(raw.get("updated_at")),
                    owner=raw.get("owner") or None,
                )
            )
        items.sort(key=lambda item: item.binding_id)
        return items

    async def _set_state(
        self, binding_id: int, state: WorkerState, *, reason: str | None
    ) -> bool:
        """Upsert worker state to target value."""
        state_key = self._state_key(binding_id)
        await self.redis.hset(
            state_key,
            mapping={
                "binding_id": str(binding_id),
                "state": state.value,
                "reason": reason or "",
                "updated_at": self._now_iso(),
            },
        )
        return True

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime:
        """Parse datetime from iso format with UTC fallback."""
        if not value:
            return datetime.now(UTC)
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.now(UTC)

    @staticmethod
    def _now_iso() -> str:
        """Return current UTC timestamp as ISO string."""
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _state_key(binding_id: int) -> str:
        return f"wrk:state:{binding_id}"

    @staticmethod
    def _config_key(binding_id: int) -> str:
        return f"wrk:cfg:{binding_id}"

    @staticmethod
    def _lock_key(binding_id: int) -> str:
        return f"wrk:lock:{binding_id}"

    @staticmethod
    def _heartbeat_key(binding_id: int) -> str:
        return f"wrk:hb:{binding_id}"
