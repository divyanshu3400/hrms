from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import date
from hrms_app.models import LeaveType

class Command(BaseCommand):
    help = 'Populate the LeaveType model based on settings.LEAVE_TYPE_CHOICES'

    def handle(self, *args, **options):
        current_date = date.today()
        current_year_start = date(current_date.year, 1, 1)
        current_year_end = date(current_date.year, 12, 31)
        
        # Assuming financial year starts on April 1st and ends on March 31st
        if current_date.month >= 4:
            fy_start = date(current_date.year, 4, 1)
            fy_end = date(current_date.year + 1, 3, 31)
        else:
            fy_start = date(current_date.year - 1, 4, 1)
            fy_end = date(current_date.year, 3, 31)

        for leave_type, leave_type_display in settings.LEAVE_TYPE_CHOICES:
            if leave_type == settings.EL:
                leave_fy_start = fy_start
                leave_fy_end = fy_end
            else:
                leave_fy_start = current_year_start
                leave_fy_end = current_year_end

            LeaveType.objects.get_or_create(
                leave_type=leave_type,
                defaults={
                    'leave_type_short_code': leave_type[:3].upper(),
                    'min_notice_days': 0,
                    'max_days_limit': 0,
                    'min_days_limit': 0,
                    'allowed_days_per_year': 0,
                    'leave_fy_start': leave_fy_start,
                    'leave_fy_end': leave_fy_end,
                    'color_hex': '#5d298a',
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated LeaveType model'))
