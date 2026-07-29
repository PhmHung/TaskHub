from pydantic import BaseModel
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenCreate(BaseModel):
    user_id: int
    token: str
    expires_at: datetime