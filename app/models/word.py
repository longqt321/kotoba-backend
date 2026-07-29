"""Word model — từ vựng tiếng Nhật kèm examples và meanings."""

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.core.enums import JLPTLevel, WordSource, WordType


class Word(SQLModel, table=True):
    __tablename__ = "words"

    id: int | None = Field(default=None, primary_key=True)
    word: str = Field(index=True)
    kanji: str | None = None
    level: JLPTLevel
    word_type: WordType
    source: WordSource
    topic: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    examples: list["Example"] = Relationship(
        back_populates="word",
        cascade_delete=True,
    )
    meanings: list["Meaning"] = Relationship(
        back_populates="word",
        cascade_delete=True,
    )


class Example(SQLModel, table=True):
    __tablename__ = "examples"

    id: int | None = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id", ondelete="CASCADE")
    japanese: str
    translation: str

    word: Word = Relationship(back_populates="examples")


class Meaning(SQLModel, table=True):
    __tablename__ = "meanings"

    id: int | None = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id", ondelete="CASCADE")
    meaning: str

    word: Word = Relationship(back_populates="meanings")
