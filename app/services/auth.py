from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from app.core.config import settings

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def authorize_google_redirect(request: Request) -> Any:
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


async def get_google_user_data(request: Request) -> dict[str, dict[str, Any]]:
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise ValueError("Không thể lấy thông tin từ Google")

    return {
        "google_data": {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
        }
    }
