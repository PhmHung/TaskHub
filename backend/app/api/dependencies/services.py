from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from .dependency import get_db


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService."""
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get an instance of UserService."""
    return UserService(db)
