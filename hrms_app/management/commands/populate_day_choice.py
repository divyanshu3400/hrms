from django.core.management.base import BaseCommand
from django.conf import settings
from hrms_app.models import LeaveDayChoiceAdjustment

class Command(BaseCommand):
    help = 'Populate DayChoiceAdjustment table with initial data'

    def handle(self, *args, **kwargs):
        initial_data = [
            {'start_day_choice': settings.FULL_DAY, 'end_day_choice': settings.FULL_DAY, 'adjustment_value': 0},  # FULL day Scenario
            {'start_day_choice': settings.FIRST_HALF, 'end_day_choice': settings.FULL_DAY, 'adjustment_value': 0},  # FULL day for start
            {'start_day_choice': settings.FULL_DAY, 'end_day_choice': settings.SECOND_HALF, 'adjustment_value': 0},  # FULL day Scenario
            {'start_day_choice': settings.SECOND_HALF, 'end_day_choice': settings.FULL_DAY, 'adjustment_value': -0.5}, 
            {'start_day_choice': settings.FULL_DAY, 'end_day_choice': settings.FIRST_HALF, 'adjustment_value': -0.5},
            {'start_day_choice': settings.SECOND_HALF, 'end_day_choice': settings.FIRST_HALF, 'adjustment_value': -1.0},

        ]

        # Check for existing entries and avoid duplicates
        created_objects = []
        for data in initial_data:
            obj, created = LeaveDayChoiceAdjustment.objects.get_or_create(
                start_day_choice=data['start_day_choice'],
                end_day_choice=data['end_day_choice'],
                defaults={'adjustment_value': data['adjustment_value']}
            )
            if created:
                created_objects.append(obj)

        # Output the result to the console
        if created_objects:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully created {len(created_objects)} LeaveDayChoiceAdjustment entries."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "No new LeaveDayChoiceAdjustment entries were created (duplicates may exist)."
            ))
