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
def create_browser_profile(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    profile_dict = {}
    t_data = json.loads(request.body)
    ##audio
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
    list_canvas = [-3,-2,-1,0,1,2,3]
    rsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    gsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    bsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    asalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    canvas_shift = {'r': rsalt_content,'g': gsalt_content,'b': bsalt_content,'a': asalt_content}
    profile_dict['profile_canvas'] = canvas_shift
    #time_zone
    
    timezoneDict = {"Pacific/Niue":{"offset":-660,"msg":{"standard":"Niue Time"}},"Pacific/Pago_Pago":{"offset":-660},"Pacific/Honolulu":{"offset":-600},"Pacific/Rarotonga":{"offset":-600},"Pacific/Tahiti":{"offset":-600,"msg":{"standard":"Tahiti Time"}},"Pacific/Marquesas":{"offset":-510,"msg":{"standard":"Marquesas Time"}},"America/Anchorage":{"offset":-540},"Pacific/Gambier":{"offset":-540,"msg":{"standard":"Gambier Time"}},"America/Los_Angeles":{"offset":-480},"America/Tijuana":{"offset":-480},"America/Vancouver":{"offset":-480},"America/Whitehorse":{"offset":-480},"Pacific/Pitcairn":{"offset":-480,"msg":{"standard":"Pitcairn Time"}},"America/Dawson_Creek":{"offset":-420},"America/Denver":{"offset":-420},"America/Edmonton":{"offset":-420},"America/Hermosillo":{"offset":-420},"America/Mazatlan":{"offset":-420},"America/Phoenix":{"offset":-420},"America/Yellowknife":{"offset":-420},"America/Belize":{"offset":-360},"America/Chicago":{"offset":-360},"America/Costa_Rica":{"offset":-360},"America/El_Salvador":{"offset":-360},"America/Guatemala":{"offset":-360},"America/Managua":{"offset":-360},"America/Mexico_City":{"offset":-360},"America/Regina":{"offset":-360},"America/Tegucigalpa":{"offset":-360},"America/Winnipeg":{"offset":-360},"Pacific/Galapagos":{"offset":-360,"msg":{"standard":"Galapagos Time"}},"America/Bogota":{"offset":-300},"America/Cancun":{"offset":-300},"America/Cayman":{"offset":-300},"America/Guayaquil":{"offset":-300},"America/Havana":{"offset":-300},"America/Iqaluit":{"offset":-300},"America/Jamaica":{"offset":-300},"America/Lima":{"offset":-300},"America/Nassau":{"offset":-300},"America/New_York":{"offset":-300},"America/Panama":{"offset":-300},"America/Port-au-Prince":{"offset":-300},"America/Rio_Branco":{"offset":-300},"America/Toronto":{"offset":-300},"Pacific/Easter":{"offset":-300,"msg":{"generic":"Easter Island Time","standard":"Easter Island Standard Time","daylight":"Easter Island Summer Time"}},"America/Caracas":{"offset":-210},"America/Asuncion":{"offset":-180},"America/Barbados":{"offset":-240},"America/Boa_Vista":{"offset":-240},"America/Campo_Grande":{"offset":-180},"America/Cuiaba":{"offset":-180},"America/Curacao":{"offset":-240},"America/Grand_Turk":{"offset":-240},"America/Guyana":{"offset":-240,"msg":{"standard":"Guyana Time"}},"America/Halifax":{"offset":-240},"America/La_Paz":{"offset":-240},"America/Manaus":{"offset":-240},"America/Martinique":{"offset":-240},"America/Port_of_Spain":{"offset":-240},"America/Porto_Velho":{"offset":-240},"America/Puerto_Rico":{"offset":-240},"America/Santo_Domingo":{"offset":-240},"America/Thule":{"offset":-240},"Atlantic/Bermuda":{"offset":-240},"America/St_Johns":{"offset":-150},"America/Araguaina":{"offset":-180},"America/Argentina/Buenos_Aires":{"offset":-180,"msg":{"generic":"Argentina Time","standard":"Argentina Standard Time","daylight":"Argentina Summer Time"}},"America/Bahia":{"offset":-180},"America/Belem":{"offset":-180},"America/Cayenne":{"offset":-180},"America/Fortaleza":{"offset":-180},"America/Godthab":{"offset":-180},"America/Maceio":{"offset":-180},"America/Miquelon":{"offset":-180},"America/Montevideo":{"offset":-180},"America/Paramaribo":{"offset":-180},"America/Recife":{"offset":-180},"America/Santiago":{"offset":-180},"America/Sao_Paulo":{"offset":-120},"Antarctica/Palmer":{"offset":-180},"Antarctica/Rothera":{"offset":-180,"msg":{"standard":"Rothera Time"}},"Atlantic/Stanley":{"offset":-180},"America/Noronha":{"offset":-120,"msg":{"generic":"Fernando de Noronha Time","standard":"Fernando de Noronha Standard Time","daylight":"Fernando de Noronha Summer Time"}},"Atlantic/South_Georgia":{"offset":-120,"msg":{"standard":"South Georgia Time"}},"America/Scoresbysund":{"offset":-60},"Atlantic/Azores":{"offset":-60,"msg":{"generic":"Azores Time","standard":"Azores Standard Time","daylight":"Azores Summer Time"}},"Atlantic/Cape_Verde":{"offset":-60,"msg":{"generic":"Cape Verde Time","standard":"Cape Verde Standard Time","daylight":"Cape Verde Summer Time"}},"Africa/Abidjan":{"offset":0},"Africa/Accra":{"offset":0},"Africa/Bissau":{"offset":0},"Africa/Casablanca":{"offset":0},"Africa/El_Aaiun":{"offset":0},"Africa/Monrovia":{"offset":0},"America/Danmarkshavn":{"offset":0},"Atlantic/Canary":{"offset":0},"Atlantic/Faroe":{"offset":0},"Atlantic/Reykjavik":{"offset":0},"Etc/GMT":{"offset":0,"msg":{"standard":"Greenwich Mean Time"}},"Europe/Dublin":{"offset":0},"Europe/Lisbon":{"offset":0},"Europe/London":{"offset":0},"Africa/Algiers":{"offset":60},"Africa/Ceuta":{"offset":60},"Africa/Lagos":{"offset":60},"Africa/Ndjamena":{"offset":60},"Africa/Tunis":{"offset":60},"Africa/Windhoek":{"offset":120},"Europe/Amsterdam":{"offset":60},"Europe/Andorra":{"offset":60},"Europe/Belgrade":{"offset":60},"Europe/Berlin":{"offset":60},"Europe/Brussels":{"offset":60},"Europe/Budapest":{"offset":60},"Europe/Copenhagen":{"offset":60},"Europe/Gibraltar":{"offset":60},"Europe/Luxembourg":{"offset":60},"Europe/Madrid":{"offset":60},"Europe/Malta":{"offset":60},"Europe/Monaco":{"offset":60},"Europe/Oslo":{"offset":60},"Europe/Paris":{"offset":60},"Europe/Prague":{"offset":60},"Europe/Rome":{"offset":60},"Europe/Stockholm":{"offset":60},"Europe/Tirane":{"offset":60},"Europe/Vienna":{"offset":60},"Europe/Warsaw":{"offset":60},"Europe/Zurich":{"offset":60},"Africa/Cairo":{"offset":120},"Africa/Johannesburg":{"offset":120},"Africa/Maputo":{"offset":120},"Africa/Tripoli":{"offset":120},"Asia/Amman":{"offset":120},"Asia/Beirut":{"offset":120},"Asia/Damascus":{"offset":120},"Asia/Gaza":{"offset":120},"Asia/Jerusalem":{"offset":120},"Asia/Nicosia":{"offset":120},"Europe/Athens":{"offset":120},"Europe/Bucharest":{"offset":120},"Europe/Chisinau":{"offset":120},"Europe/Helsinki":{"offset":120},"Europe/Istanbul":{"offset":120},"Europe/Kaliningrad":{"offset":120},"Europe/Kiev":{"offset":120},"Europe/Riga":{"offset":120},"Europe/Sofia":{"offset":120},"Europe/Tallinn":{"offset":120},"Europe/Vilnius":{"offset":120},"Africa/Khartoum":{"offset":180},"Africa/Nairobi":{"offset":180},"Antarctica/Syowa":{"offset":180,"msg":{"standard":"Syowa Time"}},"Asia/Baghdad":{"offset":180},"Asia/Qatar":{"offset":180},"Asia/Riyadh":{"offset":180},"Europe/Minsk":{"offset":180},"Europe/Moscow":{"offset":180,"msg":{"generic":"Moscow Time","standard":"Moscow Standard Time","daylight":"Moscow Summer Time"}},"Asia/Tehran":{"offset":210},"Asia/Baku":{"offset":240},"Asia/Dubai":{"offset":240},"Asia/Tbilisi":{"offset":240},"Asia/Yerevan":{"offset":240},"Europe/Samara":{"offset":240,"msg":{"generic":"Samara Time","standard":"Samara Standard Time","daylight":"Samara Summer Time"}},"Indian/Mahe":{"offset":240},"Indian/Mauritius":{"offset":240,"msg":{"generic":"Mauritius Time","standard":"Mauritius Standard Time","daylight":"Mauritius Summer Time"}},"Indian/Reunion":{"offset":240,"msg":{"standard":"Réunion Time"}},"Asia/Kabul":{"offset":270},"Antarctica/Mawson":{"offset":300,"msg":{"standard":"Mawson Time"}},"Asia/Aqtau":{"offset":300,"msg":{"generic":"Aqtau Time","standard":"Aqtau Standard Time","daylight":"Aqtau Summer Time"}},"Asia/Aqtobe":{"offset":300,"msg":{"generic":"Aqtobe Time","standard":"Aqtobe Standard Time","daylight":"Aqtobe Summer Time"}},"Asia/Ashgabat":{"offset":300},"Asia/Dushanbe":{"offset":300},"Asia/Karachi":{"offset":300},"Asia/Tashkent":{"offset":300},"Asia/Yekaterinburg":{"offset":300,"msg":{"generic":"Yekaterinburg Time","standard":"Yekaterinburg Standard Time","daylight":"Yekaterinburg Summer Time"}},"Indian/Kerguelen":{"offset":300},"Indian/Maldives":{"offset":300,"msg":{"standard":"Maldives Time"}},"Asia/Calcutta":{"offset":330},"Asia/Colombo":{"offset":330},"Asia/Katmandu":{"offset":345},"Antarctica/Vostok":{"offset":360,"msg":{"standard":"Vostok Time"}},"Asia/Almaty":{"offset":360,"msg":{"generic":"Almaty Time","standard":"Almaty Standard Time","daylight":"Almaty Summer Time"}},"Asia/Bishkek":{"offset":360},"Asia/Dhaka":{"offset":360},"Asia/Omsk":{"offset":360,"msg":{"generic":"Omsk Time","standard":"Omsk Standard Time","daylight":"Omsk Summer Time"}},"Asia/Thimphu":{"offset":360},"Indian/Chagos":{"offset":360},"Asia/Rangoon":{"offset":390},"Indian/Cocos":{"offset":390,"msg":{"standard":"Cocos Islands Time"}},"Antarctica/Davis":{"offset":420,"msg":{"standard":"Davis Time"}},"Asia/Bangkok":{"offset":420},"Asia/Hovd":{"offset":420,"msg":{"generic":"Hovd Time","standard":"Hovd Standard Time","daylight":"Hovd Summer Time"}},"Asia/Jakarta":{"offset":420},"Asia/Krasnoyarsk":{"offset":420,"msg":{"generic":"Krasnoyarsk Time","standard":"Krasnoyarsk Standard Time","daylight":"Krasnoyarsk Summer Time"}},"Asia/Saigon":{"offset":420},"Indian/Christmas":{"offset":420,"msg":{"standard":"Christmas Island Time"}},"Antarctica/Casey":{"offset":480,"msg":{"standard":"Casey Time"}},"Asia/Brunei":{"offset":480,"msg":{"standard":"Brunei Darussalam Time"}},"Asia/Choibalsan":{"offset":480,"msg":{"generic":"Choibalsan Time","standard":"Choibalsan Standard Time","daylight":"Choibalsan Summer Time"}},"Asia/Hong_Kong":{"offset":480,"msg":{"generic":"Hong Kong Time","standard":"Hong Kong Standard Time","daylight":"Hong Kong Summer Time"}},"Asia/Irkutsk":{"offset":480,"msg":{"generic":"Irkutsk Time","standard":"Irkutsk Standard Time","daylight":"Irkutsk Summer Time"}},"Asia/Kuala_Lumpur":{"offset":480},"Asia/Macau":{"offset":480,"msg":{"generic":"Macau Time","standard":"Macau Standard Time","daylight":"Macau Summer Time"}},"Asia/Makassar":{"offset":480},"Asia/Manila":{"offset":480},"Asia/Shanghai":{"offset":480},"Asia/Singapore":{"offset":480,"msg":{"standard":"Singapore Standard Time"}},"Asia/Taipei":{"offset":480,"msg":{"generic":"Taipei Time","standard":"Taipei Standard Time","daylight":"Taipei Daylight Time"}},"Asia/Ulaanbaatar":{"offset":480},"Australia/Perth":{"offset":480},"Asia/Pyongyang":{"offset":510,"msg":{"standard":"Pyongyang Time"}},"Asia/Dili":{"offset":540},"Asia/Jayapura":{"offset":540},"Asia/Seoul":{"offset":540},"Asia/Tokyo":{"offset":540},"Asia/Yakutsk":{"offset":540,"msg":{"generic":"Yakutsk Time","standard":"Yakutsk Standard Time","daylight":"Yakutsk Summer Time"}},"Pacific/Palau":{"offset":540,"msg":{"standard":"Palau Time"}},"Australia/Adelaide":{"offset":630},"Australia/Darwin":{"offset":570},"Antarctica/DumontDUrville":{"offset":600,"msg":{"standard":"Dumont-d’Urville Time"}},"Asia/Magadan":{"offset":600,"msg":{"generic":"Magadan Time","standard":"Magadan Standard Time","daylight":"Magadan Summer Time"}},"Asia/Vladivostok":{"offset":600,"msg":{"generic":"Vladivostok Time","standard":"Vladivostok Standard Time","daylight":"Vladivostok Summer Time"}},"Australia/Brisbane":{"offset":600},"Australia/Hobart":{"offset":660},"Australia/Sydney":{"offset":660},"Pacific/Chuuk":{"offset":600},"Pacific/Guam":{"offset":600,"msg":{"standard":"Guam Standard Time"}},"Pacific/Port_Moresby":{"offset":600},"Pacific/Efate":{"offset":660},"Pacific/Guadalcanal":{"offset":660},"Pacific/Kosrae":{"offset":660,"msg":{"standard":"Kosrae Time"}},"Pacific/Norfolk":{"offset":660,"msg":{"standard":"Norfolk Island Time"}},"Pacific/Noumea":{"offset":660},"Pacific/Pohnpei":{"offset":660},"Asia/Kamchatka":{"offset":720,"msg":{"generic":"Petropavlovsk-Kamchatski Time","standard":"Petropavlovsk-Kamchatski Standard Time","daylight":"Petropavlovsk-Kamchatski Summer Time"}},"Pacific/Auckland":{"offset":780},"Pacific/Fiji":{"offset":780,"msg":{"generic":"Fiji Time","standard":"Fiji Standard Time","daylight":"Fiji Summer Time"}},"Pacific/Funafuti":{"offset":720},"Pacific/Kwajalein":{"offset":720},"Pacific/Majuro":{"offset":720},"Pacific/Nauru":{"offset":720,"msg":{"standard":"Nauru Time"}},"Pacific/Tarawa":{"offset":720},"Pacific/Wake":{"offset":720,"msg":{"standard":"Wake Island Time"}},"Pacific/Wallis":{"offset":720,"msg":{"standard":"Wallis & Futuna Time"}},"Pacific/Apia":{"offset":840,"msg":{"generic":"Apia Time","standard":"Apia Standard Time","daylight":"Apia Daylight Time"}},"Pacific/Enderbury":{"offset":780},"Pacific/Fakaofo":{"offset":780},"Pacific/Tongatapu":{"offset":780},"Pacific/Kiritimati":{"offset":840}}
    timezone = 'Australia/Brisbane'
    if timezone not in timezoneDict:
      timezone = 'America/New_York'
    timezoneCountry = timezoneDict[timezone]
    timezoneOffset = timezoneCountry['offset']
    country = timezone.split('/')[1].replace('_', ' ').replace('-', ' ')
    timeZoneArray = "['%s', -1 * %s, new Date().getTimezoneOffset(), '%s']" % (timezone, timezoneOffset, country+' Standard Time')
    profile_dict['profile_time_zone'] = timeZoneArray
    
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
    list_vgas = ['ANGLE (NVIDIA Quadro 2000M Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA Quadro K420 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro 2000M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro K2000M Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 3800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0)','ANGLE (AMD Radeon R9 200 Series Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 3000 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 4 Series Express Chipset Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) Graphics Media Accelerator 3150 Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) G41 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 6150SE nForce 430 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000)','ANGLE (Mobile Intel(R) 965 Express Chipset Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (AMD Radeon HD 6310 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Graphics Media Accelerator 3600 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (AMD Radeon HD 6320 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) G41 Express Chipset)','ANGLE (ATI Mobility Radeon HD 5470 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q45/Q43 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 310M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G41 Express Chipset Direct3D9 vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 45 Express Chipset Family (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 440 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4300/4500 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7310 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics)','ANGLE (Intel(R) 4 Series Internal Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon(TM) HD 6480G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 3200 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 210 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 630 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7340 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) 82945G Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 430 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 7025 / NVIDIA nForce 630a Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q35 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) HD Graphics 4600 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7520G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD 760G (Microsoft Corporation WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 220 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9500 GT Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9 vs_3_0 ps_3_0)','ANGLE (Intel(R) Graphics Media Accelerator HD Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9800 GT Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GTX 550 Ti Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (AMD M880G with ATI Mobility Radeon HD 4250 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 650 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Mobility Radeon HD 5650 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7700 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family)','ANGLE (Intel(R) 82945G Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (SiS Mirage 3 Graphics Direct3D9Ex vs_2_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 430)','ANGLE (AMD RADEON HD 6450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon 3000 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) 4 Series Internal Chipset Direct3D9 vs_3_0 ps_3_0)','ANGLE (Intel(R) Q35 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 220 Direct3D9 vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7640G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD 760G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 640 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9200 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 610 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6290 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Mobility Radeon HD 4250 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 8600 GT Direct3D9 vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 5570 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G45/G43 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4600 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro NVS 160M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 3000)','ANGLE (NVIDIA GeForce G100)','ANGLE (AMD Radeon HD 8610G + 8500M Dual Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 4 Series Express Chipset Family Direct3D9 vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 7025 / NVIDIA nForce 630a (Microsoft Corporation - WDDM) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (AMD RADEON HD 6350 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 5450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9500 GT)','ANGLE (AMD Radeon HD 6500M/5600/5700 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 965 Express Chipset Family)','ANGLE (NVIDIA GeForce 8400 GS Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Direct3D9 vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 560 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 620 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 660 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon(TM) HD 6520G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 240 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 8240 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro NVS 140M)','ANGLE (Intel(R) Q35 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)']
    webgl_replace['37446'] = list_vgas[random.randint(0, len(list_vgas) - 1)]
    list_es = ["WebGL 2.0 (OpenGL ES 3.0 Chromium)"]
    list_glsl = ["WebGL GLSL ES (OpenGL Chromium)","WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)"]
    webgl_replace['7938'] = list_es[random.randint(0, len(list_es) - 1)]
    webgl_replace['35724'] = list_glsl[random.randint(0, len(list_glsl) - 1)]
    gpu_vendor = "Google Inc. (ATI Technologies Inc.)"
    webgl_replace['37445'] = gpu_vendor
    profile_dict['profile_web_gl'] = webgl_replace
    ##
    return successResponse({"ok": "POST request processed"})

