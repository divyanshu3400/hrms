from django.utils import timezone
from django.core.exceptions import ValidationError
from hrms_app.models import (
    LeaveApplication,
    AttendanceLog,
    UserTour,
    LeaveDayChoiceAdjustment,
)
from hrms_app.hrms.utils import get_non_working_days
from django.conf import settings
from hrms_app.hrms.utils import *


def get_employee_requested_leave(user, status=None):
    leave_status = status if status is not None else settings.PENDING

    if user.is_superuser:
        # If the user is a superuser, fetch all leave applications with the given status
        employee_leaves = [
            {
                "leaveApplication": leaveApplication,
                "start_date": format_date(leaveApplication.startDate),
                "end_date": format_date(leaveApplication.endDate),
            }
            for leaveApplication in LeaveApplication.objects.filter(
                status__in=[leave_status, settings.RECOMMEND]
            )
        ]
    else:
        # Fetch leave applications for employees assigned to the user
        employee_leaves = []
        employees = user.employees.all()
        for employee in employees:
            employee_leaves.extend(
                [
                    {
                        "leaveApplication": leaveApplication,
                        "start_date": format_date(leaveApplication.startDate),
                        "end_date": format_date(leaveApplication.endDate),
                    }
                    for leaveApplication in employee.leaves.filter(
                        status__in=[leave_status, settings.PENDING_CANCELLATION]
                    )
                ]
            )
        if user.personal_detail.designation.department.department == "admin":
            employee_leaves.extend(
                {
                    "leaveApplication": leaveApplication,
                    "start_date": format_date(leaveApplication.startDate),
                    "end_date": format_date(leaveApplication.endDate),
                }
                for leaveApplication in LeaveApplication.objects.filter(
                    status=settings.RECOMMEND
                )
            )
    return employee_leaves


def get_employee_requested_tour(user, status=None):
    tour_status = status if status is not None else settings.PENDING
    if user.is_superuser:
        # Fetch all tours with the given status for superusers
        return UserTour.objects.filter(status=tour_status)
    else:
        # Fetch tours applied by employees assigned to the user
        return UserTour.objects.filter(
            applied_by__in=user.employees.all(),
            status__in=[tour_status, settings.EXTENDED],
        )


def get_regularization_requests(user, status=None):
    reg_status = status if status is not None else settings.PENDING

    if user.is_superuser:
        # Fetch all regularization requests with the given status for superusers
        return AttendanceLog.objects.filter(is_submitted=True, status=reg_status)
    elif user.personal_detail.designation.department.department == "admin":
        return AttendanceLog.objects.filter(
            is_submitted=True,
            status__in=[reg_status],
            applied_by__in=user.employees.all(),
        ) | AttendanceLog.objects.filter(is_submitted=True, status=settings.RECOMMEND)

    else:
        # Fetch regularization requests applied by employees assigned to the user
        return AttendanceLog.objects.filter(
            applied_by__in=user.employees.all(), is_submitted=True, status=reg_status
        )


def format_date(date):
    from django.utils.timezone import make_aware, make_naive

    naive_date = make_naive(date)
    output_format = "%Y-%m-%d"
    formatted_date = naive_date.strftime(output_format)
    return formatted_date


from django.core.exceptions import ValidationError
from django.utils import timezone


