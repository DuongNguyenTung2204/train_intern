from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Post
from ..schemas.schemas import PostCreate, PostUpdate


async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
    db_post = Post(**post.model_dump(), user_id=user_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Post).offset(skip).limit(limit).order_by(Post.created_at.desc()))
    return result.scalars().all()


async def get_post(db: AsyncSession, post_id: int):
    return await db.get(Post, post_id)


async def get_posts_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Post).where(Post.user_id == user_id).offset(skip).limit(limit).order_by(Post.created_at.desc()))
    return result.scalars().all()


async def update_post(db: AsyncSession, post_id: int, post: PostUpdate):
    db_post = await db.get(Post, post_id)
    if db_post:
        for key, value in post.model_dump(exclude_unset=True).items():
            setattr(db_post, key, value)
        await db.commit()
        await db.refresh(db_post)
    return db_post


async def delete_post(db: AsyncSession, post_id: int):
    db_post = await db.get(Post, post_id)
    if db_post:
        await db.delete(db_post)
        await db.commit()
    return db_post
