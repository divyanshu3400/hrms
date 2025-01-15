from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.production')

celery_app = Celery('hrms')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
