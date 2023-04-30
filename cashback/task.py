from celery import shared_task
from storagon import settings
from cashback.models import payment_models, product_models, shop_models
import datetime
import json, re, pytz, decimal
# from django.conf import settings
import top.api, requests, aop
from http.cookiejar import CookieJar
from django.contrib.auth.models import User
from django.db.models import Sum, F, Count, Q
from telegram_bot.task import send_telegram_notify_to_group
from django.utils import timezone

appkey = settings.TAOBAO_APPKEY
secret = settings.TAOBAO_SECRET
adzone_id = settings.TAOBAO_ADZONE_ID


APP_KEY_1688 = settings.APP_KEY_1688
APP_SECRET_1688 = settings.APP_SECRET_1688
ACCESS_TOKEN_1688 = settings.ACCESS_TOKEN_1688
MEDIAID_1688 = settings.MEDIAID_1688
MEDIAZONEID_1688 = settings.MEDIAZONEID_1688

