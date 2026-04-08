from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_password_hash
from ..models.models import User
from ..schemas.schemas import UserCreate, UserUpdate


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    db_user = await db.get(User, user_id)
    if db_user:
        if user.password:
            db_user.hashed_password = get_password_hash(user.password)
        await db.commit()
        await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await db.get(User, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user
