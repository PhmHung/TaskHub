from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.task_repository import TaskRepository
from app.schemas.common import IPaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse


class TaskService:
    def __init__(self, db: AsyncSession, task_repo: TaskRepository | None = None):
        self.db = db
        self.task_repo = task_repo or TaskRepository()

    async def create_task(
        self, *, task_in: TaskCreate, project_id: int, creator: User
    ) -> TaskResponse:
        task = await self.task_repo.create(
            self.db, obj_in=task_in, project_id=project_id, creator_id=creator.id
        )
        return TaskResponse.model_validate(task)

    async def get_tasks_by_project(
        self, *, project_id: int, page: int, size: int
    ) -> IPaginatedResponse[TaskResponse]:
        tasks, total = await self.task_repo.get_multi_by_project(
            self.db, project_id=project_id, page=page, size=size
        )
        return IPaginatedResponse(
            total=total,
            page=page,
            size=size,
            results=[TaskResponse.model_validate(task) for task in tasks],
        )