"""FSRS adapter — cầu mỏng quanh thư viện `fsrs` (v4).

Tách riêng để unit test thuật toán thuần logic + freezegun, không cần DB.
Mapping giữa model `Review` (DB) và `fsrs.Card`:
  - Review.state (NEW/LEARNING/REVIEW/RELEARNING) <-> Card.state (1/2/3, không có NEW)
  - Review.step, stability, difficulty, due, last_review <-> Card tương ứng
Review chưa từng review (state=NEW) map thành Card() mới (state=Learning, step=0).
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler, State

from app.core.enums import ReviewRating, ReviewState
from app.models.review import Review

scheduler = Scheduler(enable_fuzzing=False)

# fsrs.State (int) -> ReviewState
_FSRS_STATE_MAP: dict[int, ReviewState] = {
    State.Learning.value: ReviewState.LEARNING,
    State.Review.value: ReviewState.REVIEW,
    State.Relearning.value: ReviewState.RELEARNING,
}

# ReviewState -> fsrs.State
_REVIEW_STATE_TO_FSRS: dict[ReviewState, State] = {
    ReviewState.LEARNING: State.Learning,
    ReviewState.REVIEW: State.Review,
    ReviewState.RELEARNING: State.Relearning,
}

# ReviewRating -> fsrs.Rating
_RATING_MAP: dict[ReviewRating, Rating] = {
    ReviewRating.AGAIN: Rating.Again,
    ReviewRating.HARD: Rating.Hard,
    ReviewRating.GOOD: Rating.Good,
    ReviewRating.EASY: Rating.Easy,
}


@dataclass
class FsrsResult:
    """Kết quả sau khi apply rating: review đã cập nhật + log info để ghi vào DB."""

    review: Review
    log_rating: ReviewRating
    log_reviewed_at: datetime
    log_response_time_ms: int | None


def _ensure_aware(dt: datetime | None) -> datetime | None:
    """SQLite lưu naive datetime — gán lại tzinfo UTC để so sánh với `now` aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _to_card(review: Review) -> Card:
    """Map Review (DB) -> fsrs.Card. Review state=NEW -> Card mới."""
    if review.state == ReviewState.NEW:
        return Card()

    return Card(
        state=_REVIEW_STATE_TO_FSRS[review.state],
        step=review.step,
        stability=review.stability,
        difficulty=review.difficulty,
        due=_ensure_aware(review.due),
        last_review=_ensure_aware(review.last_review),
    )


def _apply_card_to_review(review: Review, card: Card) -> None:
    """Copy field từ fsrs.Card kết quả ngược lại vào Review (in-place)."""
    review.state = _FSRS_STATE_MAP[card.state.value]
    review.step = card.step
    review.stability = card.stability
    review.difficulty = card.difficulty
    review.due = card.due
    review.last_review = card.last_review


def apply_rating(
    review: Review,
    rating: ReviewRating,
    now: datetime,
    response_time_ms: int | None = None,
) -> FsrsResult:
    """Tính toán FSRS mới cho review dựa trên rating.

    Trả về FsrsResult chứa review đã cập nhật + thông tin để review_service ghi ReviewLog.
    Hàm này KHÔNG chạm DB — chỉ tính toán.
    """
    card = _to_card(review)
    fsrs_rating = _RATING_MAP[rating]
    updated_card, _ = scheduler.review_card(card, fsrs_rating, now)

    _apply_card_to_review(review, updated_card)
    return FsrsResult(
        review=review,
        log_rating=rating,
        log_reviewed_at=now,
        log_response_time_ms=response_time_ms,
    )
