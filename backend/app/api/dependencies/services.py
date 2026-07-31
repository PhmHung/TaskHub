from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.workspace_service import WorkspaceService
from .dependency import get_db
from app.services.task_service import TaskService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService."""
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get an instance of UserService."""
    return UserService(db)


def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    """Dependency to get an instance of WorkspaceService."""
    return WorkspaceService(db)


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    """Dependency to get an instance of ProjectService."""
    return ProjectService(db)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """Dependency to get an instance of TaskService."""
    return TaskService(db)
