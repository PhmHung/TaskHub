from fastapi import APIRouter, Depends, status

from app.api.dependencies.dependency import get_current_user
from app.api.dependencies.services import get_user_service
from app.models.users import User
from app.schemas.user import ChangePassword, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    updated_user = await service.update_profile(user=current_user, update_data=update_data)
    return updated_user


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    change_password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(user=current_user, data=change_password_data)
