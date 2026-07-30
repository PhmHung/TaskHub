from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.dependency import get_current_user, get_db
from app.api.dependencies.permissions import (
    require_project_permission,
    require_workspace_editor_role,
    require_workspace_viewer_role,
)
from app.api.dependencies.resources import get_project_by_id
from app.core import exceptions
from app.enums.workspace_role import WorkspaceRole
from app.models import Project, User
from app.repositories.project_repository import project_repo
from app.repositories.workspace_repository import workspace_repo
from app.schemas import project as project_schema

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/projects",
    response_model=project_schema.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    workspace_id: int,
    project_in: project_schema.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_workspace_editor_role),
):
    """
    Create a new project within a workspace. User must be an owner or editor.
    """
    project = await project_repo.create_with_owner_and_workspace(
        db, obj_in=project_in, owner_id=current_user.id, workspace_id=workspace_id
    )
    return project


@router.get(
    "/workspaces/{workspace_id}/projects",
    response_model=list[project_schema.ProjectResponse],
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


@router.get("/projects/{project_id}", response_model=project_schema.ProjectResponse)
async def get_project(
    project: Project = Depends(require_project_permission),
):
    """
    Get a project by ID. User must have permission in the project's workspace.
    """
    return project


@router.put("/projects/{project_id}", response_model=project_schema.ProjectResponse)
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
    "/projects/{project_id}/archive", response_model=project_schema.ProjectResponse
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
    "/projects/{project_id}/unarchive", response_model=project_schema.ProjectResponse
)
async def unarchive_project(
    project: Project = Depends(require_project_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Unarchive a project.
    """
    return await project_repo.update(db, db_obj=project, obj_in={"is_archived": False})


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project: Project = Depends(get_project_by_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a project. Only project owner or workspace owner can delete.
    """
    # 1. Check if the current user is the project owner
    if project.owner_id == current_user.id:
        await project_repo.remove(db, id=project.id)
        return

    # 2. If not, check if the user is a workspace OWNER
    workspace = await workspace_repo.get(db, id=project.workspace_id)
    if not workspace:
        raise exceptions.http_404_exc("Workspace not found for this project.")

    member = await workspace_repo.get_member(db, workspace_id=workspace.id, user_id=current_user.id)
    if (workspace.owner_id == current_user.id) or (member and member.role == WorkspaceRole.OWNER):
        await project_repo.remove(db, id=project.id)
        return

    # 3. If none of the above, deny access
    raise exceptions.http_403_exc(
        "Only project owner or workspace owner can delete this project."
    )