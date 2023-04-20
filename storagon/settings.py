from .settings_base import *

DEBUG = True
LOG_FILE_PATH = os.path.join(BASE_DIR, 'log/junshare.log')
DOMAIN = 'storagon.com'
ENABLE_ENCRYPTION = False
# DOMAIN = 'storagon.com'
# ENABLE_ENCRYPTION = True

TIME_ZONE = 'Asia/Bangkok'

# CELERY settings with password AUTH
CELERY_TIMEZONE = 'Asia/Bangkok'
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

# LANGUAGE_CODE = 'vi'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
	'rest_framework.renderers.JSONRenderer',
	'rest_framework.renderers.BrowsableAPIRenderer'
)

# TELEGRAM_TOKEN = '1047219199:AAGXYEf52FjhMVUWjr673hBsm3qc76O92QE'

TAOBAO_APPKEY = '28313470'
TAOBAO_SECRET = 'bcc56502f937ebee377ddac0036dff72'
TAOBAO_ADZONE_ID = '110006400113'

# app_key_1688 = '9996942'
# app_secret_1688 = 'dGi4rAY67n3'
# access_token_1688 = 'd5e193bd-aa82-41e6-a252-4a889fe2e0b2'
# mediaId_1688 = '1351006'
# mediaZoneId_1688 = '1356006'

APP_KEY_1688 = '9996942'
APP_SECRET_1688 = 'dGi4rAY67n3'
ACCESS_TOKEN_1688 = 'd5e193bd-aa82-41e6-a252-4a889fe2e0b2'
MEDIAID_1688 = '1351006'
MEDIAZONEID_1688 = '1356006'

# BROKER_URL = 'redis://rediscache:6379/0'	# using resdis
# CELERY_RESULT_BACKEND = 'redis://rediscache:6379/0'	# using resdis

TELEGRAM_TOKEN = '2115090413:AAElpJP8QbX6ueHEDBlBZMLh2Fu8Zk5aIkQ'
TELEGRAM_CASHBACK_TOKEN = '1235501300:AAEWPcah92B1PvsdvTCSHdT12CCg4gq-qZo'
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
