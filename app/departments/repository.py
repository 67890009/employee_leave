from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.departments.model import Department


class DepartmentRepository:

    @staticmethod
    async def create(db: AsyncSession, department: Department) -> Department:
        db.add(department)
        await db.flush()
        await db.refresh(department)
        return department

    @staticmethod
    async def get_by_id(db: AsyncSession, department_id: UUID) -> Department | None:
        result = await db.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Department | None:
        result = await db.execute(
            select(Department).where(Department.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_departments(
        db: AsyncSession,
        page: int,
        page_size: int,
        is_active: bool | None = None,
    ) -> tuple[list[Department], int]:
        query = select(Department)
        count_query = select(func.count()).select_from(Department)

        if is_active is not None:
            query = query.where(Department.is_active == is_active)
            count_query = count_query.where(Department.is_active == is_active)

        total = (await db.execute(count_query)).scalar_one()

        query = query.order_by(Department.name).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)

        return list(result.scalars().all()), total

    @staticmethod
    async def deactivate(db: AsyncSession, department: Department) -> Department:
        department.is_active = False
        await db.flush()
        await db.refresh(department)
        return department

    @staticmethod
    async def has_active_employees(db: AsyncSession, department_id: UUID) -> bool:
        from app.users.model import User

        result = await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.department_id == department_id, User.is_active == True)
        )
        return result.scalar_one() > 0