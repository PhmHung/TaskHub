from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router

app = FastAPI(
    title="TaskHub API",
    version="0.1.0",
    description="Hệ thống quản lý công việc TaskHub",
)

# Add CORS middleware to allow cross-origin requests
# This is crucial for frontend applications.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers, including Authorization
)


@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")