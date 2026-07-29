"""User service — business logic cho user, không phụ thuộc HTTP layer."""

from sqlmodel import Session, select

from app.core.config import settings
from app.core.enums import JLPTLevel
from app.models.user import User


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_or_create_user(session: Session, email: str, name: str) -> User:
    """Tìm user theo email; nếu chưa có thì tạo mới với level mặc định N5.

    Đồng bộ lại is_admin theo ADMIN_EMAILS mỗi lần login — cho phép cấp/gỡ
    quyền admin chỉ bằng đổi env var, không cần sửa DB trực tiếp.
    """
    is_admin = email.lower() in settings.admin_emails
    user = session.exec(select(User).where(User.email == email)).first()
    if user is not None:
        if user.is_admin != is_admin:
            user.is_admin = is_admin
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    user = User(email=email, name=name, level=JLPTLevel.N5, is_admin=is_admin)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_level(session: Session, user: User, level: JLPTLevel) -> User:
    user.level = level
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
