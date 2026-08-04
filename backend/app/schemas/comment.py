from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    user_id: int
    task_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)