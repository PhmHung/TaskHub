from typing import AsyncGenerator

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from app.db.session import AsyncSessionLocal
from app.models.users import User

http_bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Nhật token",
    bearerFormat="JWT",
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )
    return user
