"""Tập trung các enum dùng chung toàn app."""

from enum import StrEnum


class JLPTLevel(StrEnum):
    """Trình độ JLPT — dùng cho cả user.level và word.level."""

    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"


class WordType(StrEnum):
    """Loại từ vựng tiếng Nhật."""

    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE_I = "Adjective-i"
    ADJECTIVE_NA = "Adjective-na"
    ADVERB = "Adverb"
    PARTICLE = "Particle"


class WordSource(StrEnum):
    """Nguồn gốc bộ từ vựng."""

    MIMIKARA = "Mimikara"
    TANGO = "Tango"


class ReviewState(StrEnum):
    """Trạng thái FSRS của một card."""

    NEW = "New"
    LEARNING = "Learning"
    REVIEW = "Review"
    RELEARNING = "Relearning"


class ReviewRating(StrEnum):
    """Đánh giá của user khi review (FSRS)."""

    AGAIN = "Again"
    HARD = "Hard"
    GOOD = "Good"
    EASY = "Easy"
