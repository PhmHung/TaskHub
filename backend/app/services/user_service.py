from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession, user_repo: UserRepository | None = None):
        self.db = db
        self.user_repo = user_repo or UserRepository(db)

    async def update_profile(self, user: User, update_data: UserUpdate) -> User:
        update_dict = update_data.model_dump(exclude_unset=True)
        new_password = update_dict.pop("password", None)
        current_password = update_dict.pop("current_password", None)

        if new_password:
            if not current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to set a new password.",
                )
            if not verify_password(current_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect current password.",
                )
            update_dict["hashed_password"] = get_password_hash(new_password)
        elif current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be provided to update password.",
            )

        if not update_dict:
            return user

        return await self.user_repo.update(user=user, update_data=update_dict)
