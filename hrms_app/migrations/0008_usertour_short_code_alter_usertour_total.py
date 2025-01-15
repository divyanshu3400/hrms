# Generated by Django 4.2.16 on 2024-12-12 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrms_app', '0007_usertour_total_offday'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertour',
            name='short_code',
            field=models.CharField(default='T', help_text='Short code for the tour to show in the report', max_length=10, verbose_name='Short Code'),
        ),
        migrations.AlterField(
            model_name='usertour',
            name='total',
            field=models.TimeField(blank=True, help_text='The total duration of the tour from start date & time to end date & time in hours and minutes.', null=True),
        ),
    ]
