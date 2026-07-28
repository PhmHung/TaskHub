from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)