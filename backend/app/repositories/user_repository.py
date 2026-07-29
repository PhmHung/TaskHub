from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timezone
from app.models.users import User
from app.schemas.user import UserCreate
from app.enums.user_role import UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed_password,
            role=UserRole.MEMBER,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, update_data: dict) -> User:
        """Cập nhật thông tin của một user."""
        for key, value in update_data.items():
            # Chỉ cập nhật các trường được gửi lên và không phải là None
            if value is not None:
                setattr(user, key, value)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user