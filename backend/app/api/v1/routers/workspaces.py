from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.dependency import get_current_user, get_db
from app.api.dependencies.permissions import (
    require_workspace_owner_role,
    require_workspace_viewer_role,
)
from app.api.dependencies.resources import get_workspace_by_id
from app.api.dependencies.services import get_workspace_service
from app.core import exceptions
from app.models import User, Workspace, WorkspaceMember
from app.repositories.workspace_repository import workspace_repo
from app.schemas import workspace as workspace_schema
from app.core.logger import logger
from app.services.workspace_service import WorkspaceService


router = APIRouter()


@router.post(
    "/",
    response_model=workspace_schema.WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    workspace_in: workspace_schema.WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user), # Temporarily disabled for debugging
):
    """
    Create a new workspace. The creator becomes the owner.
    """
    owner_id_for_debugging = 1
    logger.info(f"DEBUGGING: Creating a new workspace '{workspace_in.name}' for owner ID {owner_id_for_debugging}")
    workspace = await workspace_repo.create_with_owner(
        db, obj_in=workspace_in, owner_id=owner_id_for_debugging
    )
    return await workspace_repo.get_by_id_with_details(
    db,
    workspace_id=workspace.id,
)


@router.get("/{workspace_id}", response_model=workspace_schema.WorkspaceResponse)
async def get_workspace(
    workspace: Workspace = Depends(get_workspace_by_id),
    _: User = Depends(require_workspace_viewer_role),
):
    """
    Get workspace details. User must be a member of the workspace.
    """
    return workspace


@router.put("/{workspace_id}", response_model=workspace_schema.WorkspaceResponse)
async def update_workspace(
    workspace_in: workspace_schema.WorkspaceUpdate,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_workspace_owner_role),
):
    """
    Update a workspace. Only users with the OWNER role can update.
    """
    updated_workspace = await workspace_repo.update(
        db, db_obj=workspace, obj_in=workspace_in
    )
    return await workspace_repo.get_by_id_with_details(
    db,
    workspace_id=updated_workspace.id,
)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace: Workspace = Depends(get_workspace_by_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a workspace. Only the workspace owner can delete it.
    """
    if workspace.owner_id != current_user.id:
        raise exceptions.http_403_exc("Only the workspace owner can delete the workspace.")
    await workspace_repo.remove(db, id=workspace.id)


@router.post(
    "/{workspace_id}/members", response_model=workspace_schema.WorkspaceMemberResponse
)
async def invite_member(
    invitation: workspace_schema.WorkspaceMemberInvite,
    workspace: Workspace = Depends(get_workspace_by_id),
    current_user: User = Depends(require_workspace_owner_role),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Invite a user to the workspace. Only users with the OWNER role can invite.
    """
    return await service.invite_member(
        workspace=workspace, invitation=invitation, current_user=current_user
    )


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: int,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_workspace_owner_role),
):
    """
    Remove a member from the workspace. Users with OWNER role can remove members. The main owner cannot be removed.
    """
    if workspace.owner_id == user_id:
        raise exceptions.http_400_exc("Cannot remove the workspace owner.")

    member = await workspace_repo.get_member(db, workspace_id=workspace.id, user_id=user_id)
    if not member:
        raise exceptions.http_404_exc("Member not found in this workspace.")

    await workspace_repo.remove_member(db, member=member)