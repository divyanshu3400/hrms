from django.test import TestCase
from django.utils import timezone
from ..models import LeaveApplication, LeaveType, CustomUser
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from hrms_app.utility.leave_utils import LeavePolicyManager

class LeavePolicyManagerTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create(username='testuser', password='password')

        # Create leave types
        self.cl_leave_type = LeaveType.objects.create(
            leave_type='Casual Leave',
            leave_type_short_code='CL',
            min_notice_days=1,
            max_days_limit=5,
            allowed_days_per_year=10
        )
        self.el_leave_type = LeaveType.objects.create(
            leave_type='Earned Leave',
            leave_type_short_code='EL',
            min_days_limit=2,
            max_days_limit=15,
            allowed_days_per_year=20
        )

        # Create a leave application
        self.leave_application = LeaveApplication.objects.create(
            leave_type=self.cl_leave_type,
            applicationNo='APP001',
            appliedBy=self.user,
            startDate=timezone.now() - timedelta(days=1),
            endDate=timezone.now(),
            usedLeave=1,
            balanceLeave=9,
            reason='Test leave',
            status='APPROVED',
            startDayChoice='1',
            endDayChoice='1'
        )

    def test_validate_overlapping_leaves(self):
        # Test overlapping leave application
        start_date = timezone.now() - timedelta(days=1)
        end_date = timezone.now() + timedelta(days=1)
        leave_manager = LeavePolicyManager(
            user=self.user,
            leave_type=self.cl_leave_type,
            start_date=start_date,
            end_date=end_date,
            start_day_choice='1',
            end_day_choice='1'
        )
        with self.assertRaises(ValidationError):
            leave_manager.validate_overlapping_leaves()

    def test_validate_consecutive_leave_restrictions(self):
        # Test consecutive leave restrictions
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        leave_manager = LeavePolicyManager(
            user=self.user,
            leave_type=self.cl_leave_type,
            start_date=start_date,
            end_date=end_date,
            start_day_choice='1',
            end_day_choice='1'
        )
        self.cl_leave_type.restricted_after_leave_types.add(self.cl_leave_type)
        with self.assertRaises(ValidationError):
            leave_manager.validate_consecutive_leave_restrictions()

    def test_apply_cl_policy(self):
        # Test Casual Leave policy
        start_date = timezone.now() + timedelta(days=2)
        end_date = start_date + timedelta(days=1)
        leave_manager = LeavePolicyManager(
            user=self.user,
            leave_type=self.cl_leave_type,
            start_date=start_date,
            end_date=end_date,
            start_day_choice='1',
            end_day_choice='1'
        )
        leave_manager.apply_cl_policy()  # Should not raise any exception

    def test_apply_el_policy(self):
        # Test Earned Leave policy
        start_date = timezone.now() + timedelta(days=2)
        end_date = start_date + timedelta(days=2)  # Ensure it meets the minimum days requirement
        leave_manager = LeavePolicyManager(
            user=self.user,
            leave_type=self.el_leave_type,
            start_date=start_date,
            end_date=end_date,
            start_day_choice='1',
            end_day_choice='1'
        )
        leave_manager.apply_el_policy()  # Should not raise any exception

    def test_apply_el_policy_exceed_allowed_days(self):
        # Test Earned Leave policy exceeding allowed days
        start_date = timezone.now() + timedelta(days=2)
        end_date = start_date + timedelta(days=21)
        leave_manager = LeavePolicyManager(
            user=self.user,
            leave_type=self.el_leave_type,
            start_date=start_date,
            end_date=end_date,
            start_day_choice='1',
            end_day_choice='1'
        )
        with self.assertRaises(ValidationError):
            leave_manager.apply_el_policy()
