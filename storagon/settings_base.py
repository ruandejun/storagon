"""
Django settings for storagon project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from pathlib import Path
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7yn^8pwp+yzd2l4ki6+v9kp(h)rzs$9gxu4ao^_p+9x_5+1*6o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, "frontend"),
	# os.path.join(BASE_DIR, 'storagon_templates'),
)



ALLOWED_HOSTS = [
	'*', # Allow local host connect to server.
]


# Application definition

INSTALLED_APPS = (
	'system_configure', #need to be at top for first priority
	# 'suit',
    # 'suit_redactor',	# better admin interface
	'admin_resumable',	# support resumable file upload in admin
	'corsheaders',	# CORS support
	#'memcache_admin',	# memcache viewer
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admindocs',	# doc
	'rest_framework', # Restful API
	'rest_framework.authtoken',
	'rest_framework_mongoengine', # Restful for mongoengine
	'admin_file_manager',
	'private_tracker',
	'servermain',
	'serverfile',

)

MIDDLEWARE = (
	'corsheaders.middleware.CorsMiddleware',  # CORS must put before CommonMiddleware
	"whitenoise.middleware.WhiteNoiseMiddleware",
	'system_configure.controllers.Tool.DisableCSRF',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
			os.path.join(BASE_DIR, "frontend"),
            # os.path.join(BASE_DIR, 'storagon_templates'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
			'context_processors': [
				'django.contrib.auth.context_processors.auth',
				'django.template.context_processors.request',
				'django.template.context_processors.debug',
				'django.template.context_processors.i18n',
				'django.template.context_processors.media',
				'django.template.context_processors.static',
				'django.template.context_processors.tz',
				'django.contrib.messages.context_processors.messages',
			],
        },
    },
]
ROOT_URLCONF = 'storagon.urls'

WSGI_APPLICATION = 'storagon.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'storagon',
		'USER': 'root',	  # Not used with sqlite3.
		'PASSWORD': '123',  # Not used with sqlite3.
		'HOST': 'postgredb',  # Set to empty string for localhost. Not used with sqlite3.
		'PORT': 5432,  # Set to empty string for default. Not used with sqlite3.
	}
}
MONGODB = {
	'NAME': 'storagon',
	'HOST': 'mongodb',
	'PORT': 27017,
}
REDISDB = {
	'DB': 0,
	'HOST': 'rediscache',
	'PORT': 6379,
	'PASSWORD': '',
}

IS_RUNNING_UNIT_TEST = False
if 'test' in sys.argv:
	IS_RUNNING_UNIT_TEST = True





# MEMCACHE_ADMIN = {
# 	'REFRESH_RATE': 1000,	# auto refresh webpage display server status every 1 seconds
# 	'CACHE': 'default',	# use caches definition = default
# }

# Caching
CACHES = {
	# 'default': { #Simple Local MemCache (not work well with django-cache-machine)
	#		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
	#		'LOCATION': 'storagon-cache',
	#	 'PREFIX': 'storagon_',
	#	 'TIMEOUT': None, #Keep cache forever, or for seconds
	#		'OPTIONS': {
	#			'MAX_ENTRIES': 2000 #max number of row cached
	#		}
	#	}

	'default': {	# Cluster MemCache (recommend for django-cache-machine)
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': ['memcached:11211'],
		'PREFIX': 'storagon_',
		'TIMEOUT': None,	# Keep cache forever, or for seconds
		# 'OPTIONS': {
		# 	'MAX_ENTRIES': 2000	# max number of row cached
		# }
	}
}

if IS_RUNNING_UNIT_TEST:
	print ("Change Cache BACKEND to LocMemCache")
	CACHES = {
		'default': { #Simple Local MemCache (not work well with django-cache-machine)
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': 'storagon-cache',
		'PREFIX': 'storagon_',
		'TIMEOUT': None, #Keep cache forever, or for seconds
		'OPTIONS': {
			'MAX_ENTRIES': 2000 #max number of row cached
		}
	}}

# cache-machine specific setting
CACHE_COUNT_TIMEOUT = 60	# seconds, not too long.
CACHE_EMPTY_QUERYSETS = False	# will cache query = empty

# Django Suit configuration example
SUIT_CONFIG = {
	# header
	'ADMIN_NAME': 'Storagon Admin',
	'HEADER_DATE_FORMAT': 'l, j. F Y',
	'HEADER_TIME_FORMAT': 'H:i',

	# forms
	'SHOW_REQUIRED_ASTERISK': True,	# Default True
	'CONFIRM_UNSAVED_CHANGES': True,	# Default True

	# menu
	# 'SEARCH_URL': '/admin/auth/user/',
	'MENU_ICONS': {
		'sites': 'icon-leaf',
		'auth': 'icon-lock',
	},
	# 'MENU_OPEN_FIRST_CHILD': True, # Default True
	# 'MENU_EXCLUDE': ('auth.group',),

	'MENU': ('sites',

		{'label': 'Account', 'icon': 'icon-user', 'models': ('servermain.userprofile', 'servermain.userapply', 'auth.user', 'auth.group')},

		{'label': 'File and Folder', 'icon': 'icon-hdd', 'models': ('servermain.userfile', 'servermain.folder', 'servermain.realfile',)},

		{'label': 'Transactions', 'icon': 'icon-search', 'models': (
			'servermain.bill', 'servermain.accountbalance', 'servermain.transactionlog',
			{'label': 'Session', 'permissions': ('sessions.change_session'), 'url': 'CustomAdmin:mongoListSessionView'},
			'servermain.premiumkey', 'servermain.websiteagency',
		)},

		{'label': 'Settings', 'icon': 'icon-cog', 'models': ('system_configure.systemconfig', 'servermain.serverfile', 'servermain.banlist')},

		# {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},

		{'label': 'Statistic', 'icon': 'icon-signal', 'models': [
			{'label': 'User Statistic', 'permissions': ('servermain.add_bill'), 'url': 'CustomAdmin:showUserStatistic'},
			{'label': 'Session Statistic', 'permissions': ('servermain.add_bill'), 'url': 'CustomAdmin:showSessionStatistic'},
		]},

		{'label': 'Tool', 'icon': 'icon-wrench', 'models': [
			'admin_file_manager.file',
			#{'label': 'Memcache Cluster', 'permissions': ('servermain.add_serverfile'), 'url': '/adl/memcache_admin/dashboard/'},
			{'label': 'Send Signal', 'permissions': ('servermain.add_serverfile'), 'url': 'CustomAdmin:sendServerFileSignal'},
			{'label': 'Test Upload', 'permissions': ('servermain.add_serverfile'), 'url': 'CustomAdmin:userFileUpload'},
			{'label': 'Verify Bill', 'permissions': ('servermain.add_bill'), 'url': 'CustomAdmin:verifyBillManual'},
			{'label': 'Test', 'url': 'CustomAdmin:custom_site_example'},
		]},

		{'label': 'Work Tracking', 'icon': 'icon-user', 'models': ['attendance_tracking.attendancelog',
			{'label': 'Submit Attendance', 'permissions': ('attendance_tracking.submit_attendancelog'), 'url': 'AT_submitAttendance'},
			{'label': 'Check Attendance', 'permissions': ('attendance_tracking.submit_attendancelog'), 'url': 'AT_checkAttendance'},
		]},
	),

	# misc
	# 'LIST_PER_PAGE': 30
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'


USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
  # Tell Django where to look for React's static files (css, js)
  os.path.join(BASE_DIR, "frontend/static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGIN_URL = '/adl/login/'
LOGIN_REDIRECT_URL = '/adl/'
LOGOUT_URL = '/adl/logout/'

# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
#
# TEMPLATE_CONTEXT_PROCESSORS += (
# 	'django.core.context_processors.request',	# suit admin interface
# )



#Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 25
#EMAIL_USE_SSL = True
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'AKIAJ7DSMTRQ7XL2ZN6Q'
EMAIL_HOST_PASSWORD = 'Aj73rjumstvGa6jPhhQiBcTGgQ5/sivctR8as3M2XcOT'

# FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
# 						"django.core.files.uploadhandler.TemporaryFileUploadHandler")
# FILE_UPLOAD_MAX_MEMORY_SIZE = 5*1024*1204; #20MB

if 'test' in sys.argv:
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework.authentication.TokenAuthentication',
		'rest_framework.authentication.SessionAuthentication',
		'rest_framework.authentication.BasicAuthentication',
	),

	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',
		'rest_framework.renderers.BrowsableAPIRenderer'
	),
	'DEFAULT_THROTTLE_CLASSES': (
		# 'rest_framework.throttling.ScopedRateThrottle',
		'system_configure.controllers.Tool.ScopedRateThrottleBanIP',
	),

	'DEFAULT_THROTTLE_RATES': {
		'static_page': '10/minute',
		'heavy_api': '20/minute',
		'light_api': '40/minute'
	},

	# 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
	# 'PAGINATE_BY': 20,                 # Default to 10
}
SCOPED_RATE_THROTTLE_BAN_IP_WHITE_LIST = ['117.4.240.211', '118.70.183.108'];
SCOPED_RATE_THROTTLE_BAN_IP_CMD = """/usr/bin/sudo /usr/bin/firewall-cmd --zone=public --add-rich-rule='rule family="ipv4" source address="{0}" reject'"""
SCOPED_RATE_THROTTLE_UNBAN_IP_CMD = """/usr/bin/sudo /usr/bin/firewall-cmd --zone=public --remove-rich-rule='rule family="ipv4" source address="{0}" reject'"""
SCOPED_RATE_THROTTLE_BAN_IP_TOLERANCE_RATES = '60/minute'
SCOPED_RATE_THROTTLE_BAN_IP_DURATION = 60*10 #Ban for 10 mins

#import tempfile
# ADMIN_RESUMABLE_CHUNKDIR = tempfile.gettempdir() #get temp folder on current OS

ADMIN_RESUMABLE_SUBDIR = 'realfile/'
ADMIN_RESUMABLE_SHOW_THUMB = True


# CORS_ALLOW_ALL_ORIGINS = True # If this is used then CORS_ALLOWED_ORIGINS will not have any effect
# CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True	# allow all domain
# CORS_ORIGIN_WHITELIST = (
#	 'storagon.com',
#	 'test.storagon.com',
#	 'fiddle.jshell.net', #Dung~ test
#	 'localhost',
#	 'localhost:8000',
# )
CORS_ALLOW_HEADERS = list(default_headers) + [
	'range',
	'signature_authorization',
	'Signature-Authorization'
]

# CSRF_COOKIE_DOMAIN = '.storagon.com'
# SESSION_COOKIE_DOMAIN = '.storagon.com'

# CELERY settings
BROKER_URL = 'redis://localhost:6379/0'	# using resdis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'	# using resdis

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# My setting
LOG_FILE_PATH = os.path.join(BASE_DIR, 'storagon.log')
ENABLE_ENCRYPTION = True

# servermain Settings
MONGO_SESSION_EXPIRES = 24 * 3600 # seconds
ACCOUNT_ACTIVATION_EXPIRES = 3 * 86400 # seconds = 3 days

TEMPORARY_CODE_EXPIRES = 1 * 86400 # seconds = 1 days
ACTIVATE_CODE_SUCCESS_REDIRECT = '/#/login'
SYSTEM_CONFIG_ENCODE_OVERIDE = {
	'JSON': False,
	'YAML': True,
	'BUNCH': True
}

CACHE_MONGO_SESSION_PREFIX = 'session_'

INITIAL_USER_STORAGE_SPACE = 10 * 1024 * 1024 * 1024	# 10GB

STORAGON_MAIN_EMAIL_ADDRESS = 'Storagon Secure FileHosting <mail@storagon.com>'

RECAPTCHA_SECRET = '6LeAKwQTAAAAANdIb63s8C7k35Log_jC4EBAOoKS'

OPEN_TRACKER_ANNOUNCE_URL = 'http://127.0.0.1:6969/announce'
OPEN_TRACKER_SCRAPE_URL = 'http://127.0.0.1:6969/scrape'
PRIVATE_TRACKER_ENABLE_SCRAPE = False

####
DEFAULT_PLAN_ID = 1
DEFAULT_EXCHANGE_POINT = {
	'plan1': 1000,	# number of point to exchange for plan 1
}

DEFAULT_PLAN_CONFIG = {
	'price': 1000,	# 1000 cents = 10$
	# 'premium_key_price': 900,	# 900 cents
	'expires': 30 * 86400,	# 30 days
	'storage': 100 * 1024 * 1024 * 1024,	# 100GB
	'download_bandwidth': 0,	# unlimited
	'upload_bandwidth': 0,	# unlimited
	'download_speed': 1200 * 1024,	# bytes/s = 1200 KB/s
	'download_connection': 2,	# max 8
	'download_concurrent': 0,	# max is unlimited = 0
}

DEFAULT_AFF_PREMIUM_CONFIG = {
	'storage': 0, #unlimited
	'download_bandwidth': 1000 * 1024 * 1024 * 1024,	# 1 TB
	'upload_bandwidth': 0,	# unlimited
	'download_speed': 0,	# unlimited
	'download_connection': 8,	# max 8
	'download_concurrent': 0,	# max is unlimited = 0
}

DEFAULT_PAYGATE_CONFIG = {
	'paygate_url': 'http:/paypal.com',
	'plan_available': [1],
	'paygate_name': 'paypal',
}

DEFAULT_GUEST_LIMIT_CONFIG = {	# speed : bytes/s 0=unlimited
	'download_speed': 100 * 1024,	# bytes/s = 100 KB/s
	'download_connection': 2,	# max 8
	'download_concurrent': 2,	# max is unlimited = 0
}

DEFAULT_FREE_LIMIT_PER_DAY_CONFIG = {
	'max_big_file_download': 10,
	'big_file_size': 30*1024*1024, #30 MB
}

ATTENDANCE_TRACK_ALLOW_IP_LIST = ['127.0.0.1'];#
ATTENDANCE_TRACK_TIME_BETWEEN_SUBMIT = 3*3600 # 3 hours

FILE_MANAGER_ROOT_FOLDER = 'download' #must be inside MEDIA_ROOT dir

# invidvidual settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# serverfile Settings
SERVER_MAIN_URL = 'https://storagon.com/api'
SERVER_FILE_ID = 1
# ROOT_URLCONF = 'storagon.urls_serverFile'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
