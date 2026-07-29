from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from jose import JWTError
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.services import jwt_service 

# Danh sách các đường dẫn không yêu cầu xác thực
PUBLIC_PATHS = [
    "/docs",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/logout",
    "/api/v1/auth/refresh",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Bỏ qua middleware cho các đường dẫn công khai
        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/static"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        db_session = AsyncSessionLocal()
        try:
            payload = jwt_service.decode_access_token(token)
            if payload is None:
                raise ValueError("Invalid token")

            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token payload")

            user_repo = UserRepository(db_session)
            user = await user_repo.get_by_id(int(user_id))

            if user is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found"},
                )

            # Gắn user vào request state để các endpoint có thể sử dụng
            request.state.user = user

        except (ValueError, JWTError): # Catch specific token-related errors
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        finally:
            await db_session.close()

        response = await call_next(request)
        return response
