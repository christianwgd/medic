# -*- coding: utf-8 -*-
# Django settings for measurement project.

import os
import sys

# turn warnings into exception...
# import warnings
# warnings.filterwarnings(
#     'error', r"DateTimeField .* received a naive datetime",
#     RuntimeWarning, r'django\.db\.models\.fields')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.contrib import messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)

ADMINS = [
    ('cwiegand', 'cwiegand@wgdnet.de')
]

MANAGERS = ADMINS

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOGIN_REDIRECT_URL = '/'

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

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MOMENT_DATE_FORMAT = 'DD.MM.YYYY'
# MOMENT_DATE_FORMAT = 'MM/DD/YYYY'

DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGIN_REDIRECT_URL = 'startpage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request'
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
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
    'axes',
    'mail_templated',
    'adminsortable2',
    'medic',
    'chartjs',
    'django_filters',
    'usrprofile.apps.UsrProfileConfig',
    'measurement.apps.WerteConfig',
    'medicament.apps.MedicamentConfig',
    'prescription.apps.PrescriptionConfig',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'two_factor.plugins.phonenumber',
    'django_bootstrap5',
    'bootstrap_modal_forms',
]

ACCOUNT_ACTIVATION_DAYS = 3

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

BOOTSTRAP5 = {
    # 'theme_url': '/static/css/bootstrap.min.css',
}

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

LOG_FILE = os.path.join(BASE_DIR, 'log/medic.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root' : {'level': 'DEBUG',
              'handlers': None},
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(funcName)s %(message)s'
            },
        },

    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename' : LOG_FILE,
            'when': 'd',
            'interval' : 10,
            'backupCount': 5,  # 5 Generationen aufheben
            },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose',
            }
        },
    'loggers': {
        'django.db.backends' : {
            'level': 'CRITICAL',
            # 'level': 'DEBUG',
        },
        'medic' : {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
        }
    }

}

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

f = os.path.join(PROJECT_APP_PATH, "localsettings.py")
if os.path.exists(f):
    import sys
    import importlib
    module_name = "%s.localsettings" % PROJECT_APP
    module = importlib.import_module(module_name)
    module.__file__ = f
    sys.modules[module_name] = module
    exec(open(f, "rb").read())
