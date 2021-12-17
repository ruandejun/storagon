#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Bot_ClientAPI.py

from django.core import serializers
from storagon.tool import *
from servermain.models import User, UserProfile
from storagon.decorator import banned_check, login_required_ajax, signature_test
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from telegram_bot.task import check_cmd_telegram


@api_view(['GET', 'POST', 'PUT'])
def telegram_bot(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    t_data = json.loads(request.body)
    print(t_data)
    if 'message' in t_data:
        t_message = t_data["message"]
        t_chat = t_message["chat"]
        t_message_id = t_message["message_id"]
        #print(t_data)
        if 'text' in t_message:
            text = t_message["text"].strip()
            chat_id = t_chat["id"]
            check_cmd_telegram.delay(chat_id, t_message_id, text)
    elif 'callback_query' in t_data:
        t_message = t_data["callback_query"]
        t_reply_to_message = t_message["message"]
        from_user = t_message['from']
        chat_id = from_user['id']
        data = t_message['data']
        t_message_id = t_reply_to_message["message_id"]
        print(from_user['id'],data)
        check_cmd_telegram.delay(chat_id,message_id=t_message_id,callback_query=data)


    return successResponse({"ok": "POST request processed"})
