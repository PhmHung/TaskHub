from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_db
from app.schemas.token import TokenResponse
from app.schemas.user import LoginRequest, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db=db)
    return await service.register(data)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db=db)
    return await service.login(form_data.email, form_data.password)


@router.post("/auth/logout", status_code=204)
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db=db)
    await service.logout(refresh_token)
