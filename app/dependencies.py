from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.database import engine
from app.models.user import User
from app.services import user_service


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    """Lấy user hiện tại từ session cookie (đã ký bởi SessionMiddleware)."""
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chưa đăng nhập")

    user = user_service.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chưa đăng nhập")

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Yêu cầu current_user phải có quyền admin, ngược lại raise 403."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yêu cầu quyền admin")
    return current_user
