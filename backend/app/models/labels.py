from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.task_labels import task_labels


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # e.g., #RRGGBB
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    # Relationship
    project: Mapped["Project"] = relationship(back_populates="labels")
    tasks: Mapped[list["Task"]] = relationship(
        secondary=task_labels, back_populates="labels"
    )