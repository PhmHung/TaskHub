from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enums import TaskPriority, TaskStatus
from app.models.tasks import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    async def get(self, db: AsyncSession, *, id: int) -> Task | None:
        statement = select(Task).where(Task.id == id).options(
            joinedload(Task.project),  # Eagerly load the project relationship
            joinedload(Task.labels),   # Eagerly load the labels relationship
        )
        result = await db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def create(
        self, db: AsyncSession, *, obj_in: TaskCreate, project_id: int, creator_id: int
    ) -> Task:
        db_obj = Task(**obj_in.model_dump(), project_id=project_id, creator_id=creator_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        page: int = 1,
        size: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> tuple[list[Task], int]:
        """Get tasks for a project with pagination and filtering."""
        offset = (page - 1) * size

        # Base query for both items and total count
        base_query = select(Task).where(Task.project_id == project_id)

        # Apply filters
        if status:
            base_query = base_query.where(Task.status == status)
        if priority:
            base_query = base_query.where(Task.priority == priority)
        if assignee_id is not None:
            base_query = base_query.where(Task.assignee_id == assignee_id)

        # Query for paginated items
        items_query = base_query.order_by(Task.created_at.desc()).offset(offset).limit(size)
        items_result = await db.execute(items_query)
        items = list(items_result.scalars().all())

        # Query for total count with the same filters
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
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

    async def delete(self, db: AsyncSession, *, db_obj: Task) -> Task:
        await db.delete(db_obj)
        await db.commit()
        return db_obj


task_repo = TaskRepository()