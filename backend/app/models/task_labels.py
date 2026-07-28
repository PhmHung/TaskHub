from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

task_labels = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id"), primary_key=True),
)