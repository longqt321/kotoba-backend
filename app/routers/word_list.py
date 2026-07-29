"""WordList router — public read-only endpoints cho mọi user đã đăng nhập."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.word_list import WordListDetailResponse, WordListResponse
from app.services import word_list_service

router = APIRouter(prefix="/word-lists", tags=["word-lists"])


@router.get("", response_model=list[WordListResponse])
def list_word_lists(
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Trả về tất cả word lists cùng word_count."""
    rows = word_list_service.list_word_lists(session)
    return [
        WordListResponse(
            id=wl.id,
            name=wl.name,
            level=wl.level,
            source=wl.source,
            description=wl.description,
            created_at=wl.created_at,
            updated_at=wl.updated_at,
            word_count=count,
        )
        for wl, count in rows
    ]


@router.get("/{word_list_id}", response_model=WordListDetailResponse)
def get_word_list(
    word_list_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Trả về 1 list kèm danh sách Word bên trong."""
    wl = word_list_service.get_word_list(session, word_list_id)
    words = word_list_service.get_word_list_words(session, word_list_id)
    count = len(words)
    return WordListDetailResponse(
        id=wl.id,
        name=wl.name,
        level=wl.level,
        source=wl.source,
        description=wl.description,
        created_at=wl.created_at,
        updated_at=wl.updated_at,
        word_count=count,
        words=words,
    )
