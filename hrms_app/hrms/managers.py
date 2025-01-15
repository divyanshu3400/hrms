from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.utils.timezone import is_naive, make_aware
import pytz

class AttendanceStatusHandler:
    def __init__(self, user_shift, full_day_hours, half_day_color, present_color, absent_color):
        self.user_shift = user_shift
        self.full_day_hours = full_day_hours
        self.half_day_color = half_day_color
        self.present_color = present_color
        self.absent_color = absent_color

    def determine_attendance_status(
        self,
        login_date_time, # this is the user's logged in date and time
        logout_date_time,  # this is the user's logged out date and time
        total_duration, # this is the user's total working duration
        user_expected_logout_time,
        user_expected_logout_date_time,  # this is the user's  user expected logout date time
    ):
        total_hours = total_duration.total_seconds() / 3600
        color_hex_code = self.absent_color.color_hex
        att_status = settings.ABSENT
        att_status_short_code = "A"
        reg_status = None
        is_regularization = False
        rfrom_date = rto_date = reg_duration = None

        if total_hours == 0:
            return self._handle_absent(
                login_date_time, user_expected_logout_date_time, self.absent_color
            )

        if self._is_full_day(login_date_time, logout_date_time, total_hours, user_expected_logout_date_time):
            return self._handle_full_day(self.present_color)

        if self._is_late_coming(login_date_time, logout_date_time):
            return self._handle_late_coming(login_date_time, self.user_shift, self.half_day_color)

        if self._is_early_going(login_date_time, logout_date_time, user_expected_logout_time):
            return self._handle_early_going(
                logout_date_time, self.user_shift, user_expected_logout_date_time, self.half_day_color
            )

        if self._is_half_day(login_date_time, logout_date_time):
            return self._handle_half_day(user_expected_logout_date_time, self.half_day_color)

        return (
            att_status,
            color_hex_code,
            reg_status,
            is_regularization,
            rfrom_date,
            rto_date,
            reg_duration,
            att_status_short_code,
            None
        )

    def _is_full_day(self, login_date_time, logout_date_time, total_hours, user_expected_logout_date_time):
        return (
            login_date_time.time() <= self.user_shift.grace_start_time
            and total_hours >= self.full_day_hours
            and logout_date_time.time() >= user_expected_logout_date_time.time()
        )

    def _is_half_day(self, login_date_time, logout_date_time):
        return (
            login_date_time.time() >= self.user_shift.grace_start_time
            and logout_date_time.time() < self.user_shift.end_time
        )

    def _handle_absent(self, login_date_time, user_expected_logout_date_time, absent_color):
        return (
            settings.ABSENT,
            absent_color.color_hex,
            settings.MIS_PUNCHING,
            True,
            login_date_time,
            user_expected_logout_date_time,
            None,
            settings.PENDING,
            "A",
        )

    def _handle_full_day(self, present_color):
        return (
            settings.PRESENT,
            present_color.color_hex,
            None,
            False,
            None,
            None,
            None,
            None,
            "P",
        )


    def _handle_late_coming(self, login_date_time, user_shift, half_day_color):
        # Define the Asia/Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Ensure login_date_time is timezone-aware
        if is_naive(login_date_time):
            login_date_time = make_aware(login_date_time, timezone=kolkata_timezone)

        # Create rfrom_date as timezone-aware
        str_from_date = f"{login_date_time.date()} {user_shift.grace_start_time}"
        rfrom_date = datetime.strptime(str_from_date, "%Y-%m-%d %H:%M:%S")
        rfrom_date = make_aware(rfrom_date, timezone=kolkata_timezone)

        # Calculate rto_date and rtotal_duration
        rto_date = login_date_time
        rtotal_duration = rto_date - rfrom_date

        # Convert rtotal_duration to a time object
        reg_duration = (datetime.min + rtotal_duration).time()

        return (
            settings.HALF_DAY,
            half_day_color.color_hex,
            settings.LATE_COMING,
            True,
            rfrom_date,
            rto_date,
            reg_duration,
            settings.PENDING,
            "H",
        )

    def _handle_early_going(self, logout_date_time, user_shift, user_expected_logout_date_time, half_day_color):
        # Define the Asia/Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')
        
        # Ensure logout_date_time and user_expected_logout_date_time are timezone-aware
        if is_naive(logout_date_time):
            logout_date_time = make_aware(logout_date_time, timezone=kolkata_timezone)
        
        if is_naive(user_expected_logout_date_time):
            user_expected_logout_date_time = make_aware(user_expected_logout_date_time, timezone=kolkata_timezone)
        
        rfrom_date = logout_date_time

        # Recalculate user_expected_logout_date_time if needed
        if user_expected_logout_date_time.time() < user_shift.end_time:
            str_to_date = f"{logout_date_time.date()} {user_shift.end_time}"
            user_expected_logout_date_time = datetime.strptime(str_to_date, "%Y-%m-%d %H:%M:%S")
            # Make the recalculated datetime timezone-aware
            user_expected_logout_date_time = make_aware(user_expected_logout_date_time, timezone=kolkata_timezone)
        
        rto_date = user_expected_logout_date_time
        rtotal_duration = rto_date - rfrom_date
        reg_duration = (datetime.min + rtotal_duration).time()

        return (
            settings.HALF_DAY,
            half_day_color.color_hex,
            settings.EARLY_GOING,
            True,
            rfrom_date,
            rto_date,
            reg_duration,
            settings.PENDING,
            "H",
        )

    def _handle_half_day(self, user_expected_logout_date_time, half_day_color):
        return (
            settings.HALF_DAY,
            half_day_color.color_hex,
            None,
            False,
            None,
            user_expected_logout_date_time,
            None,
            None,
            "H",
        )

    def _is_late_coming(self, login_date_time, logout_date_time):
        return login_date_time.time() >= self.user_shift.grace_start_time and (
            logout_date_time.time() < self.user_shift.grace_end_time
            or logout_date_time.time() > self.user_shift.end_time
        )

    def _is_early_going(self, login_date_time, logout_date_time, user_expected_logout_time):
        return (
            login_date_time.time() <= self.user_shift.grace_start_time
            and logout_date_time.time() < user_expected_logout_time
        )
