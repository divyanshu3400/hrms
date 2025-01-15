from .base import *

DEBUG  = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, "static")

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send_wishing_email': {
        'task': 'hrms_app.tasks.send_greeting_emails',
        'schedule': crontab(minute=0, hour=9),  # Every day at 9:00 AM
    },
    'populate_attendance_log': {
        'task': 'hrms_app.tasks.populate_attendance_log',
        'schedule': crontab(minute=59, hour=22),
    },
    'send_reminder_email': {
        'task': 'hrms_app.tasks.send_reminder_email',
        'schedule': crontab(minute=0, hour=10),    },
    'backup_database': {
        'task': 'hrms_app.tasks.backup_database',
        'schedule': crontab(minute=0, hour=3),    },
}
