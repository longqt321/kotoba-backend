"""Integration test /reviews — FSRS submit + due filter."""

import pytest
from freezegun import freeze_time

from app.core.enums import ReviewState
from app.models.review import Review, ReviewLog
from tests.factories import WordFactory

pytestmark = pytest.mark.integration


class TestSubmitReview:
    async def test_submit_good_returns_200(self, authed_client, session, test_user):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        response = await authed_client.post(f"/reviews/{word.id}", json={"rating": "Good"})
        assert response.status_code == 200
        body = response.json()
        assert body["word_id"] == word.id
        assert body["state"] != ReviewState.NEW.value

    async def test_invalid_rating_returns_422(self, authed_client, session):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        response = await authed_client.post(f"/reviews/{word.id}", json={"rating": "not-a-rating"})
        assert response.status_code == 422

    async def test_requires_auth(self, client):
        response = await client.post("/reviews/1", json={"rating": "Good"})
        assert response.status_code == 401

    async def test_nonexistent_word_returns_404(self, authed_client):
        response = await authed_client.post("/reviews/99999", json={"rating": "Good"})
        assert response.status_code == 404

    async def test_submit_twice_keeps_single_review_with_two_logs(
        self, authed_client, session, test_user
    ):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        await authed_client.post(f"/reviews/{word.id}", json={"rating": "Good"})
        await authed_client.post(f"/reviews/{word.id}", json={"rating": "Good"})

        from sqlmodel import select

        reviews = session.exec(
            select(Review).where(Review.user_id == test_user.id, Review.word_id == word.id)
        ).all()
        assert len(reviews) == 1

        logs = session.exec(select(ReviewLog).where(ReviewLog.review_id == reviews[0].id)).all()
        assert len(logs) == 2


class TestDueReviews:
    @freeze_time("2026-07-19")
    async def test_due_filter_excludes_future_due(self, authed_client, session, test_user):
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        # Submit 1 lần -> due đẩy ra tương lai
        await authed_client.post(f"/reviews/{word.id}", json={"rating": "Good"})

        response = await authed_client.get("/reviews/due")
        assert response.status_code == 200
        ids = [r["word_id"] for r in response.json()]
        assert word.id not in ids

    async def test_due_includes_overdue_review(self, authed_client, session, test_user):
        from datetime import UTC, datetime, timedelta

        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        # Tạo review với due trong quá khứ
        review = Review(
            user_id=test_user.id,
            word_id=word.id,
            state=ReviewState.LEARNING,
            due=datetime.now(UTC) - timedelta(days=1),
        )
        session.add(review)
        session.commit()

        response = await authed_client.get("/reviews/due")
        ids = [r["word_id"] for r in response.json()]
        assert word.id in ids

    async def test_cross_user_isolation(self, authed_client, session, test_user):
        from datetime import UTC, datetime, timedelta

        from tests.factories import UserFactory

        other = UserFactory.build(email="other@example.com")
        session.add(other)
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(other)
        session.refresh(word)

        review = Review(
            user_id=other.id,
            word_id=word.id,
            state=ReviewState.LEARNING,
            due=datetime.now(UTC) - timedelta(days=1),
        )
        session.add(review)
        session.commit()

        response = await authed_client.get("/reviews/due")
        ids = [r["word_id"] for r in response.json()]
        assert word.id not in ids  # review của user khác không xuất hiện

    async def test_due_requires_auth(self, client):
        """GET /reviews/due không auth → 401."""
        response = await client.get("/reviews/due")
        assert response.status_code == 401
