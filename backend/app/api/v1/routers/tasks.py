from fastapi import APIRouter, Depends, status

from app.api.dependencies.dependency import get_current_user
from app.api.dependencies.resources import (
    get_comment_by_id,
    get_label_by_id,
    get_task_by_id,
)
from app.api.dependencies.services import get_task_service
from app.core import responses
from app.models import Comment, Label, Task, User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.task import TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign Label to Task",
    responses={
        **responses.PROTECTED_RESPONSES,
        status.HTTP_400_BAD_REQUEST: {"description": "Task and Label do not belong to the same project."},
        **responses.TASK_NOT_FOUND,
        **responses.LABEL_NOT_FOUND,
    },
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


@router.delete(
    "/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove Label from Task",
    responses={
        **responses.PROTECTED_RESPONSES,
        status.HTTP_400_BAD_REQUEST: {"description": "Task and Label do not belong to the same project."},
        **responses.TASK_NOT_FOUND,
        **responses.LABEL_NOT_FOUND,
    },
)
async def remove_label_from_task(
    task: Task = Depends(get_task_by_id),
    label: Label = Depends(get_label_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Removes a label from a specific task.

    - User must be a member of the project to which the task belongs.
    - The label must belong to the same project as the task.
    """
    return await service.remove_label_from_task(
        task=task, label=label, user=current_user
    )


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Comment to Task",
    responses={
        **responses.PROTECTED_RESPONSES,
        **responses.TASK_NOT_FOUND,
    },
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


@router.delete(
    "/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Comment from Task",
    responses={
        **responses.PROTECTED_RESPONSES,
        status.HTTP_400_BAD_REQUEST: {"description": "Comment does not belong to the specified task."},
        **responses.TASK_NOT_FOUND,
    },
)
async def delete_comment_from_task(
    task: Task = Depends(get_task_by_id),
    comment: Comment = Depends(get_comment_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Deletes a comment from a specific task.

    - User must be the author of the comment.
    """
    await service.delete_comment(task=task, comment=comment, user=current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a Task",
    responses={
        **responses.PROTECTED_RESPONSES,
        **responses.TASK_NOT_FOUND,
        **responses.USER_NOT_FOUND,
        status.HTTP_400_BAD_REQUEST: {"description": "Assignee ID cannot be 0."},
    },
)
async def update_task(
    task_in: TaskUpdate,
    task: Task = Depends(get_task_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Updates a task.

    - User must be a member of the project to which the task belongs.
    """
    return await service.update_task(task=task, task_in=task_in, user=current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Task",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Task deleted successfully"},
        **responses.PROTECTED_RESPONSES,
        **responses.TASK_NOT_FOUND,
    },
)
async def delete_task(
    task: Task = Depends(get_task_by_id),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    """
    Deletes a task.

    - User must be a member of the project to which the task belongs.
    """
    await service.delete_task(task=task, user=current_user)
