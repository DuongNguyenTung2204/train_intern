from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from ..dependencies import get_current_user, require_role
from ..crud import create_post, get_posts, get_post, update_post, delete_post, get_posts_by_user
from ..schemas.schemas import PostCreate, PostOut, PostUpdate
from ..models.models import User, UserRole
from ..database import get_db
from ..utils import send_new_post_notification

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostOut)
async def create_new_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    new_post = await create_post(db, post, current_user.id)
    background_tasks.add_task(send_new_post_notification, current_user.email, new_post.title)
    return new_post

@router.get("/", response_model=list[PostOut])
async def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db=Depends(get_db)
):
    return await get_posts(db, skip, limit)

@router.get("/user/{user_id}", response_model=list[PostOut])
async def read_posts_by_user(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db=Depends(get_db)
):
    return await get_posts_by_user(db, user_id, skip, limit)

@router.get("/{post_id}", response_model=PostOut)
async def read_post(post_id: int, db=Depends(get_db)):
    post = await get_post(db, post_id)
    if not post: raise HTTPException(404, "Post not found")
    return post

@router.put("/{post_id}", response_model=PostOut)
async def update_post_route(post_id: int, post: PostUpdate, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    db_post = await get_post(db, post_id)
    if not db_post:
        raise HTTPException(404, "Post not found")
    if current_user.role != UserRole.admin and db_post.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to edit this post")
    updated = await update_post(db, post_id, post)
    return updated

@router.delete("/{post_id}")
async def delete_post_route(post_id: int, current_user: User = Depends(require_role(UserRole.admin)), db=Depends(get_db)):
    deleted = await delete_post(db, post_id)
    if not deleted: raise HTTPException(404, "Post not found")
    return {"message": "Post deleted"}