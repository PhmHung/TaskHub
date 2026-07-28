from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenCreate(BaseModel):
    user_id: int
    token: str
    expires_at: str