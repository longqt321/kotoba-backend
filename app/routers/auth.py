from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.config import settings
from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import user_service
from app.services.auth import authorize_google_redirect, get_google_user_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    return await authorize_google_redirect(request)


@router.get("/callback")
async def auth_callback(request: Request, session: Session = Depends(get_session)):
    try:
        data = await get_google_user_data(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Xác thực thất bại: {str(e)}") from e

    google_data = data["google_data"]
    user = user_service.get_or_create_user(
        session, email=google_data["email"], name=google_data["name"]
    )
    request.session["user_id"] = user.id
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=204)
async def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)
