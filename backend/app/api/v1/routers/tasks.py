from fastapi import APIRouter, Depends, status

from app.api.dependencies.dependency import get_current_user
from app.api.dependencies.resources import get_label_by_id, get_task_by_id
from app.api.dependencies.services import get_task_service
from app.models import Label, Task, User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.task import TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign Label to Task",
)
async def assign_label_to_task(
    task: Task = Depends(get_task_by_id),
    label: Label = Depends(get_label_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Assigns a label to a specific task.

    - User must be a member of the project to which the task belongs.
    - The label must belong to the same project as the task.
    """
    return await service.assign_label_to_task(
        task=task, label=label, user=current_user
    )


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Comment to Task",
)
async def add_comment_to_task(
    comment_in: CommentCreate,
    task: Task = Depends(get_task_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Adds a comment to a specific task.

    - User must be a member of the project to which the task belongs.
    """
    return await service.add_comment_to_task(
        task=task, comment_in=comment_in, user=current_user
    )
