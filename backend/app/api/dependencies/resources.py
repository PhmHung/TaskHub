from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models import Project, Workspace
from app.repositories.project_repository import project_repo
from app.repositories.workspace_repository import workspace_repo
from .dependency import get_db


async def get_workspace_by_id(
    workspace_id: int = Path(), db: AsyncSession = Depends(get_db)
) -> Workspace:
    """
    Dependency to get a workspace by its ID from the path.
    Loads the workspace with its owner and members for permission checks.
    Raises 404 if not found.
    """
    workspace = await workspace_repo.get_by_id_with_details(db, workspace_id=workspace_id)
    if not workspace:
        raise exceptions.http_404_exc("Workspace not found")
    return workspace


async def get_project_by_id(
    project_id: int = Path(), db: AsyncSession = Depends(get_db)
) -> Project:
    """
    Dependency to get a project by its ID from the path.
    Raises 404 if not found.
    """
    project = await project_repo.get(db, id=project_id)
    if not project:
        raise exceptions.http_404_exc("Project not found")
    return project
