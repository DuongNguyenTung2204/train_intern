from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from ..auth.auth import verify_password, create_access_token
from ..crud import get_user_by_email, create_user, get_users, get_user, update_user, delete_user
from ..schemas.schemas import UserCreate, Token, UserOut, UserUpdate
from ..models.models import User, UserRole
from ..dependencies import get_current_user, require_role
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await create_user(db, user)
    return new_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, 
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password")
async def change_password(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user_update.password:
        raise HTTPException(status_code=400, detail="Password is required")
    updated = await update_user(db, current_user.id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password updated successfully"}


@router.get("/users", response_model=list[UserOut])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    return await get_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=UserOut)
async def read_user(user_id: int, current_user: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}")
async def delete_user_by_id(user_id: int, current_user: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.delete("/users/email/{email}")
async def delete_user_by_email(email: str, current_user: User = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = await delete_user(db, user.id)
    return {"message": "User deleted successfully"}