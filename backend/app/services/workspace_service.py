from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.enums.workspace_role import WorkspaceRole
from app.models import User, Workspace, WorkspaceMember
from app.repositories.user_repository import user_repo
from app.repositories.workspace_repository import workspace_repo
from app.schemas.workspace import WorkspaceMemberInvite


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def invite_member(
        self,
        *,
        workspace: Workspace,
        invitation: WorkspaceMemberInvite,
        current_user: User,
    ) -> WorkspaceMember:
        """
        Handles the business logic of inviting a user to a workspace.
        """
        user_to_invite = await user_repo.get_by_email(self.db, email=invitation.email)
        if not user_to_invite:
            raise exceptions.http_404_exc(f"User with email {invitation.email} not found.")

        # Check if user is already a member
        if await workspace_repo.get_member(
            self.db, workspace_id=workspace.id, user_id=user_to_invite.id
        ):
            raise exceptions.http_400_exc(f"User {invitation.email} is already a member.")

        # Only the main workspace owner can assign the OWNER role to others
        if invitation.role == WorkspaceRole.OWNER and workspace.owner_id != current_user.id:
            raise exceptions.http_403_exc("Only the main workspace owner can assign the OWNER role.")

        member = await workspace_repo.add_member(self.db, workspace, user_to_invite, invitation.role)
        return member
