from datetime import datetime, timedelta, timezone


from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        user_repo: UserRepository | None = None,
        refresh_token_repo: RefreshTokenRepository | None = None,
    ):
        self.db = db
        self.user_repo = user_repo or UserRepository(db)
        self.refresh_token_repo = refresh_token_repo or RefreshTokenRepository(db)

    async def register(self, data: UserCreate) -> UserResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(data.password)

        user = await self.user_repo.create(data, hashed_password)
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        # Fix: Calculate expires_at correctly by adding refresh_token_expire_days
        # The previous line `expires_at = datetime.now(timezone.utc)` was incorrect
        # as it made the refresh token expire immediately.
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await self.refresh_token_repo.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        stored_token = await self.refresh_token_repo.get_by_token(refresh_token)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )
        await self.refresh_token_repo.revoke(stored_token)
