"""factory_boy factories — sinh dữ liệu test theo model thật."""

from datetime import UTC, datetime

import factory
from factory.faker import Faker as FactoryFaker

from app.core.enums import JLPTLevel, ReviewState, WordSource, WordType
from app.models.review import Review
from app.models.user import User
from app.models.word import Word


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = FactoryFaker("name")
    level = JLPTLevel.N5


class WordFactory(factory.Factory):
    class Meta:
        model = Word

    word = factory.Sequence(lambda n: f"word{n}")
    kanji = "食べる"
    level = JLPTLevel.N5
    word_type = WordType.VERB
    source = WordSource.MIMIKARA
    topic = "Food"


class ReviewFactory(factory.Factory):
    class Meta:
        model = Review

    user_id = None  # phải truyền vào khi dùng
    word_id = None  # phải truyền vào khi dùng
    state = ReviewState.NEW
    step = 0
    due = factory.LazyFunction(lambda: datetime.now(UTC))
