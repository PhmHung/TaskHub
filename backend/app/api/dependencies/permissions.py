from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.enums.workspace_role import WorkspaceRole
from app.models import Project, User, Workspace
from .dependency import get_current_user, get_db # type: ignore
from .resources import get_project_by_id, get_workspace_by_id
from app.repositories.workspace_repository import workspace_repo

async def get_workspace_member_role(
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_workspace_by_id),
) -> WorkspaceRole | None:
    """
    Dependency to get the role of the current user in a specific workspace.
    Returns the role or None if the user is not a member.
    """
    # The workspace owner implicitly has the OWNER role.
    if workspace.owner_id == current_user.id:
        return WorkspaceRole.OWNER

    for member in workspace.members:
        if member.user_id == current_user.id:
            return member.role
    return None


def require_workspace_role(
    required_roles: list[WorkspaceRole],
) -> "Annotated[User, Depends]":
    """
    A dependency factory that creates a dependency to check if the current user
    has one of the required roles in the workspace.
    The workspace owner is always granted access.
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
        workspace: Workspace = Depends(get_workspace_by_id),
    ) -> User:
        # Workspace owner always has access
        if workspace.owner_id == current_user.id:
            return current_user

        member_role = None
        for member in workspace.members:
            if member.user_id == current_user.id:
                member_role = member.role
                break

        if not member_role or member_role not in required_roles:
            raise exceptions.http_403_exc(
                f"User must have one of the following roles: {', '.join(role.value for role in required_roles)}"
            )
        return current_user

    return role_checker


# Specific role requirement dependencies
require_workspace_owner_role = require_workspace_role([WorkspaceRole.OWNER])
require_workspace_editor_role = require_workspace_role(
    [WorkspaceRole.OWNER, WorkspaceRole.EDITOR]
)
require_workspace_viewer_role = require_workspace_role(
    [WorkspaceRole.OWNER, WorkspaceRole.EDITOR, WorkspaceRole.VIEWER]
)


async def require_project_permission(
    current_user: User = Depends(get_current_user),
    project: Project = Depends(get_project_by_id),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """
    Dependency to check if a user has permission to access/manage a project.
    Permission is granted if the user is the project owner, or a workspace
    OWNER or EDITOR.
    """
    # 1. Allow project owner
    if project.owner_id == current_user.id:
        return project

    # 2. Check workspace membership and role.
    # We fetch the workspace manually using the project's workspace_id.
    workspace = await workspace_repo.get_by_id_with_details(db, workspace_id=project.workspace_id)
    if not workspace:
        raise exceptions.http_404_exc("Workspace for this project not found.")

    # Check if the user is the workspace owner
    if workspace.owner_id == current_user.id:
        return project

    # Check if the user is a member with the required role
    member_role = None
    for member in workspace.members:
        if member.user_id == current_user.id:
            member_role = member.role
            break

    required_roles = [WorkspaceRole.OWNER, WorkspaceRole.EDITOR]
    if member_role and member_role in required_roles:
        return project

    # 3. If none of the above, deny access
    raise exceptions.http_403_exc(
        "User must be the project owner or a workspace OWNER/EDITOR to perform this action."
    )

    return project