class LeavePolicyManager:
    def __init__(
        self, user, leave_type, start_date, end_date, start_day_choice, end_day_choice
    ):
        self.user = user
        self.leave_type = leave_type
        self.start_date = start_date
        self.adjusted_start_date = start_date
        self.end_date = end_date
        self.start_day_choice = start_day_choice
        self.end_day_choice = end_day_choice

        # Calculate booked leave using the new function
        self.booked_leave = calculate_total_leave_days(
            start_date, end_date, start_day_choice, end_day_choice
        )

    def validate_policies(self):
        """
        Validates all leave policies applicable to the leave application.
        """

        self.validate_overlapping_leaves()
        self.validate_consecutive_leave_restrictions()

        if self.leave_type.leave_type_short_code == "CL":
            self.apply_cl_policy()
        elif self.leave_type.leave_type_short_code == "EL":
            self.apply_el_policy()

    def validate_min_days(self):
        if self.booked_leave < self.leave_type.min_days_limit:  # 1<0.5
            raise ValidationError("Booked leave is less than the minimum days limit.")

    def validate_overlapping_leaves(self):
        """
        Checks for overlapping leave applications for the user.
        """
        overlapping_leaves = LeaveApplication.objects.filter(
            appliedBy=self.user,
            endDate__date__range=(self.start_date.date(), self.end_date.date()),
            status__in=[
                settings.APPROVED,
                settings.PENDING,
                settings.PENDING_CANCELLATION,
            ],
        )
        if overlapping_leaves.exists():
            raise ValidationError(
                "There is an overlapping leave application in the selected date range."
            )


    def apply_cl_policy(self):
        """
        Applies Casual Leave specific policies.
        """
        self.apply_min_notice_days_policy()
        self.validate_min_days()
        self.apply_max_days_limit_policy()

    def apply_el_policy(self):
        """
        Applies Earned Leave specific policies.
        """
        el_allowed_days = self.leave_type.allowed_days_per_year
        el_min_days = self.leave_type.min_days_limit
        el_max_days = self.leave_type.max_days_limit

        if el_min_days and self.booked_leave < el_min_days:
            raise ValidationError(
                f"EL can be applied for a minimum of {el_min_days} days."
            )
        if el_max_days and self.booked_leave > el_max_days:
            raise ValidationError(
                f"EL can be applied for a maximum of {el_max_days} days."
            )

        current_fy_start, current_fy_end = get_current_financial_year()
        el_application_count = LeaveApplication.objects.filter(
            leave_type__leave_type_short_code="EL",
            appliedBy=self.user,
            startDate__gte=current_fy_start,
            startDate__lte=current_fy_end,
            status__in=[settings.APPROVED, settings.PENDING_CANCELLATION],
        ).count()

        if el_application_count >= el_allowed_days:
            raise ValidationError(
                f"EL can be applied a maximum of {el_allowed_days} times in the financial year."
            )

    def apply_min_notice_days_policy(self):
        """
        Applies minimum notice days policy for Casual Leave.
        """
        min_notice_days = self.leave_type.min_notice_days
        if (self.start_date.date() - timezone.now().date()).days < min_notice_days:
            raise ValidationError(
                f"{self.leave_type.leave_type_short_code} should be applied at least {min_notice_days} days in advance."
            )

    def apply_max_days_limit_policy(self):
        """
        Applies maximum days limit policy for Casual Leave.
        """
        max_days = self.leave_type.max_days_limit
        if self.booked_leave > max_days:
            raise ValidationError(
                f"{self.leave_type.leave_type_short_code} can be applied for a maximum of {max_days} days."
            )
    def validate_consecutive_leave_restrictions(self):
        """
        Enforce the consecutive leave restrictions based on the `LeaveType` settings.
        """
        last_leave = (
            LeaveApplication.objects.filter(
                appliedBy=self.user,
                status__in=[
                    settings.APPROVED,
                    settings.PENDING,
                    settings.PENDING_CANCELLATION,
                ],
            )
            .order_by("-endDate")
            .first()
        )

        if not last_leave:
            return  # No previous leaves to check against

        last_leave_type = last_leave.leave_type
        last_end_date = (
            timezone.localtime(last_leave.endDate).date()
            if timezone.is_aware(last_leave.endDate)
            else last_leave.endDate.date()
        )
        last_end_day_choice = last_leave.endDayChoice
        days_between = calculate_day_difference_btn_last_current_leave(
            last_leave_date=last_end_date,
            current_leave_date=self.start_date.date(),
            last_end_day_choice=last_end_day_choice,
            current_start_day_choice=self.start_day_choice,
        )
        non_work_days = get_non_working_days(
            start=last_end_date, end=self.start_date.date()
        )
        if (
            self.leave_type.leave_type_short_code == "CL"
            and last_leave.leave_type.leave_type_short_code == "CL"
        ):
            days_between -= non_work_days
        if (
            last_leave_type in self.leave_type.restricted_after_leave_types.all()
            and days_between <= 0
        ):
            raise ValidationError(
                f"You cannot apply for {self.leave_type} immediately after {last_leave_type}. "
                f"Please choose a different leave type or wait a few days."
            )


from django.utils import timezone


def calculate_day_difference_btn_last_current_leave(last_leave_date, current_leave_date, last_end_day_choice, current_start_day_choice):
    """
    Calculate total leave days between the start and end dates, considering start and end day choices.
    Uses database-stored adjustment values for flexibility.
    Ensures the result is always positive and handles timezone-aware dates.
    """
    # Debugging: Log the initial inputs
    if last_leave_date > current_leave_date:
        last_leave_date, current_leave_date = current_leave_date, last_leave_date
    # Calculate the total number of days between the dates
    total_days = (current_leave_date - last_leave_date).days
    if last_end_day_choice == settings.FIRST_HALF:
        total_days -=0.5
    if current_start_day_choice == settings.SECOND_HALF:
        total_days -=0.5
    final_days = max(float(total_days), 0.0)
    return final_days


def calculate_total_leave_days(start_date, end_date, start_day_choice, end_day_choice):
    """
    Calculate total leave days between the start and end dates, considering start and end day choices.
    Uses database-stored adjustment values for flexibility.
    Ensures the result is always positive.
    """
    if start_date == end_date:
        if start_day_choice in [
            settings.FIRST_HALF,
            settings.SECOND_HALF,
        ] and end_day_choice in [settings.FIRST_HALF, settings.SECOND_HALF]:
            return 0.5
        return 1.0
    else:
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        total_days = (end_date - start_date).days
        try:
            adjustment = LeaveDayChoiceAdjustment.objects.get(
                start_day_choice=start_day_choice, end_day_choice=end_day_choice
            ).adjustment_value
        except LeaveDayChoiceAdjustment.DoesNotExist:
            adjustment = 0

        total_days -= adjustment
        return float(total_days)


def get_current_financial_year():
    today = datetime.today()
    current_year = today.year
    if today.month < 4:
        fy_start = datetime(current_year - 1, 4, 1)
        fy_end = datetime(current_year, 3, 31)
    else:  # April or later
        fy_start = datetime(current_year, 4, 1)
        fy_end = datetime(current_year + 1, 3, 31)
    return fy_start, fy_end
