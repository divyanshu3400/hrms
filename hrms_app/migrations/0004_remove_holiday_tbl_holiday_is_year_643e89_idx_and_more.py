# Generated by Django 4.2.16 on 2024-12-04 06:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hrms_app', '0003_leavetype_half_day_short_code'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='holiday',
            name='tbl_holiday_is_year_643e89_idx',
        ),
        migrations.RemoveField(
            model_name='holiday',
            name='is_yearly_recurring',
        ),
        migrations.RemoveField(
            model_name='holiday',
            name='recurrence_pattern',
        ),
        migrations.RemoveField(
            model_name='holiday',
            name='recurrence_rule',
        ),
    ]
