# Django settings for measurement project.

import sys
import os
from ast import AugLoad

from pathlib import Path

from django.contrib import messages

# turn warnings into exception...
# import warnings
# warnings.filterwarnings(
#     'error', r"DateTimeField .* received a naive datetime",
#     RuntimeWarning, r'django\.db\.models\.fields')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = Path(Path(Path(__file__).resolve()).parent).parent
PROJECT_APP_PATH = Path(Path(__file__).resolve()).parent
PROJECT_APP = Path(PROJECT_APP_PATH).name

# Settings for tests, override in production with localsettings!
DEBUG = os.getenv('DEBUG', 'True')

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    'django-insecure-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'  # noqa: S105
)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*')

DATABASES = {
    'default': {
        "ENGINE": os.getenv('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DB_NAME', 'medic'),
        "USER": os.getenv('DB_USER', None),
        "PASSWORD": os.getenv('DB_PASSWORD', None),
        "HOST": os.getenv('DB_HOST', 'localhost'),
        "PORT": os.getenv('DB_PORT', '5432'),
    },
}

ADMINS = [
    ('cwiegand', 'cwiegand@wgdnet.de'),
]

MANAGERS = ADMINS

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'
# LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MOMENT_DATE_FORMAT = 'DD.MM.YYYY'
# MOMENT_DATE_FORMAT = 'MM/DD/YYYY'

DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR) / 'static'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'startpage'
LOGOUT_REDIRECT_URL = 'account_login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'medic.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'medic.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'medic',
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'mail_templated',
    'adminsortable2',
    'django_select2',
    'chartjs',
    'django_filters',
    'usrprofile.apps.UsrProfileConfig',
    'measurement.apps.WerteConfig',
    'medicament.apps.MedicamentConfig',
    'prescription.apps.PrescriptionConfig',
    'order.apps.OrderConfig',
    'django_bootstrap5',
    'bootstrap_modal_forms',
]

ACCOUNT_ACTIVATION_DAYS = 3

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

BOOTSTRAP5 = {
    # 'theme_url': '/static/css/bootstrap.min.css',
}

# All-auth settings
ACCOUNT_LOGIN_METHODS = {"username"}
MFA_PASSKEY_LOGIN_ENABLED = True

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# axes
AXES_COOLOFF_TIME = 1 # lock for 1 hour
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True
AXES_CLIENT_IP_CALLABLE = "medic.utils.get_client_ip"
