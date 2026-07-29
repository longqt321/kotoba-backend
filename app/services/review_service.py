"""Review service — điều phối DB + FSRS cho review flow."""

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.core.exceptions import WordNotFoundError
from app.models.review import Review, ReviewLog
from app.models.word import Word
from app.models.word_list import UserWordList, WordListEntry
from app.services import fsrs
from app.services.fsrs import FsrsResult


def _get_or_create_review(session: Session, user_id: int, word_id: int, now: datetime) -> Review:
    """Lấy Review theo (user_id, word_id); nếu chưa có thì tạo mới state=NEW."""
    review = session.exec(
        select(Review).where(Review.user_id == user_id, Review.word_id == word_id)
    ).first()
    if review is not None:
        return review

    review = Review(user_id=user_id, word_id=word_id, due=now)
    session.add(review)
    session.flush()
    return review


def submit_review(
    session: Session,
    user_id: int,
    word_id: int,
    rating,  # ReviewRating
    response_time_ms: int | None = None,
    now: datetime | None = None,
) -> Review:
    """Submit 1 lần review: tính FSRS, cập nhật Review, ghi ReviewLog."""
    from app.core.enums import ReviewRating

    if not isinstance(rating, ReviewRating):
        rating = ReviewRating(rating)
    if now is None:
        now = datetime.now(UTC)

    word = session.get(Word, word_id)
    if word is None:
        raise WordNotFoundError(word_id)

    review = _get_or_create_review(session, user_id, word_id, now)

    result: FsrsResult = fsrs.apply_rating(review, rating, now, response_time_ms)
    review = result.review
    review.updated_at = now

    session.add(review)
    session.flush()

    log = ReviewLog(
        review_id=review.id,
        reviewed_at=result.log_reviewed_at,
        rating=result.log_rating,
        response_time_ms=result.log_response_time_ms,
    )
    session.add(log)

    session.commit()
    session.refresh(review)
    return review


def get_due_reviews(session: Session, user_id: int, now: datetime | None = None) -> list[Review]:
    """Lấy các review đến hạn (due <= now) của user, giới hạn trong list đã chọn."""
    if now is None:
        now = datetime.now(UTC)

    selected_lists = select(UserWordList.word_list_id).where(UserWordList.user_id == user_id)
    selected_word_ids = select(WordListEntry.word_id).where(
        WordListEntry.word_list_id.in_(selected_lists)
    )

    return list(
        session.exec(
            select(Review).where(
                Review.user_id == user_id,
                Review.word_id.in_(selected_word_ids),
                Review.due <= now,
            )
        ).all()
    )
