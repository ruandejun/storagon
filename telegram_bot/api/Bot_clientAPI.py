#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Bot_ClientAPI.py

import profile
from time import time
from django.core import serializers
from storagon.tool import *
from servermain.models import User, UserProfile
from storagon.decorator import banned_check, login_required_ajax, signature_test
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view
from telegram_bot.task import check_cmd_telegram
from telegram_bot.models import *
from telegram_bot.api.TelegramBot_RestfulApi import *
import random, math
from random import choice
from django.utils import timezone
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
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_browser_profiles(request):
    browser_profiles = BrowserProfiles.objects.filter(profile_owner=request.user).order_by('-id')

    profile_data = BrowserProfilesSerializer(browser_profiles, many=True)

    ##
    return successResponse({'data':profile_data.data})



@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_emails(request):
    list_objects = AccountsEmails.objects.filter(owner=request.user).order_by('-id')

    accounts_data = AccountsEmailsSerializer(list_objects, many=True)

    ##
    return successResponse({'data':accounts_data.data})
  
 
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_created(request):
    list_objects = AccountsCreated.objects.filter(owner=request.user).order_by('-id')

    accounts_data = AccountsCreatedSerializer(list_objects, many=True)

    ##
    return successResponse({'data':accounts_data.data})
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_accounts_created(request):
  
    accounts_playload = json.loads(request.body)
    profile_id = accounts_playload['profile_id']
    email = accounts_playload['email']  
    password = accounts_playload['password']
    type = accounts_playload['type']
    profile_objects = BrowserProfiles.objects.filter(pk=profile_id)
    if not profile_objects.exists():
        return errorResponse('Profile not found', 400) 
    account_type, created = AccountsType.objects.get_or_create(value=type.lower())
    accounts_data = AccountsCreated(email=email, password=password, browser_profiles=profile_objects[0], type=account_type, owner=request.user)
    accounts_data.save()
    accounts_data.refresh_from_db()
    data_serializer = AccountsCreatedSerializer(accounts_data, many=False)
    
    return successResponse({'data':data_serializer.data}) 
 
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_data(request):
    
    if request.GET['action'] == 'refesh':
        list_objects = AccountsData.objects.filter(owner=None)
        if request.GET['state']:
            list_objects = list_objects.objects.filter(state=request.GET['state'])
        elif request.GET['city']:
            list_objects = list_objects.objects.filter(city=request.GET['city'])
        pks = list_objects.objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = list_objects.objects.get(pk=random_pk)
        accounts_data = AccountsDataSerializer(random_obj)
    else:
        list_objects = AccountsData.objects.filter(owner=request.user)
        accounts_data = AccountsDataSerializer(list_objects, many=True)
    return successResponse({'data':accounts_data.data})
  


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_inject_info(request):
    inject_data = {}
    inject_data['resolution'] = '''
      (function fakeScreenResolution(){
        "use strict";
        /**
        * Define property on an object.
        */
        var defineProp = function(obj, prop, val) {
          Object.defineProperty(obj, prop, {
            enumerable: true,
            configurable: true,
            value: val
          });
        };
        /**
        * Return screen attributes based on the most commons ones.
        */
        var getScreenAttrs = function() {
          return {
            width: {{screen_width}},
            height: {{screen_height}},
            colorDepth: 24,
            pixelDepth: 24
          };
        };
        /**
        * Spoof screen resolution.
        */
        var spoofScreenResolution = function() {
          var screen = getScreenAttrs();
          defineProp(window.screen, "width", screen.width);
          defineProp(window.screen, "height", screen.height);
          defineProp(window.screen, "availWidth", screen.width);
          defineProp(window.screen, "availHeight", screen.height);
          defineProp(window.screen, "top", 0);
          defineProp(window.screen, "left", 0);
          defineProp(window.screen, "availTop", 0);
          defineProp(window.screen, "availLeft", 0);
          defineProp(window.screen, "colorDepth", screen.colorDepth);
          defineProp(window.screen, "pixelDepth", screen.pixelDepth);
          /**
          * @todo Implement window.innerHeight, window.innerWidth, etc...
          * @see https://developer.mozilla.org/en-US/docs/Web/API/Screen
          */
        };
      
        /**
        * Initialize script
        */
        var init = function() {
          // LET SPOOF THAT FUCKIN' RES/COLOR DEPTH
          spoofScreenResolution();
        };
        init();
      })();


    '''
    inject_data['vendor'] = '''
      (function fakeVendor() {
      Object.defineProperty(navigator, 'vendor', {   value: '{{vendor}}',   configurable: true });
    })();     
    '''
    inject_data['MaxTouchPoints'] = '''
    (function fakeMaxTouchPoints() {
      Object.defineProperty(navigator, 'maxTouchPoints', {   value: {{MaxTouchPoints}},   configurable: true });
    })();
    '''
    inject_data['UserAgent'] = '''
      (function fakeUserAgent() {
        Object.defineProperty(navigator, 'userAgent', {   value: '{{UserAgent}}',   configurable: true });
      })();
      '''
    inject_data['audio'] = '''
    (function fakeAudioFinger() {
      const context = {
        "BUFFER": null,
        "getChannelData": function (e) {
          const getChannelData = e.prototype.getChannelData;
          Object.defineProperty(e.prototype, "getChannelData", {
            "value": function () {
              const results_1 = getChannelData.apply(this, arguments);
              if (context.BUFFER !== results_1) {
                context.BUFFER = results_1;
   
                let obj2 = {{audio_content}};
                for (const key of Object.keys(obj2)) {
                    results_1[key] = obj2[key]
                }
              }
              return results_1;
            }
          });
        },
        "createAnalyser": function (e) {
          const createAnalyser = e.prototype.__proto__.createAnalyser;
          Object.defineProperty(e.prototype.__proto__, "createAnalyser", {
            "value": function () {
              const results_2 = createAnalyser.apply(this, arguments);
              const getFloatFrequencyData = results_2.__proto__.getFloatFrequencyData;
              Object.defineProperty(results_2.__proto__, "getFloatFrequencyData", {
                "value": function () {
                  const results_3 = getFloatFrequencyData.apply(this, arguments);
                  for (var i = 0; i < arguments[0].length; i += 100) {
                    let index = Math.floor({{audio_random1}} * i);
                    var new_value = arguments[0][index] + {{audio_random2}} * 0.1;
                    arguments[0][index] = new_value
                  }
                  return results_3;
                }
              });
              //
              return results_2;
            }
          });
        }
      };
      //
      context.getChannelData(AudioBuffer);
      context.createAnalyser(AudioContext);
      context.getChannelData(OfflineAudioContext);
      context.createAnalyser(OfflineAudioContext);
      console.log('==fakeAudioFinger==',AudioBuffer);
    })();
    const iframes = [...window.top.document.querySelectorAll("iframe[sandbox]")];
    for (var i = 0; i < iframes.length; i++) {
      if (iframes[i].contentWindow) {
        if (iframes[i].contentWindow.AudioBuffer) {
          if (iframes[i].contentWindow.AudioBuffer.prototype) {
            if (iframes[i].contentWindow.AudioBuffer.prototype.getChannelData) {
              iframes[i].contentWindow.AudioBuffer.prototype.getChannelData = AudioBuffer.prototype.getChannelData;
            }
          }
        }

        if (iframes[i].contentWindow.AudioContext) {
          if (iframes[i].contentWindow.AudioContext.prototype) {
            if (iframes[i].contentWindow.AudioContext.prototype.__proto__) {
              if (iframes[i].contentWindow.AudioContext.prototype.__proto__.createAnalyser) {
                iframes[i].contentWindow.AudioContext.prototype.__proto__.createAnalyser = AudioContext.prototype.__proto__.createAnalyser;
              }
            }
          }
        }

        if (iframes[i].contentWindow.OfflineAudioContext) {
          if (iframes[i].contentWindow.OfflineAudioContext.prototype) {
            if (iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__) {
              if (iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__.createAnalyser) {
                iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__.createAnalyser = OfflineAudioContext.prototype.__proto__.createAnalyser;
              }
            }
          }
        }

        if (iframes[i].contentWindow.OfflineAudioContext) {
          if (iframes[i].contentWindow.OfflineAudioContext.prototype) {
            if (iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__) {
              if (iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__.getChannelData) {
                iframes[i].contentWindow.OfflineAudioContext.prototype.__proto__.getChannelData = OfflineAudioContext.prototype.__proto__.getChannelData;
              }
            }
          }
        }
      }
    }
    '''
    inject_data['canvas'] = '''
    (function fakeCanvasFingerPrint() {
        const toBlob = HTMLCanvasElement.prototype.toBlob;
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        const getImageData = CanvasRenderingContext2D.prototype.getImageData;
        //
        var noisify = function (canvas, context) {
            //console.log('==let noisify==',context);
            if (context) {
              const shift = {{canvas_shift}};
              //
              let ctxIdx = ctxArr.indexOf(context);
              let info = ctxInf[ctxIdx];
              const width = canvas.width;
              const height = canvas.height;
              if (info.useArc || info.useFillText && width && height) {
                const imageData = getImageData.apply(context, [0, 0, width, height]);
                for (let i = 0; i < height; i++) {
                  for (let j = 0; j < width; j++) {
                    const n = ((i * (width * 4)) + (j * 4));
                    imageData.data[n + 0] = imageData.data[n + 0] + shift.r;
                    imageData.data[n + 1] = imageData.data[n + 1] + shift.g;
                    imageData.data[n + 2] = imageData.data[n + 2] + shift.b;
                    imageData.data[n + 3] = imageData.data[n + 3] + shift.a;
                  }
                }
                //
                //window.top.postMessage("canvas-fingerprint-defender-alert", '*');
                context.putImageData(imageData, 0, 0); 
              }
            }
        };
        let ctxArr = [];
        let ctxInf = [];    
        let rawGetContext = HTMLCanvasElement.prototype.getContext
     
        Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
            "value": function () {
                let result = rawGetContext.apply(this, arguments);
                if (arguments[0] === '2d') {
                    ctxArr.push(result)
                    ctxInf.push({})
                }
                return result;
            }
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.constructor, "length", {
            "value": 1
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.constructor, "toString", {
            "value": () => "function getContext() { [native code] }"
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.constructor, "name", {
            "value": "getContext"
        });
        let rawArc = CanvasRenderingContext2D.prototype.arc
        Object.defineProperty(CanvasRenderingContext2D.prototype, "arc", {
            "value": function () {
                let ctxIdx = ctxArr.indexOf(this);
                ctxInf[ctxIdx].useArc = true;
                return rawArc.apply(this, arguments);
            }
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "length", {
            "value": 5
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "toString", {
            "value": () => "function arc() { [native code] }"
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "name", {
            "value": "arc"
        });    
        const rawFillText = CanvasRenderingContext2D.prototype.fillText;
        Object.defineProperty(CanvasRenderingContext2D.prototype, "fillText", {
            "value": function () {
                let ctxIdx = ctxArr.indexOf(this);
                ctxInf[ctxIdx].useFillText = true;
                return rawFillText.apply(this, arguments);
            }
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "length", {
            "value": 4
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "toString", {
            "value": () => "function fillText() { [native code] }"
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "name", {
            "value": "fillText"
        }); 
        //
        Object.defineProperty(HTMLCanvasElement.prototype, "toBlob", {
            "value": function () {
              noisify(this, this.getContext("2d"));
              return toBlob.apply(this, arguments);
            }
        });
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "length", {
            "value": 1
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "toString", {
            "value": () => "function toBlob() { [native code] }"
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "name", {
            "value": "toBlob"
        });  
        //
        Object.defineProperty(HTMLCanvasElement.prototype, "toDataURL", {
            "value": function () {
              noisify(this, this.getContext("2d"));
              return toDataURL.apply(this, arguments);
            }
        });
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "length", {
            "value": 0
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "toString", {
            "value": () => "function toDataURL() { [native code] }"
        });
     
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "name", {
            "value": "toDataURL"
        });
        //
        Object.defineProperty(CanvasRenderingContext2D.prototype, "getImageData", {
            "value": function () {
              noisify(this.canvas, this);
              return getImageData.apply(this, arguments);
            }
        });
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "length", {
            "value": 4
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "toString", {
            "value": () => "function getImageData() { [native code] }"
        });
     
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "name", {
            "value": "getImageData"
        });
    })();    
    '''
    inject_data['time_zone'] = '''
    ( function fakeTimeZone() {
        Date.prefs = {{timeZoneArray}};
        console.log('==Date.prefs==',Date.prefs);
        const ODateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(locales, options = {}) {
          Object.assign(options, {
            timeZone: Date.prefs[0]
          });
          return ODateTimeFormat(locales, options);
        };
        Intl.DateTimeFormat.prototype = Object.create(ODateTimeFormat.prototype);
        Intl.DateTimeFormat.supportedLocalesOf = ODateTimeFormat.supportedLocalesOf;
        const clean = str => {
          const toGMT = offset => {
            const z = n => (n < 10 ? '0' : '') + n;
            const sign = offset <= 0 ? '+' : '-';
            offset = Math.abs(offset);
            return sign + z(offset / 60 | 0) + z(offset % 60);
          };
          str = str.replace(/([T\\(])[\\+-]\\d+/g, '$1' + toGMT(Date.prefs[1]));
          if (str.indexOf(' (') !== -1) {
            str = str.split(' (')[0] + ' (' + Date.prefs[3] + ')';
          }
          return str;
        }

        const ODate = Date;
        const {
          getTime, getDate, getDay, getFullYear, getHours, getMilliseconds, getMinutes, getMonth, getSeconds, getYear,
          toDateString, toLocaleString, toString, toTimeString, toLocaleTimeString, toLocaleDateString,
          setYear, setHours, setTime, setFullYear, setMilliseconds, setMinutes, setMonth, setSeconds, setDate,
          setUTCDate, setUTCFullYear, setUTCHours, setUTCMilliseconds, setUTCMinutes, setUTCMonth, setUTCSeconds
        } = ODate.prototype;
        
        class ShiftedDate extends ODate {
          constructor(...args) {
            super(...args);
            this.nd = new ODate(
              getTime.apply(this) + (Date.prefs[2] - Date.prefs[1]) * 60 * 1000
            );
          }
          // get
          toLocaleString(...args) {
            return toLocaleString.apply(this.nd, args);
          }
          toLocaleTimeString(...args) {
            return toLocaleTimeString.apply(this.nd, args);
          }
          toLocaleDateString(...args) {
            return toLocaleDateString.apply(this.nd, args);
          }
          toDateString(...args) {
            return toDateString.apply(this.nd, args);
          }
          getDate(...args) {
            return getDate.apply(this.nd, args);
          }
          getDay(...args) {
            return getDay.apply(this.nd, args);
          }
          getFullYear(...args) {
            return getFullYear.apply(this.nd, args);
          }
          getHours(...args) {
            return getHours.apply(this.nd, args);
          }
          getMilliseconds(...args) {
            return getMilliseconds.apply(this.nd, args);
          }
          getMinutes(...args) {
            return getMinutes.apply(this.nd, args);
          }
          getMonth(...args) {
            return getMonth.apply(this.nd, args);
          }
          getSeconds(...args) {
            return getSeconds.apply(this.nd, args);
          }
          getYear(...args) {
            return getYear.apply(this.nd, args);
          }
          // set
          setHours(...args) {
            const a = getTime.call(this.nd);
            const b = setHours.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setFullYear(...args) {
            const a = getTime.call(this.nd);
            const b = setFullYear.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setMilliseconds(...args) {
            const a = getTime.call(this.nd);
            const b = setMilliseconds.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setMinutes(...args) {
            const a = getTime.call(this.nd);
            const b = setMinutes.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setMonth(...args) {
            const a = getTime.call(this.nd);
            const b = setMonth.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setSeconds(...args) {
            const a = getTime.call(this.nd);
            const b = setSeconds.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setDate(...args) {
            const a = getTime.call(this.nd);
            const b = setDate.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setYear(...args) {
            const a = getTime.call(this.nd);
            const b = setYear.apply(this.nd, args);
            setTime.call(this, getTime.call(this) + b - a);
            return b;
          }
          setTime(...args) {
            const a = getTime.call(this);
            const b = setTime.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCDate(...args) {
            const a = getTime.call(this);
            const b = setUTCDate.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCFullYear(...args) {
            const a = getTime.call(this);
            const b = setUTCFullYear.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCHours(...args) {
            const a = getTime.call(this);
            const b = setUTCHours.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCMilliseconds(...args) {
            const a = getTime.call(this);
            const b = setUTCMilliseconds.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCMinutes(...args) {
            const a = getTime.call(this);
            const b = setUTCMinutes.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCMonth(...args) {
            const a = getTime.call(this);
            const b = setUTCMonth.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          setUTCSeconds(...args) {
            const a = getTime.call(this);
            const b = setUTCSeconds.apply(this, args);
            setTime.call(this.nd, getTime.call(this.nd) + b - a);
            return b;
          }
          // toString
          toString(...args) {
            return clean(toString.apply(this.nd, args));
          }
          toTimeString(...args) {
            return clean(toTimeString.apply(this.nd, args));
          }
          // offset
          getTimezoneOffset() {
            return Date.prefs[1];
          }
        }
        Date = ShiftedDate;
        console.log('==fakeTimeZone==');       
    })();    
    '''
    inject_data['webgl'] = '''
     (function fakeWebglFingerPrint() {
      var config = {
        "random": {
          "value": function () {
            return Math.random();
          },
          "item": function (e) {
            var rand = e.length * config.random.value();
            return e[Math.floor(rand)];
          },
          "number": function (power) {
            var tmp = [];
            for (var i = 0; i < power.length; i++) {
              tmp.push(Math.pow(2, power[i]));
            }
            /*  */
            return config.random.item(tmp);
          },
          "int": function (power) {
            var tmp = [];
            for (var i = 0; i < power.length; i++) {
              var n = Math.pow(2, power[i]);
              tmp.push(new Int32Array([n, n]));
            }
            /*  */
            return config.random.item(tmp);
          },
          "float": function (power) {
            var tmp = [];
            for (var i = 0; i < power.length; i++) {
              var n = Math.pow(2, power[i]);
              tmp.push(new Float32Array([1, n]));
            }
            /*  */
            return config.random.item(tmp);
          }
        },
        "spoof": {
          "webgl": {
            "buffer": function (target) {
              var proto = target.prototype ? target.prototype : target.__proto__;
              const bufferData = proto.bufferData;
              Object.defineProperty(proto, "bufferData", {
                "value": function () {
                  var index = Math.floor({{gl_index}} * arguments[1].length);
                  var noise = arguments[1][index] !== undefined ? 0.1 * {{gl_noise}} * arguments[1][index] : 0;
                  //
                  arguments[1][index] = arguments[1][index] + noise;
                  //
                  return bufferData.apply(this, arguments);
                }
              });
            },
            "parameter": function (target) {
              var proto = target.prototype ? target.prototype : target.__proto__;
              const getParameter = proto.getParameter;
              Object.defineProperty(proto, "getParameter", {
                "value": function () {
                  //window.top.postMessage("webgl-fingerprint-defender-alert", '*');
                  //
                  if (arguments[0] === 3415) return 0;
                  else if (arguments[0] === 3414) return 24;
                  else if (arguments[0] === 3410) return 8;
                  else if (arguments[0] === 3411) return 8;
                  else if (arguments[0] === 3412) return 8;
                  else if (arguments[0] === 3413) return 8;
                  else if (arguments[0] === 3415) return 8;
                  else if (arguments[0] === 35375) return 24;
                  else if (arguments[0] === 35374) return 24;
                  else if (arguments[0] === 35380) return 4;
                  else if (arguments[0] === 34045) return 12;
                  else if (arguments[0] === 36348) return 32;
                  else if (arguments[0] === 35371) return 12;
                  else if (arguments[0] === 37154) return 64;
                  else if (arguments[0] === 35659) return 128;
                  else if (arguments[0] === 35978) return 64;
                  else if (arguments[0] === 35979) return 4;
                  else if (arguments[0] === 35968) return 64;
                  else if (arguments[0] === 34852) return 8;
                  else if (arguments[0] === 36063) return 8;
                  else if (arguments[0] === 36183) return 4;
                  else if (arguments[0] === 7936) return "WebKit";
                  else if (arguments[0] === 37445) return "{{37445}}";
                  else if (arguments[0] === 7937) return "WebKit WebGL";
                  else if (arguments[0] === 3379) return {{3379}};
                  else if (arguments[0] === 36347) return {{36347}};
                  else if (arguments[0] === 34076) return {{34076}};
                  else if (arguments[0] === 34024) return {{34024}};
                  else if (arguments[0] === 3386) return {{3386}};
                  else if (arguments[0] === 3413) return {{3413}};
                  else if (arguments[0] === 3412) return {{3412}};
                  else if (arguments[0] === 3411) return {{3411}};
                  else if (arguments[0] === 3410) return {{3410}};
                  else if (arguments[0] === 34047) return {{34047}};
                  else if (arguments[0] === 34930) return {{34930}};
                  else if (arguments[0] === 34921) return {{34921}};
                  else if (arguments[0] === 34324) return Math.floor({{34324}} * 6100) + 8192;
                  else if (arguments[0] === 35376) return Math.floor({{35376}} * 36384) + 10384;
                  else if (arguments[0] === 35377) return Math.floor({{35377}} * 50188) + 20188;
                  else if (arguments[0] === 35379) return Math.floor({{35379}} * 50188) + 20188;
                  else if (arguments[0] === 35658) return Math.floor({{35658}} * 36) + 1000;
                  else if (arguments[0] === 35660) return {{35660}};
                  else if (arguments[0] === 35661) return {{35661}};                  
                  else if (arguments[0] === 36349) return {{36349}};
                  else if (arguments[0] === 33902) return {{33902}};
                  else if (arguments[0] === 33901) return {{33901}};
                  else if (arguments[0] === 37446) return "{{37446}}";
                  else if (arguments[0] === 7938) return "{{7938}}";
                  else if (arguments[0] === 35724) return "{{35724}}";
                  //
                  return getParameter.apply(this, arguments);
                }
              });
            }
          }
        }
      };  
      config.spoof.webgl.buffer(WebGLRenderingContext);
      config.spoof.webgl.buffer(WebGL2RenderingContext);
      config.spoof.webgl.parameter(WebGLRenderingContext);
      config.spoof.webgl.parameter(WebGL2RenderingContext);
      console.log('==fakeWebglFingerPrint==');
    })();   
    '''
    inject_data['network'] = '''
      (function FakeNetwork() {
        var nothingtest = 1;
        var nothingtest2 = 1; 
        function processFunctions(scope) {
          var nothingtest3 = 1;
          nothingtest = nothingtest + 1;
          nothingtest2 = nothingtest2 + 1;
          nothingtest3 = nothingtest3 + 1;
        if (nothingtest2 < 3000) {
          scope.Object.defineProperty(navigator.connection, "downlink", {enumerable: true, configurable: true, get: function() {
            return [4.9,4.9,4.05,7.15,6.15,8.15,4.15,6.15,5.15,4.9,4.9,4.9,4.9,4.9,4.9,4.9,5,5,8.05,3.3,3.9,4.9,5.15,5.4,5.15,4.15,7.1,7.15,7.3,8,8.15,4.55,6.5,6.95,6.2,4.15][Math.floor(Math.random() * 36)];
          }});
            scope.Object.defineProperty(navigator.connection, "effectiveType", {enumerable: true, configurable: true, get: function() {
            return '4g';
          }});
            scope.Object.defineProperty(navigator.connection, "rtt", {enumerable: true, configurable: true, get: function() {
            return [50,150,100,100,150,150,150,150,100,100,100,100,100,150,150][Math.floor(Math.random() * 15)];
          }});
            scope.Object.defineProperty(navigator.connection, "saveData", {enumerable: true, configurable: true, get: function() {
            return false;
          }});
              
          } else {
          }				
        }
        processFunctions(window);
          var iwin = HTMLIFrameElement.prototype.__lookupGetter__('contentWindow'), idoc = HTMLIFrameElement.prototype.__lookupGetter__('contentDocument');
          Object.defineProperties(HTMLIFrameElement.prototype, {
            contentWindow: {
              get: function() {
                var frame = iwin.apply(this);
                if (this.src && this.src.indexOf('//') != -1 && location.host != this.src.split('/')[2]) return frame;
                try { frame.HTMLCanvasElement } catch (err) { /* do nothing*/ }
                try { processFunctions(frame); } catch (err) { /* do nothing*/ }
                return frame;
              }
            },
            contentDocument: {
              get: function() {
                if (this.src && this.src.indexOf('//') != -1 && location.host != this.src.split('/')[2]) return idoc.apply(this);
                var frame = iwin.apply(this);
                try { frame.HTMLCanvasElement } catch (err) { /* do nothing*/ }
                processFunctions(frame);
                return idoc.apply(this);
              }
            }
        });
        console.log('==fakeNetwork==');  
      }());
    '''
    inject_data['fonts'] = '''
    (function fakeFonts() {
      var rand = {
        "noise": function () {
          var SIGN = Math.random() < Math.random() ? -1 : 1;
          return Math.floor(Math.random() + SIGN * Math.random());
        },
        "sign": function () {
          const tmp = [-1, -1, -1, -1, -1, -1, +1, -1, -1, -1];
          const index = Math.floor(Math.random() * tmp.length);
          return tmp[index];
        }
      };
      //
      console.log('rand.sign()==',)
      Object.defineProperty(HTMLElement.prototype, "offsetHeight", {
        get () {
          const height = Math.floor(this.getBoundingClientRect().height);
          const valid = height && rand.sign() === 1;
          const result = valid ? height + rand.noise() : height;
          //
          if (valid && result !== height) {
            window.top.postMessage("font-fingerprint-defender-alert", '*');
          }
          //
          return result;
        }
      });
      //
      Object.defineProperty(HTMLElement.prototype, "offsetWidth", {
        get () {
          const width = Math.floor(this.getBoundingClientRect().width);
          const valid = width && rand.sign() === 1;
          const result = valid ? width + rand.noise() : width;

          return result;
        }
      });
      //
      console.log('==fakeFonts==');     
    })();    
    '''
    inject_data['rects'] = '''
    (function fakeClientRects() {
      var _nativegetClientRects = Element.prototype.getClientRects; 
      Element.prototype['getClientRects'] = function() { 
      return [{
              'top': 0,
              'bottom': 0,
              'left': 0,
              'right': 0,
              'height': 0,
              'width': 0
          }];
      };
      console.log('==fakeClientRects==');     
    })();
    '''  
    inject_data['webrtc'] = '''
        (function disableWebrtc() {
          if (typeof window.MediaStreamTrack !== "undefined") window.MediaStreamTrack = undefined;
          if (typeof window.RTCPeerConnection !== "undefined") window.RTCPeerConnection = undefined;
          if (typeof window.RTCSessionDescription !== "undefined") window.RTCSessionDescription = undefined;
          if (typeof window.webkitMediaStreamTrack !== "undefined") window.webkitMediaStreamTrack = undefined;
          if (typeof window.webkitRTCPeerConnection !== "undefined") window.webkitRTCPeerConnection = undefined;
          if (typeof window.webkitRTCSessionDescription !== "undefined") window.webkitRTCSessionDescription = undefined;
        })();
        console.log('==disableWebrtc=='); 
      '''
          
    
    
    return successResponse({'data':inject_data})


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
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
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_profile_by_account_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    id = request.POST['id']
    try:
        account_profile = AccountsCreated.objects.get(pk=id, owner=request.user)
    except BrowserProfiles.DoesNotExist:
        return errorResponse('Profile not found', 400)
    
    profile_data = BrowserProfilesSerializer(account_profile.browser_profiles)
    return successResponse({'data':profile_data.data})


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_key_for_search(request):
    pks = MunAnti.objects.values_list('pk', flat=True)
    KeysSearch.objects.filter()
    random_pk = choice(pks)
    random_obj = KeysSearch.objects.get(pk=random_pk)
    return successResponse({'data': random_obj.value})
  
