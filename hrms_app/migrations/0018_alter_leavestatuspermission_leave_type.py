# Generated by Django 4.2.16 on 2024-12-28 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hrms_app', '0017_leavestatuspermission_leave_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavestatuspermission',
            name='leave_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hrms_app.leavetype', verbose_name='Leave Type'),
        ),
    ]
