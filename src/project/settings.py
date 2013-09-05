import os
import sys
from os import path
import djcelery
from celery.schedules import crontab

BUILDOUT_PATH = path.split(path.abspath(path.join(path.dirname(sys.argv[0]))))[0]

PROJECT_NAME = 'skyhigh'
APP_NAME = 'Skyhigh'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Unomena Developers', 'dev@unomena.com'),
)

MANAGERS = ADMINS

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_KEY_PREFIX = 'skyhigh:'
CACHE_COUNT_TIMEOUT = 60

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s.sqlite' % PROJECT_NAME,     # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Johannesburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BUILDOUT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BUILDOUT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BUILDOUT_PATH, 'eggs/django_ckeditor-0.0.9-py2.6.egg/ckeditor/media'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z^uq$7x5jn%1novqo8b74ft583egrwfjsdpq4=p8v*$h%h93-)b88uu@7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'project.context_processors.project_settings',
    'preferences.context_processors.preferences_cp',
)

ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'skyhigh',
    'django_evolution',
    'djcelery',
    'ckeditor',
    'photologue',
    'registration',
    'honeypot',
    'unobase',
    'unobase.blog',
    'unobase.tagging',
    'unobase.commenting',
    'unobase.email_tracking',
    'unobase.support',
    'unobase.forum',
    'skyhigh.api',
    'django.contrib.admin',
)

ACCOUNT_ACTIVATION_DAYS = 7
PASSWORD_RESET_TIMEOUT_DAYS = 60
AUTH_PROFILE_MODULE = '%s.Profile' % PROJECT_NAME
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/secure/accounts/login/'
AUTH_USER_MODEL = 'auth.User'

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')
CKEDITOR_STATIC_PREFIX = '/static/ckeditor/'

EMAIL_ENABLED = False
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_PORT =  587
EMAIL_HOST_USER = 'communications@skyhighnetworks.com'
EMAIL_HOST_PASSWORD = '7eSacasPu8e4reCR'
DEFAULT_FROM_EMAIL = 'The Skyhigh Networks Team <info@skyhighnetworks.com>'

# Marketo

MARKETO_SOAP_CLIENT_LOG_FILE = '/tmp/suds.log'
MARKETO_SOAP_CLIENT_RETRIES = 3
MARKETO_SOAP_CLIENT_RETRY_SLEEP = 5
MARKETO_SOAP_CLIENT_CONNECTION_TIMEOUT = 20
MARKETO_SOAP_SERVICE_URL = 'http://app.marketo.com/soap/mktows/2_0?WSDL'
MARKETO_SOAP_SERVICE_ENDPOINT = 'https://na-sj03.marketo.com/soap/mktows/2_0'             # https://na-k.marketo.com/soap/mktows/1_6
MARKETO_SOAP_SERVICE_API_UID = 'skyhighnetworks1_4453831250F6B937F33760'                # nimbula1_189168644D6D2DC0B25194
MARKETO_SOAP_SERVICE_API_KEY = b'96355897997004385500FF66BB993389FF33443DE868'         # 627334566246333544DD66DD22DDCC12BB226ACA6296

# Salesforce Service Cloud

SERVICE_CLOUD_URL = 'https://login.salesforce.com/services/oauth2/token'
SERVICE_CLOUD_CLIENT_ID = '3MVG9Y6d_Btp4xp4qGygSMvCnjLQXtERg7S0GlhfxTGr3mUqLQRZAvaMoicLrPr9iaoV4m.eAy1wcpGXBQcgi'
SERVICE_CLOUD_CLIENT_SECRET = '1038961945592389707'
SERVICE_CLOUD_USERNAME = 'marketing@skyhighnetworks.com'
SERVICE_CLOUD_PASSWORD = 'SkyH1ghmktg'
SERVICE_CLOUD_SECURITY_TOKEN = 'VOoHDybnhB9tDQndJj31jjhB'

# Go to Webinar
GO_TO_WEBINAR_REST_SERVICE_ENDPOINT = 'https://api.citrixonline.com/G2W/rest/organizers/lol/webinars/%(webinar_key)s'

# Serialization

SERIALIZATION_MODULES = {
    'json': 'unobase.serializers.json'
}

djcelery.setup_loader()

BROKER_URL = 'amqp://skyhigh:skyhigh@127.0.0.1:5672//skyhigh'

CELERYBEAT_SCHEDULE = {
    'daily-midnight': {
        'task': 'skyhigh.automatic_emails.email_product_evaluation_5_days_in',
        'schedule': crontab(hour=0, minute=0),
        },
    'daily-midnight-5': {
        'task': 'skyhigh.automatic_emails.email_product_evaluation_25_days_in',
        'schedule': crontab(hour=0, minute=5),
        },
    'daily-midnight-10': {
        'task': 'skyhigh.automatic_emails.email_product_evaluation_expired',
        'schedule': crontab(hour=0, minute=10),
        },
    }

# Messaging emails
SKYHIGH_MAILER_EMAIL = 'mailer@skyhighnetworks.com'
SKYHIGH_INFO_EMAIL = 'info@skyhighnetworks.com'
SKYHIGH_SUPPORT_EMAIL = 'support@skyhighnetworks.com'
SKYHIGH_SALES_EMAIL = 'sales@skyhighnetworks.com'

# Honeypot
HONEYPOT_FIELD_NAME = 'skyhigh_hp'
HONEYPOT_VALUE = 'skyhigh'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Image category choices
from skyhigh.constants import DEFAULT_IMAGE_CATEGORY_CHOICES

from skyhigh import constants

# Outbound email list
OUTBOUND_EMAIL_ROLE = constants.ROLE_CHOICE_ADMIN

# Admin role
ADMIN_ROLE = constants.ROLE_CHOICE_ADMIN

try:
    from project.settings_local import *
except ImportError:
    pass
