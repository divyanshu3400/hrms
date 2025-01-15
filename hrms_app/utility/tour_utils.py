from .leave_utils import format_date
from django.conf import settings


def get_employee_requested_tour(user, status=None):
    leave_status = status if status is not None else settings.PENDING
    employee_leaves = []
    employees = user.employees.all()
    for employee in employees:
        employee_leaves.extend(
            [
                {
                    "leaveApplication": leaveApplication,
                    "start_date": format_date(leaveApplication.startDate),
                    "end_date": format_date(leaveApplication.endDate),
                } for leaveApplication in employee.tours.filter(status=leave_status)
            ]
        )
    return employee_leaves
