# -*- coding: utf-8 -*-
#x Django settings for yaapp project.

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
TEST_MODE = 'test' in sys.argv or 'jenkins' in sys.argv
USE_MYSQL_IN_LOCAL_MODE = os.environ.get('USE_MYSQL', False) and not TEST_MODE

if PRODUCTION_MODE or DEVELOPMENT_MODE:
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = "Yasound Notification <noreply@yasound.com>"
SERVER_EMAIL = "dev@yasound.com"
if DEVELOPMENT_MODE:
    SERVER_EMAIL = "dev-dev@yasound.com"
    
EMAIL_CONFIRMATION_DAYS = 4
EMAIL_RESEND_CONFIRMATION_DAYS = 2

if PRODUCTION_MODE:
    EMAIL_HOST = 'smtp.critsend.com'
    EMAIL_PORT = 25
    EMAIL_HOST_USER = 'dev@yasound.com'
    EMAIL_HOST_PASSWORD = 'w9t4vOT9OywDRZ4Yl9uP'
    
ADMINS = (
    ('Sebastien Métrot', 'seb@yasound.com'),
    ('Jerome Blondon', 'jerome@yasound.com'),
    ('Matthieu Campion', 'matthieu@yasound.com'),
)

MANAGERS = ADMINS

MODERATORS = (
    ('Jerome Blondon', 'jerome@yasound.com'),
)

CELERY_IMPORTS = (
    "yabase.task", 
    "stats.task", 
    "account.task", 
    "emailconfirmation.task", 
    "yametrics.task",
    "yahistory.task",
    "yagraph.task",
    "yasearch.task",
)

if LOCAL_MODE:
    # Celery config:
    BROKER_URL = "django://"
    BROKER_BACKEND = "django"
    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = "sqlite:///db.dat"
    CELERY_TASK_RESULT_EXPIRES = 10
    
    YAMESSAGE_NOTIFICATION_MANAGER_ENABLED = True

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
                'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'yaapp',                      # Or path to database file if using sqlite3.
                'USER': 'root',                      # Not used with sqlite3.
                'PASSWORD': 'root',                  # Not used with sqlite3.
                'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '8889',                      # Set to empty string for default. Not used with sqlite3.
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
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'yaapp-memory-cache'
        }
    }

elif DEVELOPMENT_MODE:
    # Celery config:
    CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
    BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis"
    CELERY_REDIS_HOST = "localhost"
    CELERY_REDIS_PORT = 6379
    CELERY_REDIS_DB = 0
    CELERY_TASK_RESULT_EXPIRES = 10
    
    YAMESSAGE_NOTIFICATION_MANAGER_ENABLED = True

    # Databases config:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yaapp',                      # Or path to database file if using sqlite3.
            'OPTIONS': {'read_default_file': '~/.my.cnf',}, 
        },
        'yasound': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yasound',                      # Or path to database file if using sqlite3.
            'OPTIONS': {'read_default_file': '~/.my.cnf.yasound',}, 
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'yaapp-memory-cache'
        }
    }
    
elif PRODUCTION_MODE:
    # Celery config:
    CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
    BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis"
    CELERY_REDIS_HOST = "localhost"
    CELERY_REDIS_PORT = 6379
    CELERY_REDIS_DB = 0
    CELERY_TASK_RESULT_EXPIRES = 10
    
    YAMESSAGE_NOTIFICATION_MANAGER_ENABLED = True

    # Databases config:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yaapp',                      # Or path to database file if using sqlite3.
            'OPTIONS': {'read_default_file': '~/.my.cnf',}, 
        },
        'yasound': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'yasound',                      # Or path to database file if using sqlite3.
            'OPTIONS': {'read_default_file': '~/.my.cnf',}, 
        }
    }
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': [
                'yas-web-01:11211',
                'yas-web-02:11211',
                'yas-web-03:11211',
                'yas-web-04:11211',
                'yas-web-05:11211',
                'yas-web-06:11211',
                'yas-web-07:11211',
                'yas-web-08:11211',
                'yas-web-09:11211',
                'yas-web-10:11211',
            ]
        }
    } 
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"   

