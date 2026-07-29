"""Review model — FSRS spaced repetition (fsrs v4 Card structure)."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.enums import ReviewRating, ReviewState


class Review(SQLModel, table=True):
    __tablename__ = "reviews"  # type: ignore
    __table_args__ = (UniqueConstraint("user_id", "word_id", name="uq_reviews_user_word"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    word_id: int = Field(foreign_key="words.id", ondelete="CASCADE")

    state: ReviewState = Field(default=ReviewState.NEW)
    step: int | None = 0
    stability: float | None = None
    difficulty: float | None = None

    due: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    last_review: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    logs: list["ReviewLog"] = Relationship(
        back_populates="review",
        cascade_delete=True,
    )


class ReviewLog(SQLModel, table=True):
    __tablename__ = "review_logs"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    review_id: int = Field(foreign_key="reviews.id", ondelete="CASCADE", index=True)

    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    rating: ReviewRating

    response_time_ms: int | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    review: Review = Relationship(back_populates="logs")
