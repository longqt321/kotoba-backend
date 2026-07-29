"""Unit test schema validation — Pydantic chặn input sai."""

import pytest
from pydantic import ValidationError

from app.core.enums import WordSource, WordType
from app.schemas.review import ReviewSubmitRequest
from app.schemas.user import UserBase
from app.schemas.word import WordCreate

pytestmark = pytest.mark.unit


class TestSchemaValidation:
    def test_word_create_parses_nested(self):
        data = WordCreate(
            word="食べる",
            level="N5",
            word_type=WordType.VERB,
            source=WordSource.MIMIKARA,
            examples=[{"japanese": "ご飯を食べる", "translation": "eat rice"}],
            meanings=[{"meaning": "to eat"}],
        )
        assert data.word == "食べる"
        assert len(data.examples) == 1
        assert len(data.meanings) == 1

    def test_review_submit_invalid_rating_raises(self):
        with pytest.raises(ValidationError):
            ReviewSubmitRequest(rating="not-a-rating")

    def test_user_base_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserBase(email="not-an-email", name="Alice")
