from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_tokens import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        if refresh_token:
            refresh_token.is_revoked = True
            await self.db.commit()