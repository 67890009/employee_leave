from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.leave_types.model import LeaveType
from app.leave_types.repository import LeaveTypeRepository
from app.leave_types.schema import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
)


class LeaveTypeService:

    def __init__(self):
        self.repository = LeaveTypeRepository()

    async def create_leave_type(
        self,
        db: AsyncSession,
        data: LeaveTypeCreate
    ) -> LeaveType:

        existing = await self.repository.get_by_name(db, data.name)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Leave type already exists."
            )

        leave_type = LeaveType(
            name=data.name,
            description=data.description,
            max_days_per_year=data.max_days_per_year,
        )

        return await self.repository.create(db, leave_type)

    async def get_leave_type(
        self,
        db: AsyncSession,
        leave_type_id: UUID
    ) -> LeaveType:

        leave_type = await self.repository.get_by_id(db, leave_type_id)

        if not leave_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found."
            )

        return leave_type

    async def get_all_leave_types(
        self,
        db: AsyncSession
    ) -> list[LeaveType]:

        return await self.repository.get_all(db)

    async def update_leave_type(
        self,
        db: AsyncSession,
        leave_type_id: UUID,
        data: LeaveTypeUpdate
    ) -> LeaveType:

        leave_type = await self.repository.get_by_id(db, leave_type_id)

        if not leave_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found."
            )

        if data.name is not None:

            existing = await self.repository.get_by_name(db, data.name)

            if existing and existing.id != leave_type.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Leave type already exists."
                )

            leave_type.name = data.name

        if data.description is not None:
            leave_type.description = data.description

        if data.max_days_per_year is not None:
            leave_type.max_days_per_year = data.max_days_per_year

        if data.is_active is not None:
            leave_type.is_active = data.is_active

        return await self.repository.update(db, leave_type)

    async def delete_leave_type(
        self,
        db: AsyncSession,
        leave_type_id: UUID
    ) -> LeaveType:

        leave_type = await self.repository.get_by_id(db, leave_type_id)

        if not leave_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found."
            )
        if not leave_type.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Leave type is already inactive.'
            )
        leave_type.is_active = False
        return await self.repository.update(db, leave_type)
