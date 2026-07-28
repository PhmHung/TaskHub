from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.db.base import Base
from app.models.users import User
from app.models.teams import Team
from app.enums.team import MembershipRole


class Membership(Base):
    __tablename__ = "memberships"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="memberships")
    team: Mapped["Team"] = relationship(back_populates="memberships")