from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.model import User


class AuthRepository:

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()