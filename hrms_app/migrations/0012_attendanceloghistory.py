# Generated by Django 4.2.16 on 2024-12-27 06:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hrms_app', '0011_personaldetails_salutation'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceLogHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_data', models.JSONField()),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('attendance_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='hrms_app.attendancelog')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Attendance Log History',
                'verbose_name_plural': 'Attendance Log Histories',
                'db_table': 'attendance_log_history',
                'ordering': ['-modified_at'],
                'permissions': [('can_view_history', 'Can view attendance log history')],
                'indexes': [models.Index(fields=['attendance_log'], name='attendance__attenda_308607_idx'), models.Index(fields=['modified_at'], name='attendance__modifie_1563d0_idx')],
            },
        ),
    ]
