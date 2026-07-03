from pydantic import BaseModel


class LeaveTypeCount(BaseModel):

    leave_type: str

    applied: int


class EmployeeReportResponse(BaseModel):

    employee_name: str

    department: str

    total_leave_requests: int

    paid_leave_used: int

    paid_leave_remaining: int

    leave_breakdown: list[LeaveTypeCount]


class DepartmentReportResponse(BaseModel):

    department: str

    total_employees: int

    total_leave_requests: int

    paid_leave_used: int

    paid_leave_remaining: int


class MonthlyReportResponse(BaseModel):

    month: int

    year: int

    total_leave_requests: int

    paid_leave_used: int

    approved: int

    pending: int

    rejected: int

    cancelled: int