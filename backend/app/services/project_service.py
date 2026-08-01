from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(
        self, db: AsyncSession, project_repo: ProjectRepository | None = None
    ):
        self.db = db
        self.project_repo = project_repo or ProjectRepository()

    async def create_project(
        self, *, project_in: ProjectCreate, owner: User, workspace_id: int
    ) -> Project:
        """
        Handles the business logic for creating a new project.
        """
        project = await self.project_repo.create_with_owner_and_workspace(
            self.db, obj_in=project_in, owner_id=owner.id, workspace_id=workspace_id
        )
        return project