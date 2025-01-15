import os

from django.core.wsgi import get_wsgi_application
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.production')


application = get_wsgi_application()
