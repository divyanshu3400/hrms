from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from hrms_app.models import CustomUser, LeaveType, LeaveBalanceOpenings
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize leave balances for all users and all leave types for a particular year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='The year for which to initialize leave balances')

    def handle(self, *args, **options):
        year = options['year']
        users = CustomUser.objects.all()
        leave_types = LeaveType.objects.all()
        created_by = None  # Set this to the appropriate user if needed

        leave_balances = []
        for user in users:
            for leave_type in leave_types:
                leave_balance = LeaveBalanceOpenings(
                    user=user,
                    leave_type=leave_type,
                    year=year,
                    opening_balance=0,
                    created_by=created_by,
                )
                leave_balances.append(leave_balance)

        with transaction.atomic():
            LeaveBalanceOpenings.objects.bulk_create(leave_balances)
        self.stdout.write(self.style.SUCCESS(f'Successfully initialized leave balances for the year {year}'))
