"""Word router — read-only cho user thường. Tạo/xoá Word chuyển sang /admin."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.enums import JLPTLevel
from app.core.exceptions import WordNotFoundError
from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.word import WordResponse
from app.services import word_service

router = APIRouter(prefix="/words", tags=["words"])


@router.get("", response_model=list[WordResponse])
def list_words(
    level: JLPTLevel | None = None,
    skip: int = 0,
    limit: int = 50,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    return word_service.list_words(session, level=level, skip=skip, limit=limit)


@router.get("/due", response_model=list[WordResponse])
def list_due_words(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return word_service.get_due_words(session, user_id=current_user.id)  # type: ignore


@router.get("/{word_id}", response_model=WordResponse)
def get_word(
    word_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    try:
        return word_service.get_word(session, word_id)
    except WordNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
