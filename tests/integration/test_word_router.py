"""Integration test /words — qua HTTP thật với DB in-memory."""

import pytest

from sqlmodel import select
from app.models.review import Review
from app.models.word import Word
from app.core.enums import JLPTLevel
from tests.factories import WordFactory, UserFactory

pytestmark = pytest.mark.integration


def _word_payload(**overrides) -> dict:
    payload = {
        "word": "食べる",
        "kanji": "食べる",
        "level": "N5",
        "word_type": "Verb",
        "source": "Mimikara",
        "topic": "Food",
        "examples": [{"japanese": "ご飯を食べる", "translation": "eat rice"}],
        "meanings": [{"meaning": "to eat"}],
    }
    payload.update(overrides)
    return payload


class TestListWords:
    async def test_empty_db_returns_empty_list(self, authed_client):
        response = await authed_client.get("/words")
        assert response.status_code == 200
        assert response.json() == []

    async def test_requires_auth(self, client):
        response = await client.get("/words")
        assert response.status_code == 401

    async def test_pagination(self, authed_client, session):
        """GET /words?limit=2 trả đúng số lượng."""
        for _ in range(5):
            word = WordFactory.build()
            session.add(word)
        session.commit()

        response = await authed_client.get("/words?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_filter_by_level(self, authed_client, session):
        """GET /words?level=N4 chỉ trả từ N4."""
        n5 = WordFactory.build(level=JLPTLevel.N5, word="taberu")
        n4 = WordFactory.build(level=JLPTLevel.N4, word="iku")
        session.add_all([n5, n4])
        session.commit()

        response = await authed_client.get("/words?level=N4")
        assert response.status_code == 200
        words = response.json()
        assert len(words) == 1
        assert words[0]["level"] == "N4"


class TestCreateWord:
    async def test_create_returns_201_with_nested(self, authed_client):
        response = await authed_client.post("/words", json=_word_payload())
        assert response.status_code == 201
        body = response.json()
        assert body["word"] == "食べる"
        assert len(body["examples"]) == 1
        assert len(body["meanings"]) == 1

    async def test_missing_word_type_returns_422(self, authed_client):
        payload = _word_payload()
        del payload["word_type"]
        response = await authed_client.post("/words", json=payload)
        assert response.status_code == 422

    async def test_requires_auth(self, client):
        response = await client.post("/words", json=_word_payload())
        assert response.status_code == 401

    async def test_create_word_appears_in_due(self, authed_client, session, test_user):
        """Tạo word → xuất hiện ngay trong GET /words/due (có Review seed)."""
        resp = await authed_client.post("/words", json=_word_payload())
        assert resp.status_code == 201
        word_id = resp.json()["id"]

        due_resp = await authed_client.get("/words/due")
        assert due_resp.status_code == 200
        ids = [w["id"] for w in due_resp.json()]
        assert word_id in ids

    async def test_due_word_isolated_by_creator(self, authed_client, session, test_user):
        """User A tạo word → DB chỉ có Review cho user A, không cho user B."""
        other = UserFactory.build()
        session.add(other)
        session.commit()

        resp = await authed_client.post("/words", json=_word_payload())
        word_id = resp.json()["id"]

        reviews_for_a = session.exec(
            select(Review).where(Review.user_id == test_user.id)
        ).all()
        assert len(reviews_for_a) == 1
        assert reviews_for_a[0].word_id == word_id

        reviews_for_b = session.exec(
            select(Review).where(Review.user_id == other.id)
        ).all()
        assert len(reviews_for_b) == 0


class TestGetWord:
    async def test_get_existing_word(self, authed_client, session):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        response = await authed_client.get(f"/words/{word.id}")
        assert response.status_code == 200
        assert response.json()["id"] == word.id

    async def test_get_nonexistent_returns_404(self, authed_client):
        response = await authed_client.get("/words/99999")
        assert response.status_code == 404


class TestDeleteWord:
    async def test_delete_existing_word_returns_204(self, authed_client, session):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        response = await authed_client.delete(f"/words/{word.id}")
        assert response.status_code == 204

        assert session.get(Word, word.id) is None

    async def test_delete_nonexistent_returns_404(self, authed_client):
        response = await authed_client.delete("/words/99999")
        assert response.status_code == 404

    async def test_requires_auth(self, client, session):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        response = await client.delete(f"/words/{word.id}")
        assert response.status_code == 401

    async def test_delete_cascades_reviews(self, authed_client, session, test_user):
        """Xóa word phải xóa cả Review liên quan (cascade_delete ở model)."""
        resp = await authed_client.post("/words", json=_word_payload())
        word_id = resp.json()["id"]

        reviews_before = session.exec(
            select(Review).where(Review.word_id == word_id)
        ).all()
        assert len(reviews_before) == 1

        del_resp = await authed_client.delete(f"/words/{word_id}")
        assert del_resp.status_code == 204

        reviews_after = session.exec(
            select(Review).where(Review.word_id == word_id)
        ).all()
        assert len(reviews_after) == 0
