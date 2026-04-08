from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user, require_role
from ..crud import create_comment, get_comments_by_post, get_post, get_comment, update_comment, delete_comment
from ..schemas.schemas import CommentCreate, CommentOut, CommentUpdate
from ..models.models import User, UserRole
from ..database import get_db

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

@router.post("/", response_model=CommentOut)
async def create_new_comment(post_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    post = await get_post(db, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return await create_comment(db, comment, current_user.id, post_id)

@router.get("/", response_model=list[CommentOut])
async def read_comments(post_id: int, db=Depends(get_db)):
    return await get_comments_by_post(db, post_id)

@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment_route(post_id: int, comment_id: int, comment: CommentUpdate, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    db_comment = await get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(404, "Comment not found")
    if db_comment.post_id != post_id:
        raise HTTPException(404, "Comment not found in this post")
    if current_user.role != UserRole.admin and db_comment.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to edit this comment")
    updated = await update_comment(db, comment_id, comment)
    return updated

@router.delete("/{comment_id}")
async def delete_comment_route(post_id: int, comment_id: int, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    db_comment = await get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(404, "Comment not found")
    if db_comment.post_id != post_id:
        raise HTTPException(404, "Comment not found in this post")
    if current_user.role != UserRole.admin and db_comment.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this comment")
    deleted = await delete_comment(db, comment_id)
    return {"message": "Comment deleted"}