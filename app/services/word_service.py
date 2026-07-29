"""Word service — query từ vựng (read-only cho user thường) + query từ đến hạn.

Từ user thường không còn tạo/xoá Word trực tiếp — việc đó chuyển sang admin
qua word_list_service.import_words. list_words vẫn giữ để hiển thị (không lọc
theo list — dùng cho mục đích tra cứu chung, ví dụ trong word-list detail).
"""

from datetime import UTC, datetime

from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.enums import JLPTLevel
from app.core.exceptions import WordNotFoundError
from app.models.review import Review
from app.models.word import Word
from app.models.word_list import UserWordList, WordListEntry


def list_words(
    session: Session,
    level: JLPTLevel | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Word]:
    statement = select(Word)
    if level is not None:
        statement = statement.where(Word.level == level)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_word(session: Session, word_id: int) -> Word:
    word = session.get(Word, word_id)
    if word is None:
        raise WordNotFoundError(word_id)
    return word


def get_due_words(session: Session, user_id: int, now: datetime | None = None) -> list[Word]:
    """Từ vựng đến hạn review của user, giới hạn trong các list user đã chọn.

    Bao gồm: Review có due <= now, hoặc chưa được review lần nào
    (last_review IS NULL) — dù due đã bị set về sau thời điểm hiện tại.
    Review của các list user đã bỏ chọn vẫn tồn tại trong DB (giữ lịch sử
    FSRS) nhưng bị loại khỏi kết quả này qua điều kiện word_id IN (list đã chọn).
    """
    if now is None:
        now = datetime.now(UTC)

    selected_lists = select(UserWordList.word_list_id).where(UserWordList.user_id == user_id)
    selected_word_ids = select(WordListEntry.word_id).where(
        WordListEntry.word_list_id.in_(selected_lists)
    )

    word_ids = select(Review.word_id).where(
        Review.user_id == user_id,
        Review.word_id.in_(selected_word_ids),
        or_(Review.due <= now, Review.last_review.is_(None)),
    )
    return list(session.exec(select(Word).where(Word.id.in_(word_ids))).all())
