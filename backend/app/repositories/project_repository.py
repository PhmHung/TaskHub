from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.projects import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """
    Repository for project-related database operations.
    """

    async def get(self, db: AsyncSession, *, id: int) -> Project | None:
        """Get a project by its ID."""
        statement = select(Project).where(Project.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, *, name: str, workspace_id: int) -> Project | None:
        """Get a project by its name within a specific workspace."""
        statement = select(Project).where(Project.name == name, Project.workspace_id == workspace_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_with_owner_and_workspace(
        self, db: AsyncSession, *, obj_in: ProjectCreate, owner_id: int, workspace_id: int
    ) -> Project:
        """Create a new project with an owner and workspace."""
        db_obj = Project(**obj_in.model_dump(), owner_id=owner_id, workspace_id=workspace_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_projects_by_workspace(self, db: AsyncSession, *, workspace_id: int) -> list[Project]:
        """Get all non-archived projects for a given workspace."""
        statement = select(Project).where(Project.workspace_id == workspace_id, Project.is_archived == False)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, *, db_obj: Project, obj_in: ProjectUpdate | dict[str, any]
    ) -> Project:
        """Update a project instance."""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Project | None:
        """Remove a project by its ID."""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


project_repo = ProjectRepository()
