"""Unit test FSRS adapter — thuần logic, không DB, dùng freezegun."""

from datetime import UTC, datetime

import pytest
from freezegun import freeze_time

from app.core.enums import ReviewRating, ReviewState
from app.models.review import Review
from app.services import fsrs

pytestmark = pytest.mark.unit


def _new_review() -> Review:
    return Review(user_id=1, word_id=1, due=datetime.now(UTC))


class TestApplyRating:
    @freeze_time("2026-07-19")
    def test_new_card_good_leaves_new_state(self):
        review = _new_review()
        result = fsrs.apply_rating(review, ReviewRating.GOOD, datetime.now(UTC))

        assert result.review.state != ReviewState.NEW
        assert result.review.stability is not None
        assert result.review.stability > 0
        assert result.review.last_review is not None

    @freeze_time("2026-07-19")
    def test_due_is_in_future_after_good(self):
        review = _new_review()
        now = datetime.now(UTC)
        result = fsrs.apply_rating(review, ReviewRating.GOOD, now)

        assert result.review.due >= now

    @freeze_time("2026-07-19")
    @pytest.mark.parametrize(
        "rating",
        [ReviewRating.HARD, ReviewRating.GOOD, ReviewRating.EASY],
    )
    def test_easy_gives_longest_interval(self, rating):
        """EASY luôn cho interval >= các rating khác trên cùng card mới."""
        now = datetime.now(UTC)

        review = _new_review()
        due_rating = fsrs.apply_rating(review, rating, now).review.due

        review_easy = _new_review()
        due_easy = fsrs.apply_rating(review_easy, ReviewRating.EASY, now).review.due

        assert due_easy >= due_rating

    @freeze_time("2026-07-19")
    def test_log_info_preserved(self):
        review = _new_review()
        now = datetime.now(UTC)
        result = fsrs.apply_rating(review, ReviewRating.GOOD, now, response_time_ms=1500)

        assert result.log_rating == ReviewRating.GOOD
        assert result.log_reviewed_at == now
        assert result.log_response_time_ms == 1500

    @freeze_time("2026-07-19")
    def test_review_state_again_goes_relearning(self):
        """Card đang ở REVIEW, rating AGAIN -> RELEARNING (lapse)."""
        now = datetime.now(UTC)
        review = Review(
            user_id=1,
            word_id=1,
            state=ReviewState.REVIEW,
            step=0,
            stability=10.0,
            difficulty=5.0,
            due=now,
            last_review=now,
        )
        result = fsrs.apply_rating(review, ReviewRating.AGAIN, now)

        assert result.review.state == ReviewState.RELEARNING
