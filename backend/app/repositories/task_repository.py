from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    async def get(self, db: AsyncSession, *, id: int) -> Task | None:
        statement = select(Task).where(Task.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, *, obj_in: TaskCreate, project_id: int, creator_id: int
    ) -> Task:
        db_obj = Task(**obj_in.model_dump(), project_id=project_id, creator_id=creator_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_project(
        self, db: AsyncSession, *, project_id: int, page: int = 1, size: int = 20
    ) -> tuple[list[Task], int]:
        """Get tasks for a project with pagination."""
        offset = (page - 1) * size

        items_query = (
            select(Task).where(Task.project_id == project_id).offset(offset).limit(size)
        )
        total_query = select(func.count()).select_from(Task).where(Task.project_id == project_id)

        items_result = await db.execute(items_query)
        total_result = await db.execute(total_query)

        items = list(items_result.scalars().all())
        total = total_result.scalar_one()

        return items, total

    async def update(
        self, db: AsyncSession, *, db_obj: Task, obj_in: TaskUpdate | dict
    ) -> Task:
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        )
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


task_repo = TaskRepository()