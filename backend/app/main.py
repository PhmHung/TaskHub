from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="TaskHub API",
    version="0.1.0",
    description="Hệ thống quản lý công việc TaskHub",
)

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")