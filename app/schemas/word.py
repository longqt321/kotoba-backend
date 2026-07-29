"""Word schemas — input/output cho từ vựng và examples/meanings."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import JLPTLevel, WordSource, WordType


class ExampleBase(BaseModel):
    japanese: str
    translation: str


class ExampleCreate(ExampleBase):
    pass


class ExampleResponse(ExampleBase):
    id: int
    word_id: int

    model_config = ConfigDict(from_attributes=True)


class MeaningBase(BaseModel):
    meaning: str


class MeaningCreate(MeaningBase):
    pass


class MeaningResponse(MeaningBase):
    id: int
    word_id: int

    model_config = ConfigDict(from_attributes=True)


class WordBase(BaseModel):
    word: str
    kanji: str | None = None
    level: JLPTLevel
    word_type: WordType
    source: WordSource
    topic: str | None = None


class WordCreate(WordBase):
    """Schema khi admin seed dữ liệu từ vựng."""

    examples: list[ExampleCreate] = []
    meanings: list[MeaningCreate] = []


class WordUpdate(BaseModel):
    word: str | None = None
    kanji: str | None = None
    level: JLPTLevel | None = None
    word_type: WordType | None = None
    source: WordSource | None = None
    topic: str | None = None


class WordResponse(WordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    examples: list[ExampleResponse] = []
    meanings: list[MeaningResponse] = []

    model_config = ConfigDict(from_attributes=True)
