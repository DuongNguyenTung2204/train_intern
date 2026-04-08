from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, Base
from .routers.auth import router as auth_router
from .routers.posts import router as posts_router
from .routers.comments import router as comments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application started - Using Alembic for migrations")
    yield
    print("👋 Application shutting down")

app = FastAPI(title="Personal Blog API", version="1.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)