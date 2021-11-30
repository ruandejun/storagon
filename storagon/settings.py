from .settings_base import *

DEBUG = True
LOG_FILE_PATH = os.path.join(BASE_DIR, 'log/junshare.log')
DOMAIN = 'storagon.com'
ENABLE_ENCRYPTION = False
# DOMAIN = 'storagon.com'
# ENABLE_ENCRYPTION = True

TIME_ZONE = 'Asia/Bangkok'
CELERY_TIMEZONE = 'Asia/Bangkok'
# LANGUAGE_CODE = 'vi'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
	'rest_framework.renderers.JSONRenderer',
	'rest_framework.renderers.BrowsableAPIRenderer'
)


# Caching
CACHES = {  # config for docker container memcached
    'default': {  # Cluster MemCache (recommend for django-cache-machine)
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': ['memcached:11211'],
        'PREFIX': 'storagon_',
        'TIMEOUT': None,  # Keep cache forever, or for seconds
    }
}

REDISDB = {
	'DB': 0,
	'HOST': 'redis',
	'PORT': 6379,
	'PASSWORD': 'hanoi123'
}
# CELERY settings with password AUTH

CELERY_RESULT_BACKEND = "redis://default:hanoi123@redis:6379/0"
CELERY_REDIS_HOST = "redis"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_PASSWORD = 'hanoi123'
CELERY_REDIS_DB = 0
# CELERY_TIMEZONE = TIME_ZONE
# CELERY_ENABLE_UTC = False
CELERY_BROKER_URL = 'redis://default:hanoi123@redis:6379/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_CONNECTION_TIMEOUT = 10
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 4,
    'interval_start': 0,
    'interval_step': 0.5,
    'interval_max': 3,
}

# BROKER_URL = 'redis://rediscache:6379/0'	# using resdis
# CELERY_RESULT_BACKEND = 'redis://rediscache:6379/0'	# using resdis

TELEGRAM_TOKEN = '2115090413:AAElpJP8QbX6ueHEDBlBZMLh2Fu8Zk5aIkQ'

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


if IS_RUNNING_UNIT_TEST:
	DATABASES['default'] = {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'storagon_test',
	}
	print("Swiching default DB to test using in-memory DB: %s"%(DATABASES['default']['NAME']))