@api_view(['GET', 'POST', 'PUT'])
@signature_test()
@user_passes_test(banned_check)
def check_version_for_update(request):
    obj_last = MunAnti.objects.first()
    if obj_last:
      if obj_last.update_url:
        update_url = obj_last.update_url
      else:
        update_url = 'https://munanti.s3.ap-southeast-1.amazonaws.com/Update.zip'
        update_data = {'modified': obj_last.modified.strftime("%d-%m-%Y %H:%M"), 'created': obj_last.created.strftime("%d-%m-%Y %H:%M") ,'version': obj_last.version, 'update_url': update_url}
        print(update_data)
      return successResponse(update_data)
    else:
      return successResponse()

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_key_for_search(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    add_post = json.loads(request.body)
    list_keys = add_post['list_keys']
    list_create = []
    for line_key in list_keys:
        key_objs = KeysSearch.objects.filter(value=line_key)
        if not key_objs.exists():
            keyObj = KeysSearch(value=line_key)
            list_create.append(keyObj)
    if list_create:
        KeysSearch.objects.bulk_create(list_create)

    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_profile_by_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)

    browser_profiles = BrowserProfiles.objects.filter(pk=update_post['id'], profile_owner=request.user)
    if browser_profiles.exists():
      browser_profiles.update(**update_post['update_data'])
      browser_profile = BrowserProfiles.objects.get(
          pk=update_post['id'], profile_owner=request.user)
      profile_data = BrowserProfilesSerializer(browser_profile)
    return successResponse({'data':profile_data.data})

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_account_by_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)

    accounts_objs = AccountsCreated.objects.filter(pk=update_post['id'], owner=request.user)
    if accounts_objs.exists():
      accounts_objs.update(**update_post['update_data'])
      account_obj = AccountsCreated.objects.get(
          pk=update_post['id'], owner=request.user)
      if 'socks5' in update_post['update_data'] and account_obj.browser_profiles:
          print('===update socks5')
          account_obj.browser_profiles.profile_socks5_details = update_post['update_data']['socks5']
          account_obj.browser_profiles.save()
      if 'proxy' in update_post['update_data'] and account_obj.browser_profiles:
          account_obj.browser_profiles.profile_proxy_details=update_post['update_data']['proxy']
          account_obj.browser_profiles.save()
      if 'proxy_username' in update_post['update_data'] and account_obj.browser_profiles:
          account_obj.browser_profiles.profile_proxy_username=update_post['update_data']['proxy_username']
          account_obj.browser_profiles.save()
      if 'proxy_password' in update_post['update_data'] and account_obj.browser_profiles:
          account_obj.browser_profiles.profile_proxy_password=update_post['update_data']['proxy_password']
          account_obj.browser_profiles.save()          
      account_data = AccountsCreatedSerializer(account_obj)
    return successResponse({'data':account_data.data})



