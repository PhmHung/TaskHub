"""add_in_review_and_urgent_enums

Revision ID: 23cb261d6d79
Revises: f40960ae25d0
Create Date: 2026-08-06 20:47:23.026380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23cb261d6d79'
down_revision: Union[str, Sequence[str], None] = 'f40960ae25d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('tasks', 'status',
               existing_type=sa.Enum('TODO', 'IN_PROGRESS', 'DONE', name='taskstatus'),
               type_=sa.Enum('TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', name='taskstatus'),
               existing_nullable=False)
    op.alter_column('tasks', 'priority',
               existing_type=sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'),
               type_=sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskpriority'),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('tasks', 'status',
               existing_type=sa.Enum('TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', name='taskstatus'),
               type_=sa.Enum('TODO', 'IN_PROGRESS', 'DONE', name='taskstatus'),
               existing_nullable=False)
    op.alter_column('tasks', 'priority',
               existing_type=sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskpriority'),
               type_=sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'),
               existing_nullable=False)
