from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.db.session import AsyncSessionLocal
from app.models.users import User
from app.core.logger import logger
from app.repositories.user_repository import user_repo
from app.services import jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Decodes access token, validates payload, and returns the current user.
    This is the primary dependency for securing endpoints.
    """
    logger.info("========== GET CURRENT USER ==========")
    logger.info("Token: %s", token)
    logger.debug("Attempting to get current user from token.")
    payload = jwt_service.decode_access_token(token)
    if not payload:
        logger.warning(
            "Token decoding failed or token is invalid (e.g., expired, bad signature, wrong type)."
        )
        raise exceptions.http_401_exc("Invalid or expired token.")

    user_id_str = payload.get("sub")
    logger.info("User ID in token: %s", user_id_str)
    if not user_id_str:
        logger.warning("Token payload is missing 'sub' (user ID).")
        raise exceptions.http_401_exc("Invalid token payload.")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        logger.warning(f"User ID '{user_id_str}' in token is not a valid integer.")
        raise exceptions.http_401_exc("Invalid user ID in token.")

    logger.debug(f"Token decoded successfully for user ID: {user_id}")
    user = await user_repo.get_by_id(db, user_id=user_id)
    logger.info("User from DB: %s", user)

    if not user:
        logger.warning(f"User with ID {user_id} not found in database.")
        raise exceptions.http_401_exc("User not found.")
    if not user.is_active:
        logger.warning(f"User {user.id} is inactive.")
        raise exceptions.http_400_exc("Inactive user")

    logger.debug(f"Successfully authenticated user {user.id} ({user.email}).")
    return user
