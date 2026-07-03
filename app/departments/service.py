from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.departments.model import Department
from app.departments.repository import DepartmentRepository
from app.departments.schema import DepartmentCreate, DepartmentUpdate


class DepartmentService:

    @staticmethod
    async def create_department(db: AsyncSession, data: DepartmentCreate) -> Department:
        if await DepartmentRepository.get_by_name(db, data.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists.",
            )

        department = Department(
            name=data.name,
            description=data.description,
        )

        return await DepartmentRepository.create(db, department)

    @staticmethod
    async def get_department(db: AsyncSession, department_id: UUID) -> Department:
        department = await DepartmentRepository.get_by_id(db, department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )
        return department

    @staticmethod
    async def update_department(
        db: AsyncSession, department_id: UUID, data: DepartmentUpdate
    ) -> Department:
        department = await DepartmentService.get_department(db, department_id)

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != department.name:
            existing = await DepartmentRepository.get_by_name(db, update_data["name"])
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department name already exists.",
                )

        for field, value in update_data.items():
            setattr(department, field, value)

        return department

    @staticmethod
    async def deactivate_department(db: AsyncSession, department_id: UUID) -> Department:
        department = await DepartmentService.get_department(db, department_id)

        if not department.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department is already inactive.",
            )

        if await DepartmentRepository.has_active_employees(db, department_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate a department with active employees assigned.",
            )

        return await DepartmentRepository.deactivate(db, department)

    @staticmethod
    async def list_departments(
        db: AsyncSession,
        page: int,
        page_size: int,
        is_active: bool | None = None,
    ) -> tuple[list[Department], int]:
        return await DepartmentRepository.list_departments(db, page, page_size, is_active)