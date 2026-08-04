from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Label
from app.schemas.label import LabelCreate, LabelUpdate


class LabelRepository:
    """
    Repository for label-related database operations.
    """

    async def get(self, db: AsyncSession, *, id: int) -> Label | None:
        """Get a label by its ID."""
        statement = select(Label).where(Label.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, *, obj_in: LabelCreate, project_id: int
    ) -> Label:
        """Create a new label."""
        db_obj = Label(**obj_in.model_dump(), project_id=project_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_project(
        self, db: AsyncSession, *, project_id: int
    ) -> list[Label]:
        """Get all labels for a specific project."""
        statement = select(Label).where(Label.project_id == project_id).order_by(Label.name)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, *, db_obj: Label, obj_in: LabelUpdate | dict
    ) -> Label:
        """Update a label."""
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        )
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> None:
        """Delete a label by its ID."""
        db_obj = await self.get(db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()


label_repo = LabelRepository()