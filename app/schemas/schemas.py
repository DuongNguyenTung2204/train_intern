from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from ..models.models import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    class Config: from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase): pass
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostOut(PostBase):
    id: int
    created_at: datetime
    user_id: int
    class Config: from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase): pass

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentOut(CommentBase):
    id: int
    created_at: datetime
    user_id: int
    post_id: int
    class Config: from_attributes = True