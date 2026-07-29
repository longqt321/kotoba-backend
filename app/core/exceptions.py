"""Domain exceptions — service raise, router convert sang HTTPException.

Giữ service framework-agnostic (không import fastapi ở đây).
"""


class AppBaseException(Exception):
    """Base exception chung của app — dễ bắt tổng quát ở global handler."""


class NotFoundError(AppBaseException):
    """Resource không tồn tại — router map sang HTTP 404."""


class WordNotFoundError(NotFoundError):
    def __init__(self, word_id: int | None = None) -> None:
        msg = "Word not found" if word_id is None else f"Word {word_id} not found"
        super().__init__(msg)


class ReviewNotFoundError(NotFoundError):
    def __init__(self, review_id: int | None = None) -> None:
        msg = "Review not found" if review_id is None else f"Review {review_id} not found"
        super().__init__(msg)


class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int | None = None) -> None:
        msg = "User not found" if user_id is None else f"User {user_id} not found"
        super().__init__(msg)


class WordListNotFoundError(NotFoundError):
    def __init__(self, word_list_id: int | None = None) -> None:
        msg = (
            "Word list not found"
            if word_list_id is None
            else f"Word list {word_list_id} not found"
        )
        super().__init__(msg)


class NotAuthenticatedError(AppBaseException):
    """Chưa đăng nhập — dependency get_current_user raise, router map sang HTTP 401."""
