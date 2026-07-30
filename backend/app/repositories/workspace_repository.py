from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.enums.workspace_role import WorkspaceRole
from app.models import User, Workspace, WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceRepository:
    """
    Repository for workspace-related database operations.
    """

    async def get(self, db: AsyncSession, *, id: int) -> Workspace | None:
        """Get a workspace by its ID without loading relationships."""
        statement = select(Workspace).where(Workspace.id == id)
        result = await db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def get_by_id_with_details(
        self, db: AsyncSession, *, workspace_id: int
    ) -> Workspace | None:
        """
        Get a workspace by its ID, loading the owner and members with their user details.
        """
        statement = (
            select(Workspace)
            .where(Workspace.id == workspace_id)
            .options(
                joinedload(Workspace.owner),
                joinedload(Workspace.members).joinedload(WorkspaceMember.user),
            )
        )
        result = await db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: WorkspaceCreate, owner_id: int
    ) -> Workspace:
        """Create a new workspace with an owner."""
        db_obj = Workspace(**obj_in.model_dump(), owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Workspace, obj_in: WorkspaceUpdate | dict[str, any]
    ) -> Workspace:
        """Update a workspace instance."""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Workspace | None:
        """Remove a workspace by its ID."""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def add_member(
        self, db: AsyncSession, workspace: Workspace, user: User, role: WorkspaceRole
    ) -> WorkspaceMember:
        """Add a user to a workspace with a specific role."""
        member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role=role)
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    async def get_member(
        self, db: AsyncSession, *, workspace_id: int, user_id: int
    ) -> WorkspaceMember | None:
        """Get a workspace member by workspace and user IDs."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id
        )
        result = await db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def remove_member(self, db: AsyncSession, *, member: WorkspaceMember) -> None:
        """Remove a member from a workspace."""
        await db.delete(member)
        await db.commit()


workspace_repo = WorkspaceRepository()
