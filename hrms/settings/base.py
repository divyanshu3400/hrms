from pathlib import Path
import os
from decouple import config
from .my_settings import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")
DEBUG = config("DEBUG")

INSTALLED_APPS = [
    "hrms_app",
    "formtools",
    "fontawesomefree",
    "bootstrap_datepicker_plus",
    "daphne",
    "rest_framework_simplejwt",
    "django_filters",
    "colorfield",
    "timezone_field",
    'django_tables2',
    'webpush',
    'django_extensions',
    "django_ckeditor_5",
    "django_celery_beat",
    "django.contrib.humanize",
    "admin_star.apps.AdminStarConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "django.contrib.sites",
    "djangobower",
    "crispy_forms",
    "schedule",
    "channels",
    "rest_framework",
    "django_weasyprint",
]

SITE_ID = 1  # or the ID of the site in your database

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hrms_app.current_request.CurrentRequestMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
]

ROOT_URLCONF = "hrms.urls"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hrms_app.context_processor.logo_settings",
            ],
        },
    },
]

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")



WSGI_APPLICATION = "hrms.wsgi.application"
ASGI_APPLICATION = "hrms.asgi.application"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "djangobower.finders.BowerFinder",
)


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = 'HRMS <hrms@kasheemilk.com>'
HRMS_DEFAULT_FROM_EMAIL = 'HRMS <hrms@kasheemilk.com>'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "hrms_app.CustomUser"
# Celery common settings
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Kolkata"


LOGO_URL = "hrms_app/img/logo.png"
LOGO_MINI_URL = "hrms_app/img/logo.png"


PANDAS_RENDERERS = [
    'rest_pandas.renderers.PandasJSONRenderer',    # JSON output
    'rest_pandas.renderers.PandasCSVRenderer',     # CSV output
    'rest_pandas.renderers.PandasExcelRenderer',   # Excel output (.xlsx)
    'rest_pandas.renderers.PandasOldExcelRenderer',   # Excel output (.xls)
    'rest_pandas.renderers.PandasPNGRenderer',     # PNG charts
    'rest_pandas.renderers.PandasSVGRenderer',     # SVG charts
    'rest_pandas.renderers.PandasHTMLRenderer',    # HTML tables
    'rest_pandas.renderers.PandasTextRenderer',    # Plain text output
]

VAPID_PUBLIC_KEY = config("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = config("VAPID_PRIVATE_KEY")
VAPID_ADMIN_EMAIL = config("VAPID_ADMIN_EMAIL")

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": VAPID_PUBLIC_KEY,
    "VAPID_PRIVATE_KEY":VAPID_PRIVATE_KEY,
    "VAPID_ADMIN_EMAIL": VAPID_ADMIN_EMAIL
}