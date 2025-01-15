# management/commands/reset_leave_balances.py

from django.core.management.base import BaseCommand
from datetime import datetime
from hrms_app.models import LeaveBalanceOpenings, CustomUser

class Command(BaseCommand):
    help = 'Resets leave balances for the new year'

    def handle(self, *args, **kwargs):
        current_year = datetime.now().year
        admin_user = CustomUser.objects.get(username='admin')
        LeaveBalanceOpenings.reset_leave_balances(current_year, updated_by=admin_user)
        self.stdout.write(self.style.SUCCESS('Successfully reset leave balances for the new year'))
