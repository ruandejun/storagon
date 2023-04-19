from celery import shared_task, task
import requests, re, random,json, os
import decimal
import datetime
from django.db.models import Sum, F, Count, Q
import top.api
from django.core.serializers.json import DjangoJSONEncoder
from hashlib import sha1
import hmac
import time
from http.cookiejar import CookieJar
import telebot
from telebot import types
import urllib.parse
from django.conf import settings
from cashback.api.TaobaoApi import *
from cashback.api.Alibaba1688Api import *

def send_telegram_notify_to_group(group_id,msg,reply_markup=None,reply_id=None):
    #token='1235501300:AAEWPcah92B1PvsdvTCSHdT12CCg4gq-qZo'
    token = settings.TELEGRAM_TOKEN
    bot = telebot.TeleBot(token)
    send_msg = bot.send_message(group_id,'<b>'+msg+'</b>',reply_to_message_id=reply_id,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=False)
    return send_msg




@shared_task
def check_cmd_telegram(chat_id,t_message_id=None,text=None,callback_query=''):
    if callback_query:
        callback_split = callback_query.split('|')
        action = callback_split[0].strip()
        value = callback_split[1].strip()
        if action == 'success':
            msg = 'Bạn đã thêm telegram:%s vào tài khoản %s thành công!' % (chat_id,value)
            user_obj = User.objects.get(username=value)
            usertelegram_obj, created = UserTelegram.objects.get_or_create(telegram_id=chat_id,user=user_obj)

            send_telegram_notify_to_group(chat_id, msg=msg)
    else:
        list_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if not re.search(r'1688\.',text):
            get_taokouling = taokouling_extract(text)
            if get_taokouling:
                list_urls = get_taokouling
        if list_urls:
            for full_str in list_urls:
                msg = 'Xin lỗi sản phẩm của bạn không có chiết khấu vui lòng tìm sản phâm khác hoặc truy cập chietkhauviet.com để tìm kiếm sản phẩm!'

                referUrl_obj = get_commisstion_obj(full_str,telegram_id=chat_id)

                if referUrl_obj:
                    msg = '<a href="https://chietkhauviet.com/page/thong-tin-chiet-khau/%s">Giá sản phẩm:%s Chiết khấu:%s Phieu KM:%s</a>' % (
                        referUrl_obj.pk, float(referUrl_obj.zk_final_price) - float(referUrl_obj.coupon_amount), round(float(referUrl_obj.commission_price),2), referUrl_obj.coupon_amount)

                send_telegram_notify_to_group(chat_id, msg=msg,reply_id=t_message_id)

        else:
            cmd = text.lstrip("/")
            if cmd == "hello":
                msg = 'Chào bạn đến tới bot của công ty vân mã chuyên mua hộ và vận chuyển xuyên quốc tế!'
                send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=t_message_id)
            elif cmd.find("tk") == 0:
                username = cmd.split('tk')[-1].strip()
                user_objs = User.objects.filter(username=username)
                if user_objs.exists():
                    msg = "Bạn thêm telegram id: %s vào tài khoản: %s" % (chat_id, username)

                    reply_markup = create_markup('taikhoan', call_back_success='success|' + username,call_back_cancelled='cancelled|' + username)
                    send_telegram_notify_to_group(chat_id, msg=msg,reply_id=t_message_id, reply_markup=reply_markup)
                else:
                    msg = 'Không tìm thấy tài khoản bạn đã nhập, vui lòng nhập lại hoặc đăng ký tài khoản tại chietkhauviet.com!'
                    send_telegram_notify_to_group(chat_id, msg=msg)
            else:
                msg = "Hệ thống không thể nhận diện được câu lệnh của bạn! vui lòng liên hệ admin: "+cmd
                #send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=t_message_id)
