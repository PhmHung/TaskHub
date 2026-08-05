from fastapi import APIRouter, Depends, status

from app.api.dependencies.common import get_pagination_params, get_task_filter_params
from app.api.dependencies.permissions import require_project_permission
from app.api.dependencies.services import get_task_service
from app.models import Project
from app.schemas.common import IPaginatedResponse
from app.schemas.task import TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "/{project_id}/tasks",
    response_model=IPaginatedResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Tasks for a Project",
)
async def get_tasks_for_project(
    project: Project = Depends(require_project_permission),
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_task_filter_params),
    service: TaskService = Depends(get_task_service),
):
    """
    Get a paginated and filtered list of tasks for a specific project.

    - You can filter tasks by **status**, **priority**, or **assignee_id**.
    - Pagination is controlled by **page** and **size**.
    """
    tasks = await service.get_tasks_by_project(
        project_id=project.id, **pagination, **filters
    )
    return tasks
