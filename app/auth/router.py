from fastapi import APIRouter, Depends, Request, HTTPException, status
from starlette.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.oauth import oauth
from app.auth.dependencies import get_current_employee
from app.auth.schemas import (
    AccessTokenResponse,
    LoginRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.db.session import get_db
from app.users.model import User
from app.auth.schemas import RefreshTokenRequest

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await AuthService.login(
        db=db,
        login_data=login_data,
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
async def refresh_token(
    data: RefreshTokenRequest,
):
    return await AuthService.refresh(
        refresh_token=data.refresh_token,
    )


@router.post("/logout")
async def logout():
    """
    JWT logout is handled on the client side.

    The client should remove both the access token
    and refresh token from storage.
    """

    return {
        "message": "Logged out successfully."
    }


@router.get("/me")
async def get_logged_in_user(
    current_user: User = Depends(get_current_employee),
):
    return {
        "id": current_user.id,
        "employee_code": current_user.employee_code,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role,
        "department_id": current_user.department_id,
        "manager_id": current_user.manager_id,
        "is_active": current_user.is_active,
    }

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if user_info is None or "email" not in user_info:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google.")

    return await AuthService.login_with_google_email(db=db, email=user_info["email"])