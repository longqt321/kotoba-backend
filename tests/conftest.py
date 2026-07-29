"""Fixtures dùng chung — viết 1 lần, dùng cho toàn bộ test."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.models  # noqa: F401 — đăng ký toàn bộ metadata trước create_all
from app.dependencies import get_current_user, get_session
from app.main import app as fastapi_app
from tests.factories import UserFactory


@pytest.fixture(name="session")
def session_fixture():
    """DB SQLite in-memory riêng cho mỗi test -> test độc lập."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """Một user có sẵn trong DB, dùng cho test cần auth."""
    user = UserFactory.build()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest_asyncio.fixture(name="client")
async def client_fixture(session):
    """Client chưa đăng nhập — override get_session dùng DB in-memory."""

    def get_session_override():
        return session

    fastapi_app.dependency_overrides[get_session] = get_session_override

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture(name="authed_client")
async def authed_client_fixture(session, test_user):
    """Client đã đăng nhập — override get_current_user trả test_user."""

    def get_session_override():
        return session

    fastapi_app.dependency_overrides[get_session] = get_session_override
    fastapi_app.dependency_overrides[get_current_user] = lambda: test_user

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    fastapi_app.dependency_overrides.clear()
