"""Admin router — mutation endpoints cho admin quản lý word lists và từ vựng.

Tất cả endpoint ở đây đều yêu cầu get_current_admin (403 nếu không phải admin).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.exceptions import WordListNotFoundError, WordNotFoundError
from app.dependencies import get_current_admin, get_session
from app.models.user import User
from app.schemas.word import WordResponse
from app.schemas.word_list import (
    WordListCreate,
    WordListDetailResponse,
    WordListImportRequest,
    WordListResponse,
    WordListUpdate,
)
from app.services import word_list_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/word-lists", response_model=list[WordListResponse])
def list_word_lists(
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
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


@router.post("/word-lists", response_model=WordListResponse, status_code=status.HTTP_201_CREATED)
def create_word_list(
    data: WordListCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    wl = word_list_service.create_word_list(session, data)
    return WordListResponse(
        id=wl.id,
        name=wl.name,
        level=wl.level,
        source=wl.source,
        description=wl.description,
        created_at=wl.created_at,
        updated_at=wl.updated_at,
        word_count=0,
    )


@router.patch("/word-lists/{word_list_id}", response_model=WordListResponse)
def update_word_list(
    word_list_id: int,
    data: WordListUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    try:
        wl = word_list_service.update_word_list(session, word_list_id, data)
        return WordListResponse(
            id=wl.id,
            name=wl.name,
            level=wl.level,
            source=wl.source,
            description=wl.description,
            created_at=wl.created_at,
            updated_at=wl.updated_at,
            word_count=word_list_service.word_count(session, word_list_id),
        )
    except WordListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/word-lists/{word_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_list(
    word_list_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    try:
        word_list_service.delete_word_list(session, word_list_id)
    except WordListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/word-lists/{word_list_id}/words",
    response_model=list[WordResponse],
    status_code=status.HTTP_201_CREATED,
)
def import_words(
    word_list_id: int,
    data: WordListImportRequest,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    """Import bulk words vào 1 list. Frontend parse CSV rồi gửi WordCreate[]."""
    try:
        created = word_list_service.import_words(session, word_list_id, data.words)
        return [WordResponse.model_validate(w) for w in created]
    except WordListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/word-lists/{word_list_id}/words/{word_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_word(
    word_list_id: int,
    word_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    """Xoá 1 từ khỏi list (và xoá luôn Word + Review)."""
    try:
        word_list_service.remove_word_from_list(session, word_list_id, word_id)
    except (WordListNotFoundError, WordNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/word-lists/{word_list_id}", response_model=WordListDetailResponse)
def get_word_list(
    word_list_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_admin),
):
    """Chi tiết 1 list — admin xem/quản lý từ trong list."""
    try:
        wl = word_list_service.get_word_list(session, word_list_id)
    except WordListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    words = word_list_service.get_word_list_words(session, word_list_id)
    return WordListDetailResponse(
        id=wl.id,
        name=wl.name,
        level=wl.level,
        source=wl.source,
        description=wl.description,
        created_at=wl.created_at,
        updated_at=wl.updated_at,
        word_count=len(words),
        words=[WordResponse.model_validate(w) for w in words],
    )
