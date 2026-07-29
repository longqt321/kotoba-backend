"""UserWordList service — user chọn/bỏ chọn list để học.

Chọn list: seed Review (due=now) cho các từ chưa có Review của user này —
theo pattern seed-on-create cũ (tránh chicken-egg, từ xuất hiện ngay trong /due).
Bỏ chọn: chỉ xoá UserWordList, giữ nguyên Review để không mất tiến độ FSRS
nếu user chọn lại list sau này.
"""

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.core.exceptions import WordListNotFoundError
from app.models.review import Review
from app.models.word_list import UserWordList, WordListEntry
from app.services.word_list_service import get_word_list


def list_selected_word_list_ids(session: Session, user_id: int) -> list[int]:
    return list(
        session.exec(
            select(UserWordList.word_list_id).where(UserWordList.user_id == user_id)
        ).all()
    )


def select_word_list(session: Session, user_id: int, word_list_id: int) -> None:
    get_word_list(session, word_list_id)  # 404 nếu list không tồn tại

    existing = session.exec(
        select(UserWordList).where(
            UserWordList.user_id == user_id, UserWordList.word_list_id == word_list_id
        )
    ).first()
    if existing is not None:
        return

    session.add(UserWordList(user_id=user_id, word_list_id=word_list_id))

    word_ids = session.exec(
        select(WordListEntry.word_id).where(WordListEntry.word_list_id == word_list_id)
    ).all()
    if word_ids:
        already_reviewed = set(
            session.exec(
                select(Review.word_id).where(
                    Review.user_id == user_id, Review.word_id.in_(word_ids)
                )
            ).all()
        )
        now = datetime.now(UTC)
        for word_id in word_ids:
            if word_id not in already_reviewed:
                session.add(Review(user_id=user_id, word_id=word_id, due=now))

    session.commit()


def deselect_word_list(session: Session, user_id: int, word_list_id: int) -> None:
    existing = session.exec(
        select(UserWordList).where(
            UserWordList.user_id == user_id, UserWordList.word_list_id == word_list_id
        )
    ).first()
    if existing is None:
        raise WordListNotFoundError(word_list_id)

    session.delete(existing)
    session.commit()
