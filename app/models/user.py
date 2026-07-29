"""User model — auth qua Google, lưu tên + email cơ bản."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from app.core.enums import JLPTLevel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    level: JLPTLevel = Field(default=JLPTLevel.N5)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
