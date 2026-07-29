"""WordList schemas — input/output cho danh sách từ vựng và import."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import JLPTLevel, WordSource
from app.schemas.word import WordCreate, WordResponse


class WordListBase(BaseModel):
    name: str
    level: JLPTLevel
    source: WordSource
    description: str | None = None


class WordListCreate(WordListBase):
    pass


class WordListUpdate(BaseModel):
    name: str | None = None
    level: JLPTLevel | None = None
    source: WordSource | None = None
    description: str | None = None


class WordListResponse(WordListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    word_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class WordListDetailResponse(WordListResponse):
    words: list[WordResponse] = []


class WordListImportRequest(BaseModel):
    """Request body khi admin import CSV vào 1 list.

    Frontend parse CSV thành WordCreate[] gửi lên.
    """
    words: list[WordCreate]
