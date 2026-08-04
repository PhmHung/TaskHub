from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment
from app.schemas.comment import CommentCreate


class CommentRepository:
    """
    Repository for comment-related database operations.
    """

    async def create(
        self, db: AsyncSession, *, obj_in: CommentCreate, task_id: int, user_id: int
    ) -> Comment:
        """Create a new comment."""
        db_obj = Comment(**obj_in.model_dump(), task_id=task_id, user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


comment_repo = CommentRepository()