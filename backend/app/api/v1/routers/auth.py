from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.services import get_auth_service
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(data.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh_token(data.refresh_token)