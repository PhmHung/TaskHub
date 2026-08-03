from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models import Project, User
from app.enums.workspace_role import WorkspaceRole
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate
from app.repositories.workspace_repository import workspace_repo


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
        # Check if a project with the same name already exists in this workspace
        existing_project = await self.project_repo.get_by_name(
            self.db, name=project_in.name, workspace_id=workspace_id
        )
        if existing_project:
            raise exceptions.http_409_exc(
                f"Project with name '{project_in.name}' already exists in this workspace."
            )

        project = await self.project_repo.create_with_owner_and_workspace(
            self.db, obj_in=project_in, owner_id=owner.id, workspace_id=workspace_id
        )
        # Optionally, you might want to return the project with more details if needed for the response
        return await self.project_repo.get(self.db, id=project.id)

    async def delete_project(self, *, project: Project, user: User):
        """
        Handles the business logic for deleting a project, including authorization.
        Only the project owner or a workspace owner can delete.
        """
        # 1. Allow project owner
        if project.owner_id == user.id:
            await self.project_repo.remove(self.db, id=project.id)
            return

        # 2. Allow workspace owner
        member = await workspace_repo.get_member(
            self.db, workspace_id=project.workspace_id, user_id=user.id
        )
        if member and member.role == WorkspaceRole.OWNER:
            await self.project_repo.remove(self.db, id=project.id)
            return

        # 3. Deny access
        raise exceptions.http_403_exc("Only the project owner or a workspace owner can delete this project.")