from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.user_role import UserRole

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    # Relationships to Task model
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.assignee_id",
        back_populates="assignee",
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="Task.creator_id", back_populates="creator"
    )

    # Relationships from other models
    owned_projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    owned_teams: Mapped[list["Team"]] = relationship(back_populates="owner")
    owned_workspaces: Mapped[list["Workspace"]] = relationship(back_populates="owner")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="user"
    )