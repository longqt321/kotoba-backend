"""Review schemas — input/output cho FSRS review flow (fsrs v4 Card structure)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ReviewRating, ReviewState


class ReviewLogBase(BaseModel):
    rating: ReviewRating
    response_time_ms: int | None = None


class ReviewLogCreate(ReviewLogBase):
    """Input khi user submit 1 lần review."""


class ReviewLogResponse(ReviewLogBase):
    id: int
    review_id: int
    reviewed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """Input tạo review mới (khi user bắt đầu học 1 từ)."""

    word_id: int


class ReviewUpdate(BaseModel):
    state: ReviewState | None = None
    step: int | None = None
    stability: float | None = None
    difficulty: float | None = None
    due: datetime | None = None
    last_review: datetime | None = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    word_id: int
    state: ReviewState
    step: int | None
    stability: float | None
    difficulty: float | None
    due: datetime
    last_review: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewWithLogsResponse(ReviewResponse):
    """Response kèm lịch sử review."""

    logs: list[ReviewLogResponse] = []


class ReviewSubmitRequest(BaseModel):
    """Body khi user submit 1 review — service tự tính lại FSRS state."""

    rating: ReviewRating
    response_time_ms: int | None = None
