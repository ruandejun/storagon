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
from telegram_bot.models import BrowserProfiles
from telegram_bot.api.TelegramBot_RestfulApi import BrowserProfilesSerializer
import random, math

@api_view(['GET', 'POST', 'PUT'])
def telegram_bot(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    t_data = json.loads(request.body)
    if 'message' in t_data:
        t_message = t_data["message"]
        t_chat = t_message["chat"]
        t_message_id = t_message["message_id"]
        #print(t_data)
        if 'text' in t_message:
            text = t_message["text"].strip()
            chat_id = t_chat["id"]
            check_cmd_telegram.delay(chat_id, t_message_id, text, chat=t_chat)
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

@api_view(['GET', 'POST', 'PUT'])
def get_browser_profiles(request):
    browser_profiles = BrowserProfiles.objects.filter(profile_owner=request.user)
    print('browser_profiles===',len(browser_profiles))
    if browser_profiles.exists():
        profile_data = BrowserProfilesSerializer(browser_profiles, many=True)
    else:
        return successResponse({'data':[]})
    ##
    return successResponse({'data':profile_data.data})

@api_view(['GET', 'POST', 'PUT'])
def get_browser_profile_by_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    id = request.POST['id']
    try:
        browser_profile = BrowserProfiles.objects.get(pk=id, profile_owner=request.user)
    except BrowserProfiles.DoesNotExist:
        return errorResponse('Profile not found', 400)
    
    profile_data = BrowserProfilesSerializer(browser_profile)
    return successResponse({'data':profile_data.data})

@api_view(['GET', 'POST', 'PUT'])
def create_browser_profile(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    #{'profile_name': '', 'profile_os': 'Window', 'profile_browser': 'Chrome', 'profile_version': '102.0.5005.63', 'profile_proxy': 'No Proxy', 'profile_proxy_details': '', 'profile_path_cookies': '', 'profile_user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36', 'profile_resolution': '1920×1080', 'profile_cpu': '8', 'profile_canvas': 'Noise', 'profile_rects': 'Noise', 'profile_font': 'Noise', 'profile_audio': 'Noise', 'profile_webgl': 'Noise', 'profile_time_zone': 'Follow IP', 'profile_webrtc': 'Follow IP', 'profile_geo': 'Follow IP', 'profile_vendor': 'Google Inc. (ATI Technologies Inc.)', 'profile_renderer': 'ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)', 'profile_start_url': 'https://iphey.com'}
    
    profile_post = json.loads(request.body)
    profile_dict =profile_post
    #proxy
    if profile_post['profile_proxy'] == 'No Proxy':
        profile_post['profile_proxy'] = 0
    elif profile_post['profile_proxy'] == 'Proxy':
        profile_post['profile_proxy'] = 1
    else:
        profile_post['profile_proxy'] = 2
    #audio
    if profile_post['profile_audio'] == 'Noise':
        list_length = 44100
        listAudioContent = {}
        i=0
        while i < list_length:
            index = int(random.uniform(0.01, 0.99)*i)
            listAudioContent[index] = random.uniform(0.01, 0.99) * 0.0000001
            i+=100
        audio_random1 = random.uniform(0.01, 0.99)
        audio_random2 = random.uniform(0.01, 0.99)
        audio_dict = {}
        audio_dict['audio_content'] = listAudioContent
        audio_dict['audio_random1'] = audio_random1
        audio_dict['audio_random2'] = audio_random2
        profile_dict['profile_audio'] = audio_dict
    #canvas
    if profile_post['profile_canvas'] == 'Noise':
        list_canvas = [-3,-2,-1,0,1,2,3]
        rsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        gsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        bsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        asalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        canvas_shift = {'r': rsalt_content,'g': gsalt_content,'b': bsalt_content,'a': asalt_content}
        profile_dict['profile_canvas'] = canvas_shift
    
    if profile_post['profile_webgl'] == 'Noise':
        #webgl
        list_floats = [math.pow(2, 0), math.pow(2, 10), math.pow(2, 11), math.pow(2, 12), math.pow(2, 13)];
        list_int = [math.pow(2, 13), math.pow(2, 14), math.pow(2, 15)]
        int_3386 = list_int[random.randint(0, len(list_int) - 1)]
        list_1234 = [math.pow(2, 1), math.pow(2, 2), math.pow(2, 3), math.pow(2, 4)]
        list_1415 = [math.pow(2, 14), math.pow(2, 15)]
        list_1213 = [math.pow(2, 12), math.pow(2, 13)]
        list_45678 = [math.pow(2, 4), math.pow(2, 5), math.pow(2, 6), math.pow(2, 7), math.pow(2, 8)]
        list_10111213 = [math.pow(2, 10), math.pow(2, 11), math.pow(2, 12), math.pow(2, 13)]
        webgl_replace = {}
        webgl_replace['36347'] = list_1213[random.randint(0, len(list_1213) - 1)]
        webgl_replace['3379'] = list_1415[random.randint(0, len(list_1415) - 1)]
        webgl_replace['34076'] = list_1415[random.randint(0, len(list_1415) - 1)]
        webgl_replace['34024'] = list_1415[random.randint(0, len(list_1415) - 1)]
        webgl_replace['35661'] = list_45678[random.randint(0, len(list_45678) - 1)]
        webgl_replace['36349'] = list_10111213[random.randint(0, len(list_10111213) - 1)]
        webgl_replace['3413'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['3412'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['3411'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['3410'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['35660'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['34047'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['34930'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['34921'] = list_1234[random.randint(0, len(list_1234) - 1)]
        webgl_replace['3386'] = [int_3386, int_3386]
        webgl_replace['33901'] = [random.uniform(0.01, 1), list_floats[random.randint(0, len(list_floats) - 1)]]
        webgl_replace['33902'] = [random.uniform(0.01, 1), list_floats[random.randint(0, len(list_floats) - 1)]]
        webgl_replace['34324'] = random.uniform(0.01, 0.99)
        webgl_replace['35376'] = random.uniform(0.01, 0.99)
        webgl_replace['35377'] = random.uniform(0.01, 0.99)
        webgl_replace['35379'] = random.uniform(0.01, 0.99)
        webgl_replace['35658'] = random.uniform(0.01, 0.99)
        webgl_replace['gl_index'] = random.uniform(0.01, 0.99)
        webgl_replace['gl_noise'] = random.uniform(0.01, 0.99)
        webgl_replace['37446'] = profile_post['profile_renderer']#list_vgas[random.randint(0, len(list_vgas) - 1)]
        list_es = ["WebGL 2.0 (OpenGL ES 3.0 Chromium)"]
        list_glsl = ["WebGL GLSL ES (OpenGL Chromium)","WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)"]
        webgl_replace['7938'] = list_es[random.randint(0, len(list_es) - 1)]
        webgl_replace['35724'] = list_glsl[random.randint(0, len(list_glsl) - 1)]
        gpu_vendor = "Google Inc. (ATI Technologies Inc.)"
        webgl_replace['37445'] = profile_post['profile_vendor']#gpu_vendor
        profile_dict['profile_webgl'] = webgl_replace

    browser_profiles = BrowserProfiles(profile_owner=request.user,**profile_post)
    browser_profiles.save()
    profile_data = BrowserProfilesSerializer(browser_profiles)

    ##
    return successResponse({'data':profile_data.data})

