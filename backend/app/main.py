from fastapi import FastAPI

from app.api.v1.router import api_router
from app.middlewares.auth_middleware import AuthMiddleware

app = FastAPI(
    title="TaskHub API",
    version="0.1.0",
    description="Hệ thống quản lý công việc TaskHub",
)

app.add_middleware(AuthMiddleware)

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")