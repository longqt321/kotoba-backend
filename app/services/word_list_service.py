"""WordList service — CRUD danh sách từ vựng + import/xoá từ trong list.

Word không có owner và không seed Review khi admin import (khác với
word_service.create_word cũ) — Review chỉ được seed khi user chọn học 1 list,
xem user_word_list_service.select_word_list.
"""

from datetime import UTC, datetime

from sqlmodel import Session, func, select

from app.core.exceptions import WordListNotFoundError, WordNotFoundError
from app.models.review import Review
from app.models.word import Example, Meaning, Word
from app.models.word_list import WordList, WordListEntry
from app.schemas.word import WordCreate
from app.schemas.word_list import WordListCreate, WordListUpdate


def word_count(session: Session, word_list_id: int) -> int:
    return session.exec(
        select(func.count()).where(WordListEntry.word_list_id == word_list_id)
    ).one()


def list_word_lists(session: Session) -> list[tuple[WordList, int]]:
    """Trả về (WordList, word_count) cho mọi list — dùng cho response có word_count."""
    lists = session.exec(select(WordList)).all()
    return [(wl, word_count(session, wl.id)) for wl in lists]  # type: ignore


def get_word_list(session: Session, word_list_id: int) -> WordList:
    word_list = session.get(WordList, word_list_id)
    if word_list is None:
        raise WordListNotFoundError(word_list_id)
    return word_list


def get_word_list_words(session: Session, word_list_id: int) -> list[Word]:
    word_ids = select(WordListEntry.word_id).where(WordListEntry.word_list_id == word_list_id)
    return list(session.exec(select(Word).where(Word.id.in_(word_ids))).all())


def create_word_list(session: Session, data: WordListCreate) -> WordList:
    word_list = WordList(
        name=data.name,
        level=data.level,
        source=data.source,
        description=data.description,
    )
    session.add(word_list)
    session.commit()
    session.refresh(word_list)
    return word_list


def update_word_list(session: Session, word_list_id: int, data: WordListUpdate) -> WordList:
    word_list = get_word_list(session, word_list_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(word_list, key, value)
    word_list.updated_at = datetime.now(UTC)
    session.add(word_list)
    session.commit()
    session.refresh(word_list)
    return word_list


def delete_word_list(session: Session, word_list_id: int) -> None:
    """Xoá 1 list + toàn bộ Word thuộc list đó (và Review liên quan).

    Cascade tay giống word_service.delete_word: Review không có relationship
    ngược tới Word/WordList nên SQLite không tự cascade — phải xoá thủ công
    theo thứ tự Review -> Word (cascade Example/Meaning qua relationship) ->
    WordListEntry -> WordList.
    """
    word_list = get_word_list(session, word_list_id)

    entries = session.exec(
        select(WordListEntry).where(WordListEntry.word_list_id == word_list_id)
    ).all()
    word_ids = [e.word_id for e in entries]

    if word_ids:
        reviews = session.exec(select(Review).where(Review.word_id.in_(word_ids))).all()
        for review in reviews:
            session.delete(review)

        words = session.exec(select(Word).where(Word.id.in_(word_ids))).all()
        for word in words:
            session.delete(word)

    for entry in entries:
        session.delete(entry)

    session.delete(word_list)
    session.commit()


def import_words(
    session: Session, word_list_id: int, words: list[WordCreate]
) -> list[Word]:
    """Import nhiều Word vào 1 list trong 1 transaction. Không seed Review."""
    get_word_list(session, word_list_id)  # 404 nếu list không tồn tại

    created: list[Word] = []
    for data in words:
        word = Word(
            word=data.word,
            kanji=data.kanji,
            level=data.level,
            word_type=data.word_type,
            source=data.source,
            topic=data.topic,
        )
        session.add(word)
        session.flush()

        for ex in data.examples:
            session.add(
                Example(word_id=word.id, japanese=ex.japanese, translation=ex.translation)
            )
        for mn in data.meanings:
            session.add(Meaning(word_id=word.id, meaning=mn.meaning))

        session.add(WordListEntry(word_list_id=word_list_id, word_id=word.id))
        created.append(word)

    session.commit()
    for word in created:
        session.refresh(word)
    return created


def remove_word_from_list(session: Session, word_list_id: int, word_id: int) -> None:
    """Xoá 1 từ khỏi list — xoá luôn Word (và Review liên quan) vì Word chỉ thuộc 1 list."""
    entry = session.exec(
        select(WordListEntry).where(
            WordListEntry.word_list_id == word_list_id, WordListEntry.word_id == word_id
        )
    ).first()
    if entry is None:
        raise WordNotFoundError(word_id)

    reviews = session.exec(select(Review).where(Review.word_id == word_id)).all()
    for review in reviews:
        session.delete(review)

    word = session.get(Word, word_id)
    if word is not None:
        session.delete(word)

    session.delete(entry)
    session.commit()
