"""User schemas — input/output cho auth flow."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import JLPTLevel


class UserBase(BaseModel):
    email: EmailStr
    name: str
    level: JLPTLevel = JLPTLevel.N5


class UserCreate(UserBase):
    """Schema khi tạo user từ Google OAuth callback."""


class UserUpdate(BaseModel):
    name: str | None = None
    level: JLPTLevel | None = None


class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
