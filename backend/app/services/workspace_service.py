from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.enums.workspace_role import WorkspaceRole
from app.models import User, Workspace, WorkspaceMember
from app.repositories.user_repository import user_repo
from app.repositories.workspace_repository import workspace_repo # Keep this
from app.schemas.workspace import WorkspaceCreate, WorkspaceMemberInvite # Add WorkspaceCreate


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workspace(
        self, *, workspace_in: WorkspaceCreate, owner_id: int
    ) -> Workspace:
        """
        Handles the business logic for creating a new workspace,
        including checking for duplicate names and adding the owner.
        """
        # Check if a workspace with the same name already exists
        existing_workspace = await workspace_repo.get_by_name(self.db, name=workspace_in.name)
        if existing_workspace:
            raise exceptions.http_409_exc(f"Workspace with name '{workspace_in.name}' already exists.")

        workspace = await workspace_repo.create_with_owner(
            self.db, obj_in=workspace_in, owner_id=owner_id
        )
        # Return the workspace with details for the response
        return await workspace_repo.get_by_id_with_details(self.db, workspace_id=workspace.id)

    async def invite_member(
        self,
        *,
        workspace: Workspace,
        invitation: WorkspaceMemberInvite,
        inviter: User,
    ) -> WorkspaceMember:
        """
        Handles the business logic of inviting a user to a workspace.
        """
        # Authorization Check: Only owners can invite members.
        inviter_membership = await workspace_repo.get_member(
            self.db, workspace_id=workspace.id, user_id=inviter.id
        )
        if not inviter_membership or inviter_membership.role != WorkspaceRole.OWNER:
            raise exceptions.http_403_exc("Only workspace owners can invite new members.")

        user_to_invite = await user_repo.get_by_email(self.db, email=invitation.email)
        if not user_to_invite:
            raise exceptions.http_404_exc(f"User with email {invitation.email} not found.")

        if user_to_invite.id == inviter.id:
            raise exceptions.http_400_exc("You cannot invite yourself.")

        # Check if user is already a member
        if await workspace_repo.get_member(
            self.db, workspace_id=workspace.id, user_id=user_to_invite.id
        ):
            raise exceptions.http_400_exc(f"User {invitation.email} is already a member.")

        # Only the main workspace owner can assign the OWNER role to others
        if invitation.role == WorkspaceRole.OWNER and workspace.owner_id != inviter.id:
            raise exceptions.http_403_exc("Only the main workspace owner can assign the OWNER role.")

        member = await workspace_repo.add_member(self.db, workspace, user_to_invite, invitation.role)
        return member

    async def delete_workspace(self, *, workspace: Workspace, user: User):
        """
        Handles the business logic of deleting a workspace, including authorization.
        """
        if workspace.owner_id != user.id:
            raise exceptions.http_403_exc("Only the main workspace owner can delete the workspace.")

        await workspace_repo.remove(self.db, id=workspace.id)
