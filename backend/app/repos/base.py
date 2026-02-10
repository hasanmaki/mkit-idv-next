"""base.py - Base repository with generic CRUD operations."""
# app/repos/base_repo.py

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):  # noqa: UP046
    """Base repository for CRUD operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Get by primary key."""
        return await db.get(self.model, id)

    async def get_by(self, db: AsyncSession, **filters) -> ModelType | None:
        """Get single by filters."""
        stmt = select(self.model).filter_by(**filters)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, **filters
    ) -> Sequence[ModelType]:
        """Get multiple with optional filters."""
        stmt = select(self.model).filter_by(**filters).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, commit: bool = False, **kwargs
    ) -> ModelType:
        """Create new record from kwargs (not tied to Pydantic)."""
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        await db.flush()
        if commit:
            await db.commit()
        else:
            await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, *, commit: bool = False, **kwargs
    ) -> ModelType:
        """Update record with kwargs."""
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        await db.flush()
        if commit:
            await db.commit()
        else:
            await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False
