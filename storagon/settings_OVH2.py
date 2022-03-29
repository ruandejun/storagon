"""
Django settings for storagon project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from settings_base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = [
	'127.0.0.1', #do not remove this
	'.storagon.com',	# Only allow domain and subdomains when launch connect to server.
]
#send debug email to ADMINS using SERVER_EMAIL
SERVER_EMAIL = 'Storagon Admin <admin@storagon.com>'
ADMINS = (('dev','vanh.storagon@gmail.com'),)


TEMPLATE_DEBUG = False

ROOT_URLCONF = 'storagon.urls'
# ROOT_URLCONF = 'storagon.urls_serverFile'

DATABASES = {

	'default': {

		'ENGINE': 'django.db.backends.mysql',

		'NAME': 'storagon',
		'USER': 'root',  # Not used with sqlite3.
		'PASSWORD': '2Lj2UkqXymn6',  # Not used with sqlite3.
		'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '',  # Set to empty string for default. Not used with sqlite3.

	},

}


MONGODB = {
	'NAME': 'storagon',
	'HOST': 'localhost',
	'PORT': 27017,
}

REDISDB = {
	'DB': 0,
	'HOST': 'localhost',
	'PORT': 6379,
	'PASSWORD': '81dKCRADcaeV',
}

# Caching
CACHES = {
	'default': {  # Cluster MemCache (recommend for django-cache-machine)
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': ['127.0.0.1:11211'],
		'PREFIX': 'storagon_',
		'TIMEOUT': None,  # Keep cache forever, or for seconds
		'OPTIONS': {
			'MAX_ENTRIES': 2000  # max number of row cached
		}
	}
}


TIME_ZONE = 'UTC'

# CELERY settings with password AUTH
BROKER_URL = 'redis://:81dKCRADcaeV@localhost:6379/0'	# using resdis
CELERY_RESULT_BACKEND = 'redis://:81dKCRADcaeV@localhost:6379/0'	# using resdis
CELERY_TIMEZONE = 'UTC'

from datetime import timedelta

TRAFFIC_LOG_PATH = '/var/log/nginx/traffic.log'
CELERYBEAT_SCHEDULE = {
	'execute-every-12-hours': {
		'task': 'serverfile.tasks.processClearTemporaryFolder',
		'schedule': timedelta(hours=12),
		'args': (-1,)
	},
	'add-every-60-seconds': {
		'task': 'serverfile.tasks.scanTrafficLogForCompletedSession',
		'schedule': timedelta(seconds=60),
		'args': (TRAFFIC_LOG_PATH, True)
	},
}

# My setting
LOG_FILE_PATH = '/var/www/storagon/log/storagon.log'
DOMAIN = 'storagon.com'
ENABLE_ENCRYPTION = True

STORAGON_MAIN_EMAIL_ADDRESS = 'Storagon Secure FileHosting <mail@storagon.com>'

ATTENDANCE_TRACK_ALLOW_IP_LIST = ['127.0.0.1', '117.4.240.211', '118.70.183.108', '113.190.242.112'];#
ATTENDANCE_TRACK_TIME_BETWEEN_SUBMIT = 2*3600 # 2 hours

# invidvidual settings
MEDIA_ROOT = '/media'; #remember to: sudo chown -R TVA /media

#server main settings
# ALLOWED_HOSTS += ['167.114.158.184']
# serverfile settings ,
SERVER_MAIN_URL = 'http://127.0.0.1' #on the same node as server main
SERVER_FILE_ID = 1


if IS_RUNNING_UNIT_TEST:
	DATABASES['default'] = {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'storagon_test',
	}
	print("Swiching default DB to test using in-memory DB: %s"%(DATABASES['default']['NAME']))