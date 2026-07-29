"""E2E test — luồng học từ đầy đủ (thay cho test tay khi chưa có frontend)."""

from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time

from app.core.enums import ReviewState
from app.models.review import Review
from tests.factories import WordFactory

pytestmark = pytest.mark.e2e


class TestFullLearningFlow:
    @freeze_time("2026-07-19")
    async def test_user_learns_and_reviews_word(self, authed_client, session, test_user):
        # 1. Seed 1 từ + review đến hạn cho user
        word = WordFactory.build()
        session.add(word)
        session.commit()
        session.refresh(word)

        review = Review(
            user_id=test_user.id,
            word_id=word.id,
            state=ReviewState.LEARNING,
            due=datetime.now(UTC) - timedelta(days=1),
        )
        session.add(review)
        session.commit()

        # 2. Lấy từ cần học -> có từ vừa seed
        words_resp = await authed_client.get("/words/due")
        assert words_resp.status_code == 200
        due_ids = [w["id"] for w in words_resp.json()]
        assert word.id in due_ids

        # 3. Review với rating Good -> due đẩy ra tương lai
        review_resp = await authed_client.post(f"/reviews/{word.id}", json={"rating": "Good"})
        assert review_resp.status_code == 200
        new_due = datetime.fromisoformat(review_resp.json()["due"])
        if new_due.tzinfo is None:
            new_due = new_due.replace(tzinfo=UTC)
        assert new_due > datetime.now(UTC)

        # 4. Từ vừa review không còn trong danh sách due hôm nay
        words_resp_2 = await authed_client.get("/words/due")
        due_ids_2 = [w["id"] for w in words_resp_2.json()]
        assert word.id not in due_ids_2
