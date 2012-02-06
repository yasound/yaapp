# -*- coding: utf-8 -*-
# Django settings for yaapp project.

import os, sys
import djcelery

djcelery.setup_loader()

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

# Theses settings are different with env variables
#
# We wait a DJANGO_MODE environment variable with values :
# 'production' OR 'development'
#
DJANGO_MODE = os.environ.get('DJANGO_MODE', False)
PRODUCTION_MODE = ( DJANGO_MODE == 'production' )
DEVELOPMENT_MODE = ( DJANGO_MODE == 'development' )
LOCAL_MODE = not ( PRODUCTION_MODE or DEVELOPMENT_MODE )
TEST_MODE = 'test' in sys.argv
USE_MYSQL_IN_LOCAL_MODE = os.environ.get('USE_MYSQL', False) and not TEST_MODE

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    ('Sebastien Metrot', 'seb@yasound.com'),
)

MANAGERS = ADMINS

if LOCAL_MODE:
    # Celery config:
    BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
    CELERY_IMPORTS = ("yabase.task", "stats.task", )
    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = "sqlite:///db.dat"
    CELERY_TASK_RESULT_EXPIRES = 10

    # Databases config:
    if not USE_MYSQL_IN_LOCAL_MODE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': os.path.join(PROJECT_PATH, 'db.dat'),                      # Or path to database file if using sqlite3.
                'USER': '',                      # Not used with sqlite3.
                'PASSWORD': '',                  # Not used with sqlite3.
                'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            },
             'yasound': {
                 'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                 'NAME': os.path.join(PROJECT_PATH, 'yasound_db.dat'),                      # Or path to database file if using sqlite3.
                 'USER': '',                      # Not used with sqlite3.
                 'PASSWORD': '',                  # Not used with sqlite3.
                 'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
                 'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
             }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': os.path.join(PROJECT_PATH, 'db.dat'),                      # Or path to database file if using sqlite3.
                'USER': '',                      # Not used with sqlite3.
                'PASSWORD': '',                  # Not used with sqlite3.
                'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            },
            'yasound': {
                'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'yasound',                      # Or path to database file if using sqlite3.
                'USER': 'root',                      # Not used with sqlite3.
                'PASSWORD': 'root',                  # Not used with sqlite3.
                'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '8889',                      # Set to empty string for default. Not used with sqlite3.
            }
        }
else:
    # Celery config:
    if False:
        BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
        CELERY_IMPORTS = ("yabase.task","stats.task" )
        CELERY_RESULT_BACKEND = "database"
        CELERY_RESULT_DBURI = "postgresql://yaapp:N3EDTnz945FSh6D@yasound.com/yaapp"
        CELERY_TASK_RESULT_EXPIRES = 10
    else:
        CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
        CELERY_IMPORTS = ("yabase.task", "stats.task")
        #BROKER_HOST = "127.0.0.1"
        #BROKER_PORT = 5672
        #BROKER_VHOST = "prod"
        #BROKER_USER = "yaapp"
        #BROKER_PASSWORD = "N3EDTnz945FSh6D"
        #BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
        BROKER_URL = "amqp://yaapp:N3EDTnz945FSh6D@yasound.com:5672/prod"
        CELERY_RESULT_BACKEND = "amqp"
        #CELERY_RESULT_DBURI = "amqp://yaapp:N3EDTnz945FSh6D@yasound.com:5672/prod"
        CELERY_TASK_RESULT_EXPIRES = 10

    # Databases config:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yaapp',                      # Or path to database file if using sqlite3.
            'USER': 'yaapp',                      # Not used with sqlite3.
            'PASSWORD': 'N3EDTnz945FSh6D',                  # Not used with sqlite3.
            'HOST': 'yasound.com',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5433',                      # Set to empty string for default. Not used with sqlite3.
        },
        'yasound': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yasound',                      # Or path to database file if using sqlite3.
            'USER': 'yaapp',                      # Not used with sqlite3.
            'PASSWORD': 'N3EDTnz945FSh6D',                  # Not used with sqlite3.
            'HOST': 'yasound.com',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5433',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# As we use a multi database config, we need a working database router:
if not TEST_MODE:
    DATABASE_ROUTERS = ['yabase.router.YaappRouter']
else:
    # the test router enable syncdb for yasound database
    DATABASE_ROUTERS = ['yabase.router.YaappRouterForTest']



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
#ADMIN_MEDIA_PREFIX = '/media/admin/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(MEDIA_ROOT, 'statics')
#STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
#STATIC_URL = '/static/'
STATIC_URL = '/media/statics'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'
ADMIN_MEDIA_PREFIX = "/media/statics/admin/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_a4-7n+0@fy9u15%jfue+=ce$-*kxq$=xy&l_jb(8eujz4+t#e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_extensions',
    'south',
    'account',
    'wall',
    'yabase',
    'yaref',
    'stats',
    'tastypie',
    "djkombu",
    'djcelery',
    'taggit',
    'test_utils',
)

ugettext = lambda s: s
LANGUAGES = (
    ('en', 'English'),
    ('fr', u'Français'),
)
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*10000, 
            'backupCount': 10,
            'filename': os.path.join(PROJECT_PATH, 'logs/yaapp.log'),
            'formatter': 'verbose'
        },     
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'yaapp.yaref': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.yabase': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

AUTH_PROFILE_MODULE = 'account.UserProfile'

PICTURE_FOLDER = 'pictures'

YASOUND_TWITTER_APP_CONSUMER_KEY = 'bvpS9ZEO6REqL96Sjuklg'
YASOUND_TWITTER_APP_CONSUMER_SECRET = 'TMdhQbWXarXoxkjwSdUbTif5CyapHLfcAdYfTnTOmc'

if LOCAL_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://dev.yasound.com:8001/'
elif DEVELOPMENT_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://dev.yasound.com:8001/'
elif PRODUCTION_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://dev.yasound.com:8001/'
 
SOUTH_TESTS_MIGRATE=False   

from pymongo.connection import Connection
from pymongo import DESCENDING
import gridfs
MONGO_DB = Connection().yasound



from celery.schedules import crontab
#from stats.task import radio_listening_stats_task

CELERYBEAT_SCHEDULE = {
    # Executes every hour
    "radio-listening-stat-every-hour": {
        "task": "stats.task.radio_listening_stats_task",
        "schedule": crontab(minute=0, hour='*'),
    },
    "leaderboard_update-every-hour": {
        "task": "yabase.task.leaderboard_update_task",
        "schedule": crontab(minute=0, hour='*'),
    },
}
