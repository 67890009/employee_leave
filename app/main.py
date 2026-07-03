from fastapi import FastAPI
from sqlalchemy import text
from app.leave_types.router import router as leave_type_router
from app.auth.router import router as auth_router
from app.core.config import settings
from app.db.session import AsyncSessionLocal
import app.db.model
from app.users.router import router as users_router
from app.leave_requests.router import router as leave_request_router
from app.departments.router import router as departments_router
from app.common.exceptions import register_exception_handlers
from app.reports.router import router as report_router

app = FastAPI()
register_exception_handlers(app)
app.include_router(leave_type_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(leave_request_router)
app.include_router(departments_router)
app.include_router(report_router)


@app.get("/")
async def root():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
    return {
        "database": result.scalar(),
        "jwt_algorithm": settings.JWT_ALGORITHM,
    }