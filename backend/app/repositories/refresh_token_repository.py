from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_tokens import RefreshToken


class RefreshTokenRepository:
    async def create(
        self, db: AsyncSession, *, user_id: int, token: str, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    async def get_by_token(self, db: AsyncSession, *, token: str) -> RefreshToken | None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke(self, db: AsyncSession, *, refresh_token: RefreshToken) -> None:
        if refresh_token:
            refresh_token.is_revoked = True
            db.add(refresh_token)
            await db.commit()


refresh_token_repo = RefreshTokenRepository()