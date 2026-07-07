from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import (
    AccessTokenResponse,
    LoginRequest,
    TokenResponse,
)
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)


class AuthService:

    @staticmethod
    async def login(
        db: AsyncSession,
        login_data: LoginRequest,
    ) -> TokenResponse:

        user = await AuthRepository.get_user_by_email(
            db=db,
            email=login_data.email,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        if not verify_password(
            login_data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        payload = {
            "sub": str(user.id),
            "role": user.role.value,
        }

        access_token = create_access_token(payload)

        refresh_token = create_refresh_token(payload)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    async def refresh(
        refresh_token: str,
    ) -> AccessTokenResponse:

        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        access_token = create_access_token(
            {
                "sub": payload["sub"],
                "role": payload["role"],
            }
        )

        return AccessTokenResponse(
            access_token=access_token,
        )

    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        user_id: UUID,
    ):
        user = await AuthRepository.get_user_by_id(
            db=db,
            user_id=user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        return user
    
    @staticmethod
    async def login_with_google_email(db: AsyncSession, email: str) -> TokenResponse:
        user = await AuthRepository.get_user_by_email(db=db, email=email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No account exists for this email. Contact your administrator.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        payload = {"sub": str(user.id), "role": user.role.value}
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    
