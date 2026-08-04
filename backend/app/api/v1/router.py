from fastapi import APIRouter

from app.api.v1.routers import auth, user, workspaces, projects, tasks, labels

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(projects.router, tags=["Projects"])
api_router.include_router(labels.router, prefix="/projects/{project_id}/labels")
api_router.include_router(tasks.router)
