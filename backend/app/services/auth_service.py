from datetime import datetime, timedelta, timezone


from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import jwt_service
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.repositories.refresh_token_repository import refresh_token_repo
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        user_repo: UserRepository | None = None,
    ):
        self.db = db
        self.user_repo = user_repo or UserRepository()

    async def register(self, data: UserCreate) -> UserResponse:
        existing = await self.user_repo.get_by_email(self.db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        hashed_password = get_password_hash(data.password)
        user = await self.user_repo.create(self.db, data, hashed_password)
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(self.db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await refresh_token_repo.create(
            self.db,
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        stored_token = await refresh_token_repo.get_by_token(self.db, token=refresh_token)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )
        await refresh_token_repo.revoke(self.db, refresh_token=stored_token)

    async def refresh_token(self, token: str):
        """
        Xác thực refresh token và cấp một cặp token mới.
        """
        # 1. Xác thực và lấy payload từ refresh token
        payload = jwt_service.decode_refresh_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # 2. Kiểm tra token có trong DB và hợp lệ không
        db_token = await refresh_token_repo.get_by_token(self.db, token=token)
        if not db_token or db_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or has been revoked",
            )
        
        # 3. Lấy thông tin người dùng
        user = await self.user_repo.get_by_id(self.db, user_id=int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # 4. Tạo access token mới
        # (Tùy chọn: bạn có thể thu hồi refresh token cũ và tạo cả refresh token mới)
        new_access_token = create_access_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=token,  # This is the old refresh token
            token_type="bearer",
        )
