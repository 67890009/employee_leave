from pydantic import BaseModel


class LeaveTypeReport(BaseModel):

    leave_type: str

    applied_count: int


class EmployeeReportResponse(BaseModel):

    employee_id: str

    employee_code: str

    employee_name: str

    department: str

    manager_name: str | None

    total_leave_requests: int

    paid_leave_used: int

    paid_leave_remaining: int

    leave_breakdown: list[LeaveTypeReport]


class DepartmentReportResponse(BaseModel):

    department_id: str

    department_name: str

    total_employees: int

    total_leave_requests: int

    paid_leave_used: int


class MonthlyReportResponse(BaseModel):

    month: int

    year: int

    total_leave_requests: int

    approved_requests: int

    pending_requests: int

    rejected_requests: int

    cancelled_requests: int

    paid_leave_used: int