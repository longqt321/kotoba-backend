from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.routers import admin, auth, docs, review, root, user, word, word_list


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,  # Tắt docs mặc định để dùng custom swagger
    redoc_url=None,
    lifespan=lifespan,
)

# Middleware (thứ tự LIFO: middleware thêm sau cùng chạy trước cùng)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(root.router, prefix="/api")
app.include_router(docs.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(word.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(word_list.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
