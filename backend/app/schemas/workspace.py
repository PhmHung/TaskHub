from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.enums.workspace_role import WorkspaceRole
from app.schemas.user import UserResponse


class WorkspaceBase(BaseModel):
    name: str
    description: str | None = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class WorkspaceMemberResponse(BaseModel):
    user_id: int
    role: WorkspaceRole
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class WorkspaceResponse(WorkspaceBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: UserResponse
    members: list[WorkspaceMemberResponse]

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberInvite(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.EDITOR


class WorkspaceMemberUpdate(BaseModel):
    role: WorkspaceRole