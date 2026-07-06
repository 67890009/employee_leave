from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token
from app.auth.service import AuthService
from app.common.enums import UserRole
from app.db.session import get_db
from app.users.model import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Returns the currently authenticated user.
    """

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    return await AuthService.get_current_user(
        db=db,
        user_id=UUID(user_id),
    )


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allows only Admin users.
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return current_user


async def get_current_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allows only Manager users.
    """

    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return current_user


async def get_current_hr(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allows only HR users.
    """

    if current_user.role != UserRole.HR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return current_user


async def get_current_employee(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Returns any authenticated user.
    """

    return current_user

def require_roles(*roles: UserRole):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
        return current_user
    return dependency