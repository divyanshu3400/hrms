# Generated by Django 4.2.16 on 2024-12-27 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrms_app', '0012_attendanceloghistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='LockStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_locked', models.CharField(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked')], default='unlocked', help_text='Determines whether certain models are locked for modifications.', max_length=10, verbose_name='Lock Status')),
                ('reason', models.TextField(blank=True, help_text='The reason for locking the actions.', null=True, verbose_name='Lock Reason')),
                ('locked_at', models.DateTimeField(auto_now_add=True, verbose_name='Lock Timestamp')),
            ],
            options={
                'verbose_name': 'Lock Status',
                'verbose_name_plural': 'Lock Statuses',
            },
        ),
    ]
