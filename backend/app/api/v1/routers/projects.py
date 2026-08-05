from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.dependency import get_current_user, get_db
from app.api.dependencies.common import get_pagination_params, get_task_filter_params
from app.api.dependencies.permissions import (
    require_project_permission,
    require_workspace_editor_role,
    require_workspace_viewer_role,
)
from app.api.dependencies.resources import get_project_by_id
from app.api.dependencies.services import get_project_service, get_task_service
from app.core import responses
from app.core import exceptions
from app.enums.workspace_role import WorkspaceRole
from app.models import Project, User
from app.repositories.project_repository import project_repo
from app.repositories.workspace_repository import workspace_repo
from app.schemas import project as project_schema
from app.schemas.common import IPaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/projects",
    response_model=project_schema.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.PROTECTED_RESPONSES,
        **responses.WORKSPACE_NOT_FOUND,
        **responses.CONFLICT,
    },
)
async def create_project(
    workspace_id: int,
    project_in: project_schema.ProjectCreate,
    current_user: User = Depends(require_workspace_editor_role),
    service: ProjectService = Depends(get_project_service),
):
    """
    Create a new project within a workspace. User must be an owner or editor.
    """
    # Delegate the creation and duplicate name check to the service layer
    return await service.create_project(
        project_in=project_in, owner=current_user, workspace_id=workspace_id
    )


@router.get(
    "/workspaces/{workspace_id}/projects",
    response_model=list[project_schema.ProjectResponse],
    responses={
        **responses.PROTECTED_RESPONSES,
        **responses.WORKSPACE_NOT_FOUND,
    },
)
async def get_workspace_projects(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_workspace_viewer_role),
):
    """
    Get all non-archived projects for a workspace. User must be a member of the workspace.
    """
    return await project_repo.get_projects_by_workspace(db, workspace_id=workspace_id)


@router.get(
    "/projects/{project_id}",
    response_model=project_schema.ProjectResponse,
    responses={**responses.PROTECTED_RESPONSES, **responses.PROJECT_NOT_FOUND},
)
async def get_project(
    project: Project = Depends(require_project_permission),
):
    """
    Get a project by ID. User must have permission in the project's workspace.
    """
    return project


@router.put(
    "/projects/{project_id}",
    response_model=project_schema.ProjectResponse,
    responses={**responses.PROTECTED_RESPONSES, **responses.PROJECT_NOT_FOUND},
)
async def update_project(
    project_in: project_schema.ProjectUpdate,
    project: Project = Depends(require_project_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a project. User must be project owner or workspace editor/owner.
    """
    return await project_repo.update(db, db_obj=project, obj_in=project_in)


@router.patch(
    "/projects/{project_id}/archive",
    response_model=project_schema.ProjectResponse,
    responses={**responses.PROTECTED_RESPONSES, **responses.PROJECT_NOT_FOUND},
)
async def archive_project(
    project: Project = Depends(require_project_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Archive a project.
    """
    return await project_repo.update(db, db_obj=project, obj_in={"is_archived": True})


@router.patch(
    "/projects/{project_id}/unarchive",
    response_model=project_schema.ProjectResponse,
    responses={**responses.PROTECTED_RESPONSES, **responses.PROJECT_NOT_FOUND},
)
async def unarchive_project(
    project: Project = Depends(require_project_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Unarchive a project.
    """
    return await project_repo.update(db, db_obj=project, obj_in={"is_archived": False})


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Project deleted successfully"},
        **responses.PROTECTED_RESPONSES,
        **responses.PROJECT_NOT_FOUND,
    },
)
async def delete_project(
    project: Project = Depends(get_project_by_id),
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    """
    Delete a project. Only project owner or workspace owner can delete.
    """
    # Delegate all logic, including authorization, to the service layer.
    await service.delete_project(project=project, user=current_user)


# --- Task Endpoints ---


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    responses={**responses.PROTECTED_RESPONSES, **responses.PROJECT_NOT_FOUND},
)
async def create_task_for_project(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service),
    # The user must be at least a member of the project's workspace to create a task.
    project: Project = Depends(require_project_permission),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task within a specific project.
    """
    return await service.create_task(
        task_in=task_in, project_id=project.id, creator=current_user
    )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=IPaginatedResponse[TaskResponse],
    summary="Get Tasks for a Project",
    responses={
        **responses.PROTECTED_RESPONSES,
        **responses.PROJECT_NOT_FOUND,
    },
)
async def list_tasks_for_project(
    project: Project = Depends(require_project_permission),
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_task_filter_params),
    service: TaskService = Depends(get_task_service),
):
    """
    Get a paginated and filtered list of tasks for a specific project.
    """
    tasks = await service.get_tasks_by_project(
        project_id=project.id, **pagination, **filters
    )
    return tasks