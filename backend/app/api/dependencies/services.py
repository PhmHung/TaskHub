from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.dependency import get_db
from app.api.dependencies.redis import get_redis_client
from app.services.auth_service import AuthService
from app.services.label_service import LabelService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService
from app.repositories.user_repository import user_repo as user_repository_instance


async def get_task_service(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> TaskService:
    return TaskService(db=db, redis_client=redis_client, user_repo=user_repository_instance)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db=db)


async def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(db=db)


async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db=db)


async def get_label_service(db: AsyncSession = Depends(get_db)) -> LabelService:
    return LabelService(db=db)