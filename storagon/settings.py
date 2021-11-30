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

REDISDB = {
	'DB': 0,
	'HOST': 'rediscache',
	'PORT': 6379,
	'PASSWORD': ''
}

# CELERY settings with password AUTH
BROKER_URL = 'redis://rediscache:6379/0'	# using resdis
CELERY_RESULT_BACKEND = 'redis://rediscache:6379/0'	# using resdis

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