@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def remove_profiles(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        browser_profile = BrowserProfiles.objects.filter(profile_owner=request.user)
    else:
        browser_profile = BrowserProfiles.objects.filter(pk__in=remove_post['list_id'], profile_owner=request.user)

    browser_profile.delete()
    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def remove_accounts(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        list_objects = AccountsCreated.objects.filter(
            owner=request.user)
    else:
        print('remove_post==', remove_post['list_id'])
        list_objects = AccountsCreated.objects.filter(pk__in=remove_post['list_id'], owner=request.user)
        
    if list_objects.exists():
        print('===remove===', len(list_objects))
        list_objects.delete()
    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def set_auto_views(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        list_objects = AccountsCreated.objects.filter(
            owner=request.user)
    else:
        print('remove_post==', remove_post['list_id'])
        list_objects = AccountsCreated.objects.filter(
            pk__in=remove_post['list_id'], owner=request.user)

    if list_objects.exists():
        print('===update===', len(list_objects))
        list_objects.update(auto_view=True)
    return successResponse()
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def remove_auto_views(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        list_objects = AccountsCreated.objects.filter(
            owner=request.user)
    else:
        print('remove_post==', remove_post['list_id'])
        list_objects = AccountsCreated.objects.filter(
            pk__in=remove_post['list_id'], owner=request.user)

    if list_objects.exists():
        print('===update===', len(list_objects))
        list_objects.update(auto_view=False)
    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_profile_for_auto_views(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    account_type = remove_post['account_type']
    data_show = {}
    if account_type == 'amazon':
        account_objects = AccountsCreated.objects.filter(
            owner=request.user, type__value=account_type, auto_view=True)
        print('account_objects', len(account_objects))
        if account_objects.exists():
            account_obj = account_objects.earliest('auto_viewed')
            account_obj.auto_viewed = timezone.now()
            account_obj.save()
            profile_data = BrowserProfilesSerializer(account_obj.browser_profiles)
            data_show['data'] = profile_data.data
    return successResponse(data_show)


def create_random_profile(self, sock5='', proxy='', phoneOs=False):
    profile_dict = {}

    #GEO

    profile_dict['profile_geo'] = 2

    #webrtc

    profile_dict['profile_webrtc'] = 2
    #time_zone

    profile_dict['profile_time_zone'] = 2

    #proxy
    profile_dict['profile_socks5_details'] = sock5
    profile_dict['profile_proxy_details'] = proxy
    profile_dict['profile_proxy_type'] = 2
    #audio

    list_length = 44100
    listAudioContent = {}
    i = 0
    while i < list_length:
        index = int(random.uniform(0.01, 0.99)*i)
        listAudioContent[index] = round(
            random.uniform(0.01, 0.99) * 0.0000001, 15)
        i += 100
    audio_random1 = round(random.uniform(0.01, 0.99), 15)
    audio_random2 = round(random.uniform(0.01, 0.99), 15)
    audio_dict = {}
    audio_dict['audio_content'] = listAudioContent
    audio_dict['audio_random1'] = audio_random1
    audio_dict['audio_random2'] = audio_random2
    profile_dict['profile_audio'] = json.dumps(audio_dict)
    #canvas

    list_canvas = [-3, -2, -1, 0, 1, 2, 3]
    rsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    gsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    bsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    asalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
    canvas_shift = {'r': rsalt_content, 'g': gsalt_content,
                    'b': bsalt_content, 'a': asalt_content}
    profile_dict['profile_canvas'] = json.dumps(canvas_shift)

    #webgl
    list_floats = [math.pow(2, 0), math.pow(2, 10), math.pow(
        2, 11), math.pow(2, 12), math.pow(2, 13)]
    list_int = [math.pow(2, 13), math.pow(2, 14), math.pow(2, 15)]
    int_3386 = int(list_int[random.randint(0, len(list_int) - 1)])
    list_1234 = [math.pow(2, 1), math.pow(
        2, 2), math.pow(2, 3), math.pow(2, 4)]
    list_1415 = [math.pow(2, 14), math.pow(2, 15)]
    list_1213 = [math.pow(2, 12), math.pow(2, 13)]
    list_45678 = [math.pow(2, 4), math.pow(2, 5), math.pow(
        2, 6), math.pow(2, 7), math.pow(2, 8)]
    list_10111213 = [math.pow(2, 10), math.pow(
        2, 11), math.pow(2, 12), math.pow(2, 13)]
    webgl_replace = {}
    webgl_replace['36347'] = int(
        list_1213[random.randint(0, len(list_1213) - 1)])
    webgl_replace['3379'] = int(
        list_1415[random.randint(0, len(list_1415) - 1)])
    webgl_replace['34076'] = int(
        list_1415[random.randint(0, len(list_1415) - 1)])
    webgl_replace['34024'] = int(
        list_1415[random.randint(0, len(list_1415) - 1)])
    webgl_replace['35661'] = int(
        list_45678[random.randint(0, len(list_45678) - 1)])
    webgl_replace['36349'] = int(
        list_10111213[random.randint(0, len(list_10111213) - 1)])
    webgl_replace['3413'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['3412'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['3411'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['3410'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['35660'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['34047'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['34930'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['34921'] = int(
        list_1234[random.randint(0, len(list_1234) - 1)])
    webgl_replace['3386'] = [int_3386, int_3386]
    webgl_replace['33901'] = [round(random.uniform(
        0.01, 1), 15), list_floats[random.randint(0, len(list_floats) - 1)]]
    webgl_replace['33902'] = [round(random.uniform(
        0.01, 1), 15), list_floats[random.randint(0, len(list_floats) - 1)]]
    webgl_replace['34324'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['35376'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['35377'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['35379'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['35658'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['gl_index'] = round(random.uniform(0.01, 0.99), 15)
    webgl_replace['gl_noise'] = round(random.uniform(0.01, 0.99), 15)
    # list_vgas[random.randint(0, len(list_vgas) - 1)]
    list_vgas = ['ANGLE (NVIDIA Quadro 2000M Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA Quadro K420 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro 2000M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro K2000M Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 3800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0)','ANGLE (AMD Radeon R9 200 Series Direct3D11 vs_5_0 ps_5_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 3000 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 4 Series Express Chipset Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) Graphics Media Accelerator 3150 Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) G41 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 6150SE nForce 430 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 4000)','ANGLE (Mobile Intel(R) 965 Express Chipset Family Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (NVIDIA GeForce GTX 760 Direct3D11 vs_5_0 ps_5_0)','ANGLE (AMD Radeon HD 6310 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Graphics Media Accelerator 3600 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (AMD Radeon HD 6320 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) G41 Express Chipset)','ANGLE (ATI Mobility Radeon HD 5470 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q45/Q43 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 310M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G41 Express Chipset Direct3D9 vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 45 Express Chipset Family (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 440 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4300/4500 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7310 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics)','ANGLE (Intel(R) 4 Series Internal Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon(TM) HD 6480G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 3200 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 210 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 630 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7340 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) 82945G Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 430 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 7025 / NVIDIA nForce 630a Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q35 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (Intel(R) HD Graphics 4600 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7520G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD 760G (Microsoft Corporation WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 220 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9500 GT Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Family Direct3D9 vs_3_0 ps_3_0)','ANGLE (Intel(R) Graphics Media Accelerator HD Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9800 GT Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GTX 550 Ti Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (AMD M880G with ATI Mobility Radeon HD 4250 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 650 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Mobility Radeon HD 5650 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7700 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G33/G31 Express Chipset Family)','ANGLE (Intel(R) 82945G Express Chipset Family Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (SiS Mirage 3 Graphics Direct3D9Ex vs_2_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 430)','ANGLE (AMD RADEON HD 6450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon 3000 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) 4 Series Internal Chipset Direct3D9 vs_3_0 ps_3_0)','ANGLE (Intel(R) Q35 Express Chipset Family (Microsoft Corporation - WDDM 1.0) Direct3D9Ex vs_0_0 ps_2_0)','ANGLE (NVIDIA GeForce GT 220 Direct3D9 vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 7640G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD 760G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 640 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9200 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 610 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6290 Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Mobility Radeon HD 4250 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 8600 GT Direct3D9 vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 5570 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 6800 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) G45/G43 Express Chipset Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 4600 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro NVS 160M Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics 3000)','ANGLE (NVIDIA GeForce G100)','ANGLE (AMD Radeon HD 8610G + 8500M Dual Graphics Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 4 Series Express Chipset Family Direct3D9 vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 7025 / NVIDIA nForce 630a (Microsoft Corporation - WDDM) Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) Q965/Q963 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)','ANGLE (AMD RADEON HD 6350 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (ATI Radeon HD 5450 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce 9500 GT)','ANGLE (AMD Radeon HD 6500M/5600/5700 Series Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Mobile Intel(R) 965 Express Chipset Family)','ANGLE (NVIDIA GeForce 8400 GS Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (Intel(R) HD Graphics Direct3D9 vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 560 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 620 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GTX 660 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon(TM) HD 6520G Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA GeForce GT 240 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (AMD Radeon HD 8240 Direct3D9Ex vs_3_0 ps_3_0)','ANGLE (NVIDIA Quadro NVS 140M)','ANGLE (Intel(R) Q35 Express Chipset Family Direct3D9 vs_0_0 ps_2_0)']
    if phoneOs:
      webgl_replace['37446'] = 'Apple GPU'
    else:
      webgl_replace['37446'] = list_vgas[random.randint(0, len(list_vgas) - 1)]
    list_es = ["WebGL 2.0 (OpenGL ES 3.0 Chromium)"]
    list_glsl = ["WebGL GLSL ES (OpenGL Chromium)","WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)"]
    webgl_replace['7938'] = list_es[random.randint(0, len(list_es) - 1)]
    webgl_replace['35724'] = list_glsl[random.randint(0, len(list_glsl) - 1)]
    if phoneOs:
      gpu_vendor = "Apple Computer, Inc."
    else:
      gpu_vendor = "Google Inc. (ATI Technologies Inc.)"
    webgl_replace['37445'] = gpu_vendor 
    profile_dict['profile_webgl'] = json.dumps(webgl_replace)
    profile_dict['profile_name'] = ''
    # profile_dict['profile_user_agent'] = ''
    list_os = ['Window', 'Mac OS X', 'Linux', 'Chrome OS']
    comboBoxOS = list_os[random.randint(0, len(list_os)-1)]
    AgentOperationOS = ''
    if comboBoxOS == 'Window':
        AgentOperationOS = 'Windows NT 10.0; Win64; x64'
    elif comboBoxOS == 'Mac OS X':
      AgentOperationOS = 'Macintosh; Intel Mac OS X 12_5_1'
    elif comboBoxOS == 'Linux':
      AgentOperationOS = 'X11; Linux x86_64'
    else:
      AgentOperationOS = "X11; CrOS x86_64 14909.100.0"
      
    self.list_cpu = ["2","4","6","8","10"]
    self.list_screen_resolution = ['1920x1200','1920x1080','1536x864','1440x900','1366x768','1280x720']
    
    self.list_chrome_version = ["105.0.5195.125","105.0.0.0","105.0.5195.136","104.0.5112.79","104.0.0.0"]
          
    self.list_iPhone_resolution = {'iPhone 14 Pro Max':{'resolution':'430x932','scale':'3'},'iPhone 14 Pro':{'resolution':'393x852','scale':'3'}, 'iPhone 14 Plus':{'resolution':'428x926','scale':'3'},'iPhone 14':{'resolution':'390x844','scale':'3'},'iPhone SE 3rd gen':{'resolution':'375x667','scale':'2'},'iPhone 13':{'resolution':'390x844','scale':'3'}, 'iPhone 13 mini':{'resolution':'375x812','scale':'3'},'iPhone 13 Pro Max':{'resolution':'428x926','scale':'3'}, 'iPhone 13 Pro':{'resolution':'390x844','scale':'3'}, 'iPhone 12':{'resolution':'390x844','scale':'3'},'iPhone 12 mini':{'resolution':'375x812','scale':'3'}, 'iPhone 12 Pro Max':{'resolution':'428x926','scale':'3'}, 'iPhone 12 Pro': {'resolution':'390x844','scale':'3'}, 'iPhone SE 2nd gen':{'resolution':'375x667','scale':'2'}, 'iPhone 11 Pro Max':{'resolution':'414x896','scale':'3'}, 'iPhone 11 Pro':{'resolution':'375x812','scale':'3'}, 'iPhone 11':{'resolution':'414x896','scale':'2'}, 'iPhone XR':{'resolution':'414x896','scale':'2'}, 'iPhone XS Max':{'resolution':'414x896','scale':'3'}, 'iPhone XS':{'resolution':'375x812','scale':'3'}, 'iPhone X':{'resolution':'375x812','scale':'3'}}
    Agentversion = self.list_chrome_version[random.randint(
          0, len(self.list_chrome_version)-1)]
    if phoneOs:
      list_phone_os = list(self.list_iPhone_resolution.keys())
      # print(list_phone_os)
      comboBoxOS = list_phone_os[random.randint(0, len(list_phone_os)-1)]
      self.user_header_set = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/%s Mobile/15E148 Safari/604.1" % (Agentversion)		
      profile_resolution = self.list_iPhone_resolution[comboBoxOS]['resolution']
    else:
      self.user_header_set = "Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % (
                      AgentOperationOS, Agentversion)
    
      profile_resolution = self.list_screen_resolution[random.randint(
          0, len(self.list_screen_resolution)-1)]
    profile_cpu = self.list_cpu[random.randint(
        0, len(self.list_cpu)-1)]
    
    profile_dict['profile_user_agent'] = self.user_header_set
    profile_dict['profile_os'] = comboBoxOS
    profile_dict['profile_resolution'] = profile_resolution
    profile_dict['profile_cpu'] = profile_cpu
    if sock5:
        profile_dict['profile_proxy_details'] = sock5
    elif proxy:
        profile_dict['profile_proxy_details'] = proxy
    else:
        profile_dict['profile_proxy_details'] = ''

    profile_dict['profile_rects'] = 'Noise'
    profile_dict['profile_font'] = 'Noise'
    profile_dict['profile_start_url'] = ''
    return profile_dict

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_new_profiles(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        list_objects = BrowserProfiles.objects.filter(
            owner=request.user)
    else:
        list_objects = BrowserProfiles.objects.filter(
            pk__in=remove_post['list_id'], owner=request.user)

    if list_objects.exists():
        print('===update===', len(list_objects))
        i = 0
        for line_profile in list_objects:
            profile_dict = create_random_profile()
            browser_profiles_objs = BrowserProfiles.objects.filter(pk=line_profile.id)
            browser_profiles_objs.update(**profile_dict)
            i+=1

    return successResponse()

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def accounts_update_new_profiles(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        list_objects = AccountsCreated.objects.filter(
            owner=request.user)
    else:
        print('remove_post==', remove_post['list_id'])
        list_objects = AccountsCreated.objects.filter(
            pk__in=remove_post['list_id'], owner=request.user)

    if list_objects.exists():
        print('===update===', len(list_objects))
        i = 0
        for line_account in list_objects:
            profile_dict = create_random_profile()
            browser_profiles_objs = BrowserProfiles.objects.filter(pk=line_account.browser_profiles.id)
            browser_profiles_objs.update(**profile_dict)
            i+=1
    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def create_browser_profile(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    #{'profile_name': '', 'profile_os': 'Window', 'profile_browser': 'Chrome', 'profile_version': '102.0.5005.63', 'profile_proxy': 'No Proxy', 'profile_proxy_details': '', 'profile_path_cookies': '', 'profile_user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36', 'profile_resolution': '1920×1080', 'profile_cpu': '8', 'profile_canvas': 'Noise', 'profile_rects': 'Noise', 'profile_font': 'Noise', 'profile_audio': 'Noise', 'profile_webgl': 'Noise', 'profile_time_zone': 'Follow IP', 'profile_webrtc': 'Follow IP', 'profile_geo': 'Follow IP', 'profile_vendor': 'Google Inc. (ATI Technologies Inc.)', 'profile_renderer': 'ANGLE (Intel(R) G41 Express Chipset (Microsoft Corporation - WDDM 1.1) Direct3D9Ex vs_3_0 ps_3_0)', 'profile_start_url': 'https://iphey.com'}
    
    profile_post = json.loads(request.body)
    print('=====profile_post',profile_post)
    profile_dict = profile_post
    block = 0
    noise = 1
    follow = 2    
    #GEO
    if profile_post['profile_geo'] == 'Follow IP':
        profile_dict['profile_geo'] = follow
    else:
        profile_dict['profile_geo'] = block
    #webrtc
    if profile_post['profile_webrtc'] == 'Follow IP':
        profile_dict['profile_webrtc'] = 2
    elif profile_post['profile_webrtc'] == 'Block':
        profile_dict['profile_webrtc'] = 0
    else:
        profile_dict['profile_webrtc'] = 1
    #time_zone
    if profile_post['profile_time_zone'] == 'Follow IP':
        profile_dict['profile_time_zone'] = 2
    else:
        profile_dict['profile_time_zone'] = 0
    #proxy
    if profile_post['profile_proxy_type'] == 'No Proxy':
        profile_dict['profile_proxy_type'] = 0
    elif profile_post['profile_proxy_type'] == 'Proxy':
        profile_dict['profile_proxy_type'] = 1
    else:
        profile_post['profile_proxy_type'] = 2
    #audio
    if profile_post['profile_audio'] == 'Noise':
        list_length = 44100
        listAudioContent = {}
        i=0
        while i < list_length:
            index = int(random.uniform(0.01, 0.99)*i)
            listAudioContent[index] = round(random.uniform(0.01, 0.99) * 0.0000001, 15)
            i+=100
        audio_random1 = round(random.uniform(0.01, 0.99), 15)
        audio_random2 = round(random.uniform(0.01, 0.99), 15)
        audio_dict = {}
        audio_dict['audio_content'] = listAudioContent
        audio_dict['audio_random1'] = audio_random1
        audio_dict['audio_random2'] = audio_random2
        profile_dict['profile_audio'] = json.dumps(audio_dict)
    #canvas
    if profile_post['profile_canvas'] == 'Noise':
        list_canvas = [-3,-2,-1,0,1,2,3]
        rsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        gsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        bsalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        asalt_content = list_canvas[random.randint(0, len(list_canvas) - 1)]
        canvas_shift = {'r': rsalt_content,'g': gsalt_content,'b': bsalt_content,'a': asalt_content}
        profile_dict['profile_canvas'] = json.dumps(canvas_shift)
    
    if profile_post['profile_webgl'] == 'Noise':
        #webgl
        list_floats = [math.pow(2, 0), math.pow(2, 10), math.pow(2, 11), math.pow(2, 12), math.pow(2, 13)];
        list_int = [math.pow(2, 13), math.pow(2, 14), math.pow(2, 15)]
        int_3386 = int(list_int[random.randint(0, len(list_int) - 1)])
        list_1234 = [math.pow(2, 1), math.pow(2, 2), math.pow(2, 3), math.pow(2, 4)]
        list_1415 = [math.pow(2, 14), math.pow(2, 15)]
        list_1213 = [math.pow(2, 12), math.pow(2, 13)]
        list_45678 = [math.pow(2, 4), math.pow(2, 5), math.pow(2, 6), math.pow(2, 7), math.pow(2, 8)]
        list_10111213 = [math.pow(2, 10), math.pow(2, 11), math.pow(2, 12), math.pow(2, 13)]
        webgl_replace = {}
        webgl_replace['36347'] = int(list_1213[random.randint(0, len(list_1213) - 1)])
        webgl_replace['3379'] = int(list_1415[random.randint(0, len(list_1415) - 1)])
        webgl_replace['34076'] = int(list_1415[random.randint(0, len(list_1415) - 1)])
        webgl_replace['34024'] = int(list_1415[random.randint(0, len(list_1415) - 1)])
        webgl_replace['35661'] = int(list_45678[random.randint(0, len(list_45678) - 1)])
        webgl_replace['36349'] = int(list_10111213[random.randint(0, len(list_10111213) - 1)])
        webgl_replace['3413'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['3412'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['3411'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['3410'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['35660'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['34047'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['34930'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['34921'] = int(list_1234[random.randint(0, len(list_1234) - 1)])
        webgl_replace['3386'] = [int_3386, int_3386]
        webgl_replace['33901'] = [round(random.uniform(0.01, 1),15), list_floats[random.randint(0, len(list_floats) - 1)]]
        webgl_replace['33902'] = [round(random.uniform(0.01, 1), 15), list_floats[random.randint(0, len(list_floats) - 1)]]
        webgl_replace['34324'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['35376'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['35377'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['35379'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['35658'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['gl_index'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['gl_noise'] = round(random.uniform(0.01, 0.99), 15)
        webgl_replace['37446'] = profile_post['profile_renderer']#list_vgas[random.randint(0, len(list_vgas) - 1)]
        list_es = ["WebGL 2.0 (OpenGL ES 3.0 Chromium)"]
        list_glsl = ["WebGL GLSL ES (OpenGL Chromium)","WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)"]
        webgl_replace['7938'] = list_es[random.randint(0, len(list_es) - 1)]
        webgl_replace['35724'] = list_glsl[random.randint(0, len(list_glsl) - 1)]
        gpu_vendor = "Google Inc. (ATI Technologies Inc.)"
        webgl_replace['37445'] = profile_post['profile_vendor']#gpu_vendor
        profile_dict['profile_webgl'] = json.dumps(webgl_replace)
    print('request.user==', request.user)
    browser_profiles = BrowserProfiles(profile_owner=request.user,**profile_dict)
    browser_profiles.save()
    profile_data = BrowserProfilesSerializer(browser_profiles)

    ##
    return successResponse({'data':profile_data.data})

