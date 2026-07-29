"""Unit test user_service.get_or_create_user."""

import pytest
from sqlmodel import select

from app.core.enums import JLPTLevel
from app.models.user import User
from app.services import user_service

pytestmark = pytest.mark.unit


class TestGetOrCreateUser:
    def test_creates_new_user_with_default_level(self, session):
        user = user_service.get_or_create_user(session, email="new@example.com", name="Alice")

        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.name == "Alice"
        assert user.level == JLPTLevel.N5

    def test_returns_existing_user_no_duplicate(self, session):
        user_service.get_or_create_user(session, email="dup@example.com", name="Alice")
        user_service.get_or_create_user(session, email="dup@example.com", name="Alice")

        all_users = session.exec(select(User)).all()
        assert len(all_users) == 1

    def test_get_user_returns_none_when_missing(self, session):
        assert user_service.get_user(session, 99999) is None
