from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.task_priority import TaskPriority
from app.enums.task_status import TaskStatus


class TaskBase(BaseModel):
    name: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)