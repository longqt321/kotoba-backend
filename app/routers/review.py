"""Review router — submit review (FSRS) + query review đến hạn."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.exceptions import WordNotFoundError
from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.review import ReviewResponse, ReviewSubmitRequest
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{word_id}", response_model=ReviewResponse)
def submit_review(
    word_id: int,
    data: ReviewSubmitRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return review_service.submit_review(
            session,
            user_id=current_user.id,
            word_id=word_id,
            rating=data.rating,
            response_time_ms=data.response_time_ms,
        )
    except WordNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/due", response_model=list[ReviewResponse])
def list_due_reviews(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return review_service.get_due_reviews(session, user_id=current_user.id)