# As we use a multi database config, we need a working database router:
if not TEST_MODE:
    DATABASE_ROUTERS = ['yabase.router.YaappRouter']
else:
    # the test router enable syncdb for yasound database
    DATABASE_ROUTERS = ['yabase.router.YaappRouterForTest']
    
    # celery should be sync when running tests
    CELERY_ALWAYS_EAGER = True


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

# defaut permission for uploaded file
FILE_UPLOAD_PERMISSIONS = 0644
if PRODUCTION_MODE:
    FILE_UPLOAD_TEMP_DIR = '/data/tmp/'
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
    'django_mobile.loader.Loader',
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
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
)

if LOCAL_MODE or DEVELOPMENT_MODE:
    # ios 4 send double slashes. Nginx on prod server handle it gracefully, not on dev & local
    MIDDLEWARE_CLASSES += ('yabase.middleware.DoubleSlashMiddleware',)
    
ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "social_auth.context_processors.social_auth_by_type_backends",
    "yabase.context_processors.my_radios",
    "yabase.context_processors.facebook",
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
    'django.contrib.sitemaps',
    'django_extensions',
    'django_jenkins',
    'extjs',
    'pipeline',
    'south',
    'account',
    'wall',
    'yabase',
    'yaref',
    'stats',
    'tastypie',
    'djcelery',
    'taggit',
    'taggit_templatetags',
    'test_utils',
    'bootstrap',
    #'django-iphone-push',
    'yagraph',
    'yabackoffice',
    'social_auth',
    'sorl.thumbnail',
    'yasearch',
    'yainvitation',
    'yareport',
    'yaweb',
    'kombu.transport.django',
    'django_mobile',
    'captcha',
    'emailconfirmation',
    'yametrics',
    'yamenu',
    'yamessage',
    'yahistory',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

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
    'filters': {
        'time_throttled': {
            '()': 'timethrottledfilter.TimeThrottledFilter',
            'quantity': 5,
            'interval': 30,
            'ignore_lines': [],
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['time_throttled'],
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*10000, 
            'backupCount': 10,
            'filename': os.path.join(PROJECT_PATH, 'logs/yaapp.log'),
            'formatter': 'verbose'
        },     
        'file_yaweb':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*10000, 
            'backupCount': 10,
            'filename': os.path.join(PROJECT_PATH, 'logs/yaweb.log'),
            'formatter': 'verbose'
        },     
        'file_missing_songs':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*10000, 
            'backupCount': 10,
            'filename': os.path.join(PROJECT_PATH, 'logs/missing_songs.log'),
            'formatter': 'verbose'
        },     
        'file_delete_song':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*10000, 
            'backupCount': 10,
            'filename': os.path.join(PROJECT_PATH, 'logs/yaapp.delete_song.log'),
            'formatter': 'verbose'
        },     
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
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
        'yaapp.yabase.delete_song': {
            'handlers': ['console', 'file_delete_song'],
            'level': 'DEBUG',
            'propagate': False,
        },                
        'yaapp.account': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.yaweb': {
            'handlers': ['console', 'file_yaweb'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.yacore': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.yagraph': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.stats': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yaapp.missing_songs': {
            'handlers': ['console', 'file_missing_songs'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'account.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

if PRODUCTION_MODE:
    FACEBOOK_APP_ID              = '296167703762159'
    FACEBOOK_API_SECRET          = 'af4d20f383ed42cabfb4bf4b960bb03f'
    FACEBOOK_REALTIME_VERIFY_TOKEN = 'P6bSsjBqNRvKJWL'
    FACEBOOK_OPEN_GRAPH_ENABLED  = True
    FACEBOOK_APP_NAMESPACE       = 'yasound'
elif DEVELOPMENT_MODE:
    FACEBOOK_APP_ID              = '352524858117964'
    FACEBOOK_API_SECRET          = '687fbb99c25598cee5425ab24fec2f99'
    FACEBOOK_REALTIME_VERIFY_TOKEN = 'P6bSsjBqNRvKJWL'
    FACEBOOK_OPEN_GRAPH_ENABLED  = True
    FACEBOOK_APP_NAMESPACE       = 'yasoundev'
else:
    # myapp.com:8000
    FACEBOOK_APP_ID='256873614391089'
    FACEBOOK_API_SECRET='7e591216eeaa551cc8c4ed10a0f5c490'
    FACEBOOK_REALTIME_VERIFY_TOKEN = 'P6bSsjBqNRvKJWL'
    FACEBOOK_OPEN_GRAPH_ENABLED  = False
    FACEBOOK_APP_NAMESPACE       = 'yasoundev'

FACEBOOK_SHARE_PICTURE = '/media/yaweb/images/logo.png'

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login-error/'
PUBLIC_WEBSITE_URL = 'http://yasound.com'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
from django.template.defaultfilters import slugify
SOCIAL_AUTH_USERNAME_FIXER = lambda u: slugify(u)
SOCIAL_AUTH_EXPIRATION = 'expires'
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/app/settings/'
SOCIAL_AUTH_ENABLED_BACKENDS = ( 'facebook', 'twitter', )
AUTH_PROFILE_MODULE = 'account.UserProfile'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'account.pipeline.associate_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)

if PRODUCTION_MODE:
    DEFAULT_HTTP_PROTOCOL = 'https'
else:
    DEFAULT_HTTP_PROTOCOL = 'http'
    
# thumbnail
THUMBNAIL_KEY_DBCOLUMN = 'thumb_key' # key is a mysql reserved keyword and break replication
PICTURE_FOLDER = 'pictures'
if PRODUCTION_MODE:
    # use shared folder on prod servers
    PICTURE_FOLDER = 'pictures'
    THUMBNAIL_PREFIX = 'cache/'
    
# twitter
if PRODUCTION_MODE:
    YASOUND_TWITTER_APP_CONSUMER_KEY = 'bvpS9ZEO6REqL96Sjuklg'
    YASOUND_TWITTER_APP_CONSUMER_SECRET = 'TMdhQbWXarXoxkjwSdUbTif5CyapHLfcAdYfTnTOmc'
    
    
elif DEVELOPMENT_MODE or LOCAL_MODE:
    YASOUND_TWITTER_APP_CONSUMER_KEY = 'iLkxaRcY8QKku0UhaMvPQ'
    YASOUND_TWITTER_APP_CONSUMER_SECRET = 'rZYlrG4KXIat3nNJ3U8qXniQBSkJu8PjI1v7sCTHg'

PUSH_REDIS_HOST = 'localhost'
PUSH_REDIS_DB = 0

if LOCAL_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://yas-web-01.ig-1.net:8000/'
    YASOUND_PUSH_URL = 'http://localhost:9000/'
    ENABLE_PUSH = True
elif DEVELOPMENT_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://dev.yasound.com:8000/'
    YASOUND_PUSH_URL = 'http://dev.yasound.com:9090/'
    ENABLE_PUSH = True
elif PRODUCTION_MODE:
    YASOUND_STREAM_SERVER_URL = 'http://yas-web-01.ig-1.net:8000/'
    YASOUND_PUSH_URL = 'https://api.yasound.com:9000/'
    ENABLE_PUSH = True
    PUSH_REDIS_HOST = 'yas-sql-01'
    PUSH_REDIS_DB = 2


# constants needed by django-social-auth, see https://github.com/omab/django-social-auth#twitter
TWITTER_CONSUMER_KEY         = YASOUND_TWITTER_APP_CONSUMER_KEY
TWITTER_CONSUMER_SECRET      = YASOUND_TWITTER_APP_CONSUMER_SECRET
 
SOUTH_TESTS_MIGRATE=False   

# mongodb
from pymongo.connection import Connection
if PRODUCTION_MODE:
    MONGO_DB = Connection('mongodb://yasound:yiNOAi6P8eQC14L@yas-sql-01,yas-sql-02/yasound').yasound
elif DEVELOPMENT_MODE:
    MONGO_DB = Connection('mongodb://yasound:yiNOAi6P8eQC14L@localhost/yasound').yasound
else:
    MONGO_DB = Connection().yasound

if TEST_MODE:
    MONGO_DB = Connection().yasound_test

# album images folder
ALBUM_COVER_SHORT_URL = 'covers/albums/'
ALBUM_COVER_URL = MEDIA_URL + ALBUM_COVER_SHORT_URL

SONG_COVER_SHORT_URL = 'covers/songs/'
SONG_COVER_URL = MEDIA_URL + SONG_COVER_SHORT_URL

# celery stuff
from celery.schedules import crontab

if not PRODUCTION_MODE:
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
        "scan_friends_regularly": {
            "task": "account.task.scan_friends_task",
            "schedule": crontab(minute=0, hour='*'),
        },
        "check_users_are_alive": {
            "task": "account.task.check_live_status_task",
            "schedule": crontab(minute='*/10', hour='*'),
        },
        "build-mongodb-index": {
            "task": "yasearch.task.build_mongodb_index",
            "schedule": crontab(minute="*/30"),
        },
        "need-sync-songs": {
            "task": "yabase.task.process_need_sync_songs",
            "schedule": crontab(minute=0, hour='*'),
        },
        "resend_confirmations": {
            "task": "emailconfirmation.task.resend_confirmations_task",
            "schedule": crontab(minute=0, hour='10'),
        },
#        "delete_expired_confirmations": {
#            "task": "emailconfirmation.task.delete_expired_confirmations_task",
#            "schedule": crontab(minute=0, hour='12'),
#        },
        "calculate_top_missing_songs": {
            "task": "yametrics.task.calculate_top_missing_songs_task",
            "schedule": crontab(minute=0, hour='03'),
        },
        "daily-metrics": {
            "task": "yametrics.task.daily_metrics",
            "schedule": crontab(minute=0, hour='05'),
        },
        "raido_popularity": {
            "task": "yametrics.task.popularity_update_task",
            "schedule": crontab(minute=0, hour='*'),
        }
                           
    }
else:
    import socket   
    hostname = socket.gethostname()
    if hostname == 'yas-web-01':
        CELERYBEAT_SCHEDULE = {
            "radio-listening-stat-every-hour": {
                "task": "stats.task.radio_listening_stats_task",
                "schedule": crontab(minute=0, hour='*'),
            },
        }
    elif hostname == 'yas-web-02':
        CELERYBEAT_SCHEDULE = {
            "leaderboard_update-every-hour": {
                "task": "yabase.task.leaderboard_update_task",
                "schedule": crontab(minute=0, hour='*'),
            },
        }
    elif hostname == 'yas-web-03':
        CELERYBEAT_SCHEDULE = {
            "resend_confirmations": {
                "task": "emailconfirmation.task.resend_confirmations_task",
                "schedule": crontab(minute=0, hour='10'),
            },
#            "delete_expired_confirmations": {
#                "task": "emailconfirmation.task.delete_expired_confirmations_task",
#                "schedule": crontab(minute=0, hour='12'),
#            },
        }
    elif hostname == 'yas-web-04':
        CELERYBEAT_SCHEDULE = {
            "check_users_are_alive": {
                "task": "account.task.check_live_status_task",
                "schedule": crontab(minute='*/10', hour='*'),
            },
        }
    elif hostname == 'yas-web-05':
        CELERYBEAT_SCHEDULE = {
            "build-mongodb-index": {
                "task": "yasearch.task.build_mongodb_index",
                "schedule": crontab(minute="*/30"),
            },
            "daily-metrics": {
                "task": "yametrics.task.daily_metrics",
                "schedule": crontab(minute=0, hour='05'),
            },
        }
    elif hostname == 'yas-web-06':
        CELERYBEAT_SCHEDULE = {
            "need-sync-songs": {
                "task": "yabase.task.process_need_sync_songs",
                "schedule": crontab(minute=0, hour='*'),
            },
        }
    elif hostname == 'yas-web-07':
        CELERYBEAT_SCHEDULE = {
            "calculate_top_missing_songs": {
                "task": "yametrics.task.calculate_top_missing_songs_task",
                "schedule": crontab(minute=0, hour='03'),
            },
        }
    elif hostname == 'yas-web-08':
        CELERYBEAT_SCHEDULE = {
            "raido_popularity": {
                "task": "yametrics.task.popularity_update_task",
                "schedule": crontab(minute=0, hour='*'),
            },
        }
        
        
        
    
    
UPLOAD_SONG_FOLDER = '/tmp/'
if PRODUCTION_MODE:
    UPLOAD_SONG_FOLDER = '/space/new/medias/sources/with_id3/'

# tastypie
API_LIMIT_PER_PAGE = 0 # no pagination for now


# pipeline
if PRODUCTION_MODE :
    PIPELINE = True
else :
    PIPELINE = False

PIPELINE_ROOT=MEDIA_ROOT
PIPELINE_VERSION=True
from resources_settings import PIPELINE_JS, PIPELINE_JS
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
PIPELINE_CSS_COMPRESSOR = () # no css compression

# FFMPEG settings
FFMPEG_BIN = 'ffmpeg' # path to binary
FFMPEG_GENERATE_PREVIEW_OPTIONS = '-ar 24000 -ab 64000 -y' # convert option when generating mp3 preview
FFMPEG_CONVERT_TO_MP3_OPTIONS = '-ar 44100 -ab 192000' # convert to mp3

if LOCAL_MODE:
    FFMPEG_GENERATE_PREVIEW_OPTIONS = '-ar 24000 -ab 64000 -y' # convert option when generating mp3 preview
    FFMPEG_CONVERT_TO_MP3_OPTIONS = '-ar 44100 -ab 192000' # convert to mp3

if PRODUCTION_MODE:
    SONGS_ROOT = '/data/glusterfs-mnt/replica2all/song/'
    ALBUM_COVERS_ROOT = '/data/glusterfs-mnt/replica2all/album-cover/'
    SONG_COVERS_ROOT = '/data/glusterfs-mnt/replica2all/song-cover/'
elif DEVELOPMENT_MODE:
    SONGS_ROOT = '/home/customer/data/song/'
    ALBUM_COVERS_ROOT = '/home/customer/data/album-cover/'
    SONG_COVERS_ROOT = '/home/customer/data/song-cover/'
else:
    SONGS_ROOT = '/tmp/'
    ALBUM_COVERS_ROOT = '/tmp/'
    SONG_COVERS_ROOT = '/tmp/'
    
DEFAULT_IMAGE = MEDIA_URL +'images/default_image.png'

# temp files
if PRODUCTION_MODE:
    TEMP_DIRECTORY = '/data/tmp/'
else:
    TEMP_DIRECTORY = '/tmp/'

# iTunes buy link
ITUNES_BASE_URL="http://itunes.apple.com/search"
TRADEDOUBLER_URL="http://clk.tradedoubler.com/click?p=23753&a=2007583&url="
TRADEDOUBLER_ID="partnerId=2003"

GEOIP_DATABASE = os.path.join(PROJECT_PATH, 'GeoIP.dat')
GEOIP_LOOKUP = 'REMOTE_ADDR' 
if DJANGO_MODE == 'PRODUCTION':
    GEOIP_LOOKUP = 'HTTP_X_REAL_IP' 
    
# test
TEST_RUNNER="ignoretests.DjangoIgnoreTestSuiteRunner"
IGNORE_TESTS = (
    # Apps to ignore. example : 'django.contrib.auth',
    'django_extensions',
)
JENKINS_TEST_RUNNER="ignoretests.jenkins.JenkinsIgnoreTestSuiteRunner"


