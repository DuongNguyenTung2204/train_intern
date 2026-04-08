from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Comment
from ..schemas.schemas import CommentCreate, CommentUpdate


async def create_comment(db: AsyncSession, comment: CommentCreate, user_id: int, post_id: int):
    db_comment = Comment(**comment.model_dump(), user_id=user_id, post_id=post_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def get_comments_by_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Comment).where(Comment.post_id == post_id))
    return result.scalars().all()


async def get_comment(db: AsyncSession, comment_id: int):
    return await db.get(Comment, comment_id)


async def update_comment(db: AsyncSession, comment_id: int, comment: CommentUpdate):
    db_comment = await db.get(Comment, comment_id)
    if db_comment:
        for key, value in comment.model_dump(exclude_unset=True).items():
            setattr(db_comment, key, value)
        await db.commit()
        await db.refresh(db_comment)
    return db_comment


async def delete_comment(db: AsyncSession, comment_id: int):
    db_comment = await db.get(Comment, comment_id)
    if db_comment:
        await db.delete(db_comment)
        await db.commit()
    return db_comment