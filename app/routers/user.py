"""User router — user tự quản lý level và danh sách từ vựng (chọn/bỏ chọn)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.exceptions import WordListNotFoundError
from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.word_list import WordListResponse
from app.services import user_service, user_word_list_service, word_list_service

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserResponse)
def update_my_level(
    data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật JLPT level của user."""
    if data.level is None and data.name is None:
        raise HTTPException(status_code=400, detail="Cần ít nhất 1 field để cập nhật")
    return user_service.update_user_level(
        session, current_user, data.level or current_user.level
    )


@router.get("/me/word-lists", response_model=list[WordListResponse])
def list_my_word_lists(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Danh sách các list user đã chọn học, kèm word_count."""
    list_ids = user_word_list_service.list_selected_word_list_ids(session, current_user.id)  # type: ignore
    result: list[WordListResponse] = []
    for lid in list_ids:
        try:
            wl = word_list_service.get_word_list(session, lid)
            count = word_list_service.word_count(session, lid)
            result.append(
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
            )
        except WordListNotFoundError:
            continue
    return result


@router.post("/me/word-lists/{word_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def select_word_list(
    word_list_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Chọn 1 list để học — seed Review cho các từ trong list (nếu chưa có)."""
    try:
        user_word_list_service.select_word_list(session, current_user.id, word_list_id)  # type: ignore
    except WordListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Word list not found") from e


@router.delete("/me/word-lists/{word_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def deselect_word_list(
    word_list_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Bỏ chọn 1 list — giữ Review, chỉ xoá UserWordList (có thể chọn lại sau)."""
    try:
        user_word_list_service.deselect_word_list(session, current_user.id, word_list_id)  # type: ignore
    except WordListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Word list not found") from e
