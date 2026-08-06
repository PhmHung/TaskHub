from sqlalchemy import select
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

    async def get_by_id(self, db: AsyncSession, *, comment_id: int) -> Comment | None:
        """Get a comment by its id."""
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def delete(self, db: AsyncSession, *, comment: Comment) -> None:
        """Delete a comment."""
        await db.delete(comment)
        await db.commit()


comment_repo = CommentRepository()