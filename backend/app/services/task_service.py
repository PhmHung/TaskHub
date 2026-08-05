import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.enums import TaskPriority, TaskStatus
from app.models import Label, Task, User
from app.repositories.comment_repository import comment_repo
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import workspace_repo
from app.schemas.common import IPaginatedResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    def __init__(
        self,
        db: AsyncSession,
        task_repo: TaskRepository | None = None,
        redis_client: Redis | None = None,
        user_repo: UserRepository | None = None,
    ):
        self.db = db
        self.task_repo = task_repo or TaskRepository()
        self.redis_client = redis_client
        self.user_repo = user_repo or UserRepository()

    async def create_task(
        self, *, task_in: TaskCreate, project_id: int, creator: User
    ) -> TaskResponse:
        task = await self.task_repo.create(
            self.db, obj_in=task_in, project_id=project_id, creator_id=creator.id
        )
        await self._invalidate_project_tasks_cache(project_id=project_id)
        return TaskResponse.model_validate(task)

    async def get_tasks_by_project(
        self,
        *,
        project_id: int,
        page: int,
        size: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> IPaginatedResponse[TaskResponse]:
        # Caching logic
        if self.redis_client:
            cache_key = (
                f"tasks:project:{project_id}:page:{page}:size:{size}"
                f":status:{status}:priority:{priority}:assignee:{assignee_id}"
            )
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return IPaginatedResponse[TaskResponse].model_validate_json(cached_data)

        # If not cached, fetch from DB
        tasks, total = await self.task_repo.get_multi_by_project(
            self.db,
            project_id=project_id,
            page=page,
            size=size,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )
        response = IPaginatedResponse(
            total=total,
            page=page,
            size=size,
            results=[TaskResponse.model_validate(task) for task in tasks],
        )

        # Store in cache
        if self.redis_client:
            await self.redis_client.set(
                cache_key, response.model_dump_json(), ex=3600  # Cache for 1 hour
            )

        return response

    async def _invalidate_project_tasks_cache(self, project_id: int):
        """Invalidates all task list caches for a given project."""
        if not self.redis_client:
            return

        # SCAN is preferred over KEYS in production to avoid blocking.
        # This will delete all cache entries for the project's task lists.
        async for key in self.redis_client.scan_iter(f"tasks:project:{project_id}:*"):
            await self.redis_client.delete(key)

    async def _check_is_workspace_member(self, user: User, task: Task):
        """
        Checks if the user is a member of the workspace containing the task.
        A user is considered a member if they are the workspace owner or listed
        in the workspace members with any role.
        """
        # Accessing task.project may trigger a lazy load if not already loaded by the caller.
        project = task.project
        if not project:
            raise exceptions.http_404_exc(
                f"Project with id {task.project_id} not found for the task."
            )

        # Get the workspace with its members to check for membership.
        workspace = await workspace_repo.get_by_id_with_details(
            self.db, workspace_id=project.workspace_id
        )
        if not workspace:
            raise exceptions.http_404_exc(
                f"Workspace with id {project.workspace_id} not found."
            )

        # Check if the user is the owner or a member.
        is_owner = workspace.owner_id == user.id
        is_member = any(member.user_id == user.id for member in workspace.members)

        if not (is_owner or is_member):
            raise exceptions.http_403_exc(
                "User does not have permission to access this task."
            )

    async def update_task(
        self, *, task: Task, task_in: TaskUpdate, user: User
    ) -> TaskResponse:
        """Updates a task after verifying permissions."""
        await self._check_is_workspace_member(user=user, task=task)

        # Validate assignee_id if provided and not None
        # We check if assignee_id is explicitly provided in the update payload.
        if task_in.assignee_id is not None:
            if task_in.assignee_id == 0:
                raise exceptions.http_400_exc("Assignee ID cannot be 0.")
            
            assignee = await self.user_repo.get_by_id(self.db, user_id=task_in.assignee_id)
            if not assignee:
                raise exceptions.http_404_exc(f"Assignee with ID {task_in.assignee_id} not found.")

        updated_task = await self.task_repo.update(self.db, db_obj=task, obj_in=task_in)

        await self._invalidate_project_tasks_cache(project_id=updated_task.project_id)

        return TaskResponse.model_validate(updated_task)

    async def delete_task(self, *, task: Task, user: User) -> None:
        """Deletes a task after verifying permissions."""
        await self._check_is_workspace_member(user=user, task=task)
        project_id = task.project_id

        await self.task_repo.delete(self.db, db_obj=task)

        # Invalidate cache
        await self._invalidate_project_tasks_cache(project_id=project_id)

    async def assign_label_to_task(
        self, *, task: Task, label: Label, user: User
    ) -> TaskResponse:
        """Assigns a label to a task after verifying permissions and business rules."""
        # 1. Permission Check: User must be a member of the project's workspace.
        await self._check_is_workspace_member(user=user, task=task)

        # 2. Business Logic: Ensure label and task are in the same project.
        if task.project_id != label.project_id:
            raise exceptions.http_400_exc(
                "Task and Label do not belong to the same project."
            )

        # 3. Idempotency: If label is already assigned, do nothing and return the task.
        # Accessing task.labels may trigger a lazy load.
        if label in task.labels:
            return TaskResponse.model_validate(task)

        # 4. Assign label and commit.
        task.labels.append(label)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        await self._invalidate_project_tasks_cache(project_id=task.project_id)

        return TaskResponse.model_validate(task)

    async def add_comment_to_task(
        self, *, task: Task, comment_in: CommentCreate, user: User
    ) -> CommentResponse:
        """Adds a comment to a task after verifying permissions."""
        # 1. Permission Check: User must be a member of the project's workspace.
        await self._check_is_workspace_member(user=user, task=task)

        # 2. Create comment using the repository.
        comment = await comment_repo.create(
            self.db, obj_in=comment_in, task_id=task.id, user_id=user.id
        )

        return CommentResponse.model_validate(comment)