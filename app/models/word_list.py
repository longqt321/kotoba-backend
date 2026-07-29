"""WordList models — danh sách từ vựng theo giáo trình + liên kết user chọn list."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, UniqueConstraint

from app.core.enums import JLPTLevel, WordSource


class WordList(SQLModel, table=True):
    __tablename__ = "word_lists"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    level: JLPTLevel
    source: WordSource
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WordListEntry(SQLModel, table=True):
    __tablename__ = "word_list_entries"
    __table_args__ = (UniqueConstraint("word_list_id", "word_id", name="uq_wle_list_word"),)

    id: int | None = Field(default=None, primary_key=True)
    word_list_id: int = Field(foreign_key="word_lists.id", ondelete="CASCADE")
    word_id: int = Field(foreign_key="words.id", ondelete="CASCADE")


class UserWordList(SQLModel, table=True):
    __tablename__ = "user_word_lists"
    __table_args__ = (UniqueConstraint("user_id", "word_list_id", name="uq_uwl_user_list"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    word_list_id: int = Field(foreign_key="word_lists.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
