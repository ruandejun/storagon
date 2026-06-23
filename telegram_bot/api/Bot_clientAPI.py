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
from telegram_bot.task import check_cmd_telegram, check_cmd_telegram_gpt, check_cmd_cashback_telegram
from telegram_bot.models import *
from telegram_bot.api.TelegramBot_RestfulApi import *
import random, math
from random import choice
from django.utils import timezone
from django.http import FileResponse
from servermain.models import AccountBalance, AccountCurrency
from servermain.controllers import UserController
from coinbase_commerce.error import WebhookInvalidPayload, SignatureVerificationError
from coinbase_commerce.webhook import Webhook
from django.db import transaction
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
            check_cmd_telegram.delay(chat_id, t_message_id, text, chat=t_chat)
        if 'document' in t_message:
            chat_id = t_chat["id"]
            document = t_message['document']
            check_cmd_telegram.delay(chat_id, message_id=t_message_id, chat=t_chat, document=document)
    elif 'callback_query' in t_data:
        t_message = t_data["callback_query"]
        t_reply_to_message = t_message["message"]
        from_user = t_message['from']
        chat_id = from_user['id']
        data = t_message['data']
        t_message_id = t_reply_to_message["message_id"]
        original_text = t_message.get('text')
        # print(from_user['id'],data)
        check_cmd_telegram.delay(chat_id,message_id=t_message_id,callback_query=data,original_text=original_text)


    return successResponse({"ok": "POST request processed"})

@api_view(['GET', 'POST', 'PUT'])
def telegram_cashback_bot(request):
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
            check_cmd_cashback_telegram.delay(chat_id, t_message_id, text, chat=t_chat)
        if 'document' in t_message:
            chat_id = t_chat["id"]
            document = t_message['document']
            check_cmd_cashback_telegram.delay(chat_id, message_id=t_message_id, chat=t_chat, document=document)
    elif 'callback_query' in t_data:
        t_message = t_data["callback_query"]
        t_reply_to_message = t_message["message"]
        from_user = t_message['from']
        chat_id = from_user['id']
        data = t_message['data']
        t_message_id = t_reply_to_message["message_id"]
        original_text = t_message.get('text')
        # print(from_user['id'],data)
        check_cmd_cashback_telegram.delay(chat_id,message_id=t_message_id,callback_query=data,original_text=original_text)


    return successResponse({"ok": "POST request processed"})
  
@api_view(['GET', 'POST', 'PUT'])
def telegram_gpt_bot(request):
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
            check_cmd_telegram_gpt.delay(chat_id, t_message_id, text, chat=t_chat)
        if 'document' in t_message:
            chat_id = t_chat["id"]
            document = t_message['document']
            check_cmd_telegram_gpt.delay(chat_id, message_id=t_message_id, chat=t_chat, document=document)
    elif 'callback_query' in t_data:
        t_message = t_data["callback_query"]
        t_reply_to_message = t_message["message"]
        from_user = t_message['from']
        chat_id = from_user['id']
        data = t_message['data']
        t_message_id = t_reply_to_message["message_id"]
        original_text = t_message.get('text')
        # print(from_user['id'],data)
        check_cmd_telegram_gpt.delay(chat_id,message_id=t_message_id,callback_query=data,original_text=original_text)


    return successResponse({"ok": "POST request processed"})

@api_view(['GET', 'POST', 'PUT'])
def coinbase_bot(request):
    
    WEBHOOK_SECRET = 'e2d8dfc2-c1d5-47c8-bfbe-c2d65e7fdca5'
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    request_data = request.body
    print(request_data)
    # request_data = request.data
    # webhook signature
    request_sig = request.headers.get('X-CC-Webhook-Signature', None)

    try:
        # signature verification and event object construction
        event = Webhook.construct_event(request_data, request_sig, WEBHOOK_SECRET)
    except (WebhookInvalidPayload, SignatureVerificationError) as e:
        pass
    else:
        print("Received event: id={id}, type={type}".format(id=event.id, type=event.type))
        if event.type == 'charge:confirmed':
            print('==charge:confirmed==')
            metadata = event.data['metadata']
            payments = event.data['payments']
            pricing = event.data['pricing']
            addresses = event.data['addresses']
            print('====',metadata, payments, pricing, addresses)
        # print(event)
    # return 'success', 200
    return successResponse({"ok": "POST request processed"})


def _get_pagination_params(request):
    page = None
    page_size = None
    if hasattr(request, 'query_params') and request.query_params:
        page = request.query_params.get('page')
        page_size = request.query_params.get('page_size')
    if not page and hasattr(request, 'GET') and request.GET:
        page = request.GET.get('page')
    if not page_size and hasattr(request, 'GET') and request.GET:
        page_size = request.GET.get('page_size')
    if not page and hasattr(request, 'data') and isinstance(request.data, dict):
        page = request.data.get('page')
    if not page_size and hasattr(request, 'data') and isinstance(request.data, dict):
        page_size = request.data.get('page_size')
    if not page and hasattr(request, 'POST') and request.POST:
        page = request.POST.get('page')
    if not page_size and hasattr(request, 'POST') and request.POST:
        page_size = request.POST.get('page_size')
    return page, page_size


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_browser_profiles(request):
    browser_profiles = BrowserProfiles.objects.filter(profile_owner=request.user).select_related('profile_owner').order_by('-id')

    page, page_size = _get_pagination_params(request)
    if page or page_size:
        from system_configure.controllers.Tool import StandardResultsSetPagination
        paginator = StandardResultsSetPagination()
        if page_size:
            try:
                paginator.page_size = int(page_size)
            except ValueError:
                pass
        paginated_qs = paginator.paginate_queryset(browser_profiles, request)
        if paginated_qs is not None:
            profile_data = BrowserProfilesSerializer(paginated_qs, many=True)
            return successResponse({
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'data': profile_data.data
            })

    browser_profiles = browser_profiles[:1000]
    profile_data = BrowserProfilesSerializer(browser_profiles, many=True)

    ##
    return successResponse({'data':profile_data.data})



@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_emails(request):
    account_type = request.GET.get('account_type')
    action = request.GET.get('action')
    from django.db.models import Q
    list_objects = AccountsEmails.objects.filter(Q(owner=request.user) | Q(created_by=request.user)).select_related('customer', 'owner', 'created_by', 'type').prefetch_related('accounts_emails_set__type').order_by('-id')
    if account_type:
      if action == 'create_accounts':
        list_objects = list_objects.exclude(accounts_emails_set__type__value=account_type).filter(status=0)
        pks = list_objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        list_objects = AccountsEmails.objects.filter(pk=random_pk)
        list_objects.update(status=3)
      elif action == 'list_signup_emails':
        list_objects = list_objects.exclude(accounts_emails_set__type__value=account_type).filter(status=0)
        # pks = list_objects.values_list('pk', flat=True)
        # random_pk = choice(pks)
        # list_objects = AccountsEmails.objects.filter(pk=random_pk)
        # list_objects.update(status=3)  
      else:
        list_objects = list_objects.filter(accounts_emails_set__type__value=account_type)

    page, page_size = _get_pagination_params(request)
    if page or page_size:
        from system_configure.controllers.Tool import StandardResultsSetPagination
        paginator = StandardResultsSetPagination()
        if page_size:
            try:
                paginator.page_size = int(page_size)
            except ValueError:
                pass
        paginated_qs = paginator.paginate_queryset(list_objects, request)
        if paginated_qs is not None:
            accounts_data = AccountsEmailsSerializer(paginated_qs, many=True)
            return successResponse({
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'data': accounts_data.data
            })

    list_objects = list_objects[:1000]
    accounts_data = AccountsEmailsSerializer(list_objects, many=True)

    return successResponse({'data':accounts_data.data})
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_accounts_emails(request):
    accounts_playload = json.loads(request.body)
    list_emails = accounts_playload['list_emails']
    for e in list_emails:
        email_clean = e.get('email', '').strip()
        if not email_clean:
            continue
        obj = AccountsEmails(
            owner=request.user,
            created_by=request.user,
            email=email_clean,
            password=e.get('password', '')
        )
        obj.save()
    return successResponse() 

  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_accounts_emails(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)

    from django.db.models import Q
    accounts_emails_qs = AccountsEmails.objects.filter(Q(pk=update_post['id']) & (Q(owner=request.user) | Q(created_by=request.user)))
    if accounts_emails_qs.exists():
      email_obj = accounts_emails_qs.first()
      for key, value in update_post['update_data'].items():
          setattr(email_obj, key, value)
      email_obj.save()
      accounts_emails_data = AccountsEmailsSerializer(email_obj)
    return successResponse({'data':accounts_emails_data.data})
  

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_mun_proxies(request):
    list_objects = MunProxies.objects.filter(owner=request.user).order_by('-id')

    page, page_size = _get_pagination_params(request)
    if page or page_size:
        from system_configure.controllers.Tool import StandardResultsSetPagination
        paginator = StandardResultsSetPagination()
        if page_size:
            try:
                paginator.page_size = int(page_size)
            except ValueError:
                pass
        paginated_qs = paginator.paginate_queryset(list_objects, request)
        if paginated_qs is not None:
            object_data = MunProxiesSerializer(paginated_qs, many=True)
            return successResponse({
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'data': object_data.data
            })

    list_objects = list_objects[:1000]
    object_data = MunProxiesSerializer(list_objects, many=True)

    ##
    return successResponse({'data':object_data.data})
  
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_link_checkout(request):
    data_show = []
    if request.GET.get('action') == 'random':
        list_objects = LinkCheckout.objects.filter(status=0)
        if request.GET.get('type'):
            list_objects = list_objects.filter(type__value=request.GET['type'])
        if list_objects.exists():
            pks = list_objects.values_list('pk', flat=True)
            random_pk = choice(pks)
            random_obj = LinkCheckout.objects.filter(pk=random_pk)
            accounts_data = LinkCheckoutSerializer(random_obj, many=True) 
            data_show = accounts_data.data
    else:
        list_objects = LinkCheckout.objects.filter(status=0).order_by('-id')

        accounts_data = LinkCheckoutSerializer(list_objects, many=True)
        data_show = accounts_data.data
    return successResponse({'data':data_show}) 

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_link_checkout(request):
    list_create = []
    list_playload = json.loads(request.body)
    accountObj, created = AccountsType.objects.get_or_create(value=list_playload['type'], label=list_playload['type'])
    checkFailedStatus = LinkCheckout.objects.filter(status=LinkStatus.failed, type__value=list_playload['type'])
    if checkFailedStatus.exists():
        for line in list_playload['data']:
            checkFailedStatus = LinkCheckout.objects.filter(status=LinkStatus.failed, type__value=list_playload['type'])
            if not LinkCheckout.objects.filter(url=line).exists() and checkFailedStatus.exists():
                linkObj = checkFailedStatus[0]
                linkObj.url = line
                linkObj.status = LinkStatus.working
                linkObj.save()  
            if not checkFailedStatus.exists():
                list_create.append(LinkCheckout(url=line, type=accountObj))
            LinkCheckout.refresh_from_db()
    else:
        for line in list_playload['data']:
            if not LinkCheckout.objects.filter(url=line).exists():
                list_create.append(LinkCheckout(url=line, type=accountObj))
    if list_create:
        LinkCheckout.objects.bulk_create(list_create)
    return successResponse()  

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_link_checkout(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)
    link_checkout_obj = LinkCheckout.objects.filter(url=update_post['url'].strip())
    if link_checkout_obj.exists():
        link_checkout_obj.update(**update_post['update_data'])
        link_checkout_obj = LinkCheckout.objects.filter(
            url=update_post['url'])
        link_checkout_data = LinkCheckoutSerializer(link_checkout_obj, many=True)
        return successResponse({'data':link_checkout_data.data})
    else:
        return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_created(request):
    if request.GET.get('action') == 'random':
        list_objects = AccountsCreated.objects.filter(owner=None, status=0)
        if request.GET.get('type'):
            list_objects = list_objects.filter(type__value=request.GET['type'])
  
        pks = list_objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = AccountsCreated.objects.filter(pk=random_pk)
        accounts_data = AccountsCreatedSerializer(random_obj, many=True) 
    else:
        list_objects = AccountsCreated.objects.filter(owner=request.user).select_related(
            'customer', 'owner', 'created_by', 'type', 'browser_profiles', 'accounts_emails'
        ).order_by('-id')

        page, page_size = _get_pagination_params(request)
        if page or page_size:
            from system_configure.controllers.Tool import StandardResultsSetPagination
            paginator = StandardResultsSetPagination()
            if page_size:
                try:
                    paginator.page_size = int(page_size)
                except ValueError:
                    pass
            paginated_qs = paginator.paginate_queryset(list_objects, request)
            if paginated_qs is not None:
                accounts_data = AccountsCreatedSerializer(paginated_qs, many=True)
                return successResponse({
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'data': accounts_data.data
                })

        list_objects = list_objects[:1000]
        accounts_data = AccountsCreatedSerializer(list_objects, many=True)

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
    if 'email_id' in accounts_playload:
      email_id = accounts_playload['email_id']
    else:
      email_id = ''
    if 'data_id' in accounts_playload:
      data_id = accounts_playload['data_id']
    else:
      data_id = ''
    profile_objects = BrowserProfiles.objects.filter(pk=profile_id)
    if not profile_objects.exists():
        return errorResponse('Profile not found', 400) 
    account_type, created = AccountsType.objects.get_or_create(value=type.lower(), defaults={'label': type.title()})
    accounts_data = AccountsCreated(email=email, password=password, browser_profiles=profile_objects[0], type=account_type, owner=request.user)
    if data_id:
      data_objects = AccountsData.objects.filter(pk=data_id)
      if data_objects.exists:
        accounts_data.accounts_data = data_objects[0]
    if email_id:
      email_objects = AccountsEmails.objects.filter(pk=email_id)
      if email_objects.exists:
        accounts_data.accounts_emails = email_objects[0]   
    if 'phone_number' in accounts_playload:
      accounts_data.phone_number = accounts_playload['phone_number']
    if 'signup_ip' in accounts_playload:
      accounts_data.signup_ip = str(accounts_playload['signup_ip'])
    if 'two_factor_auth' in accounts_playload:
      accounts_data.two_factor_auth = accounts_playload['two_factor_auth']
    if 'cookies' in accounts_playload:
      accounts_data.cookies = accounts_playload['cookies']
    if 'username' in accounts_playload:
      accounts_data.username = accounts_playload['username']
    accounts_data.save()
    accounts_data.refresh_from_db()
    data_serializer = AccountsCreatedSerializer(accounts_data, many=False)
    
    return successResponse({'data':data_serializer.data}) 
 
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_accounts_data(request):  
    if request.GET.get('action') == 'create_accounts':
        list_objects = AccountsData.objects.filter(owner=None, status=0)
        if request.GET.get('state'):
            list_objects = list_objects.filter(state=request.GET['state'])
        if request.GET.get('city'):
            list_objects = list_objects.filter(city=request.GET['city'])
        if request.GET.get('account_type'):
            list_objects = list_objects.exclude(account_data_created_set__type__value=request.GET['account_type'])
        if request.GET.get('email_type'):
            list_objects = list_objects.exclude(account_data_emails_set__type__value=request.GET['email_type']) 
            
        pks = list_objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = AccountsData.objects.filter(pk=random_pk)
        accounts_data = AccountsDataSerializer(random_obj, many=True)
        random_obj.update(status=3)
    elif request.GET.get('action') == 'random_address':
        list_objects = AccountsData.objects.filter(owner=None, status=0)
        if request.GET.get('state'):
            list_objects = list_objects.filter(state=request.GET['state'])
        if request.GET.get('city'):
            list_objects = list_objects.filter(city=request.GET['city'])
        if request.GET.get('account_type'):
            list_objects = list_objects.exclude(account_data_created_set__type__value=request.GET['account_type'])
        if request.GET.get('email_type'):
            list_objects = list_objects.exclude(account_data_emails_set__type__value=request.GET['email_type']) 
            
        pks = list_objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = AccountsData.objects.filter(pk=random_pk)
        accounts_data = AccountsDataSerializer(random_obj, many=True)
    else:
        list_objects = AccountsData.objects.filter(owner=request.user).select_related(
            'customer', 'owner', 'type'
        ).order_by('-id')

        page, page_size = _get_pagination_params(request)
        if page or page_size:
            from system_configure.controllers.Tool import StandardResultsSetPagination
            paginator = StandardResultsSetPagination()
            if page_size:
                try:
                    paginator.page_size = int(page_size)
                except ValueError:
                    pass
            paginated_qs = paginator.paginate_queryset(list_objects, request)
            if paginated_qs is not None:
                accounts_data = AccountsDataSerializer(paginated_qs, many=True)
                return successResponse({
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'data': accounts_data.data
                })

        list_objects = list_objects[:1000]
        accounts_data = AccountsDataSerializer(list_objects, many=True)
    return successResponse({'data':accounts_data.data})

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_accounts_data(request):
    list_playload = json.loads(request.body)
    list_create = []
    for line in list_playload:
      list_create.append(AccountsData(**line))
    if list_create:
        AccountsData.objects.bulk_create(list_create)
    return successResponse() 

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_accounts_data(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)
    accounts_emails_obj = AccountsData.objects.filter(pk=update_post['id'], owner=request.user)
    if accounts_emails_obj.exists():
      accounts_emails_obj.update(**update_post['update_data'])
      accounts_emails_obj = AccountsData.objects.get(
          pk=update_post['id'], profile_owner=request.user)
      accounts_emails_data = AccountsDataSerializer(accounts_emails_obj)
    return successResponse({'data':accounts_emails_data.data})



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
    inject_data['UserAgent'] = '''
    (function fakeUserAgent() {
      Object.defineProperty(navigator, 'userAgent', {   value: '{{UserAgent}}',   configurable: true });
    })();
    '''
    inject_data['vendor'] = '''
      (function fakeVendor() {
      Object.defineProperty(navigator, 'vendor', {   value: '{{vendor}}', configurable: true });
    })();     
    '''
    inject_data['MaxTouchPoints'] = '''
    (function fakeMaxTouchPoints() {
      Object.defineProperty(navigator, 'maxTouchPoints', {   value: {{MaxTouchPoints}},   configurable: true });
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
            }, configurable: true, writable: true
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
                }, configurable: true, writable: true
              });
              //
              return results_2;
            }, configurable: true, writable: true
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
            }, configurable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.constructor, "length", {
            "value": 1, configurable: true, writable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.constructor, "toString", {
            "value": () => "function getContext() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.constructor, "name", {
            "value": "getContext", configurable: true
        });
        let rawArc = CanvasRenderingContext2D.prototype.arc
        Object.defineProperty(CanvasRenderingContext2D.prototype, "arc", {
            "value": function () {
                let ctxIdx = ctxArr.indexOf(this);
                ctxInf[ctxIdx].useArc = true;
                return rawArc.apply(this, arguments);
            }, configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "length", {
            "value": 5, configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "toString", {
            "value": () => "function arc() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.arc, "name", {
            "value": "arc", configurable: true, writable: true
        });    
        const rawFillText = CanvasRenderingContext2D.prototype.fillText;
        Object.defineProperty(CanvasRenderingContext2D.prototype, "fillText", {
            "value": function () {
                let ctxIdx = ctxArr.indexOf(this);
                ctxInf[ctxIdx].useFillText = true;
                return rawFillText.apply(this, arguments);
            }, configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "length", {
            "value": 4, configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "toString", {
            "value": () => "function fillText() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.fillText, "name", {
            "value": "fillText", configurable: true, writable: true
        }); 
        //
        Object.defineProperty(HTMLCanvasElement.prototype, "toBlob", {
            "value": function () {
              noisify(this, this.getContext("2d"));
              return toBlob.apply(this, arguments);
            }, configurable: true, writable: true
        });
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "length", {
            "value": 1, configurable: true, writable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "toString", {
            "value": () => "function toBlob() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.toBlob, "name", {
            "value": "toBlob", configurable: true, writable: true
        });  
        //
        Object.defineProperty(HTMLCanvasElement.prototype, "toDataURL", {
            "value": function () {
              noisify(this, this.getContext("2d"));
              return toDataURL.apply(this, arguments);
            }, configurable: true, writable: true
        });
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "length", {
            "value": 0, configurable: true, writable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "toString", {
            "value": () => "function toDataURL() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(HTMLCanvasElement.prototype.toDataURL, "name", {
            "value": "toDataURL", configurable: true, writable: true
        });
        //
        Object.defineProperty(CanvasRenderingContext2D.prototype, "getImageData", {
            "value": function () {
              noisify(this.canvas, this);
              return getImageData.apply(this, arguments);
            }, configurable: true, writable: true
        });
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "length", {
            "value": 4, configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "toString", {
            "value": () => "function getImageData() { [native code] }", configurable: true, writable: true
        });
    
        Object.defineProperty(CanvasRenderingContext2D.prototype.getImageData, "name", {
            "value": "getImageData", configurable: true, writable: true
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
      (function fakeWebgl() {
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
                  }, configurable: true, writable: true
                });
              },
              "parameter": function (target) {
                var proto = target.prototype ? target.prototype : target.__proto__;
                const getParameter = proto.getParameter;
                Object.defineProperty(proto, "getParameter", {
                  "value": function () {
                    //window.top.postMessage("webgl-fingerprint-defender-alert", '*');
                    //
                    if (arguments[0] === 3415) return {{3412}};
                    else if (arguments[0] === 3414) return {{3412}};
                    else if (arguments[0] === 3415) return {{3412}};
                    else if (arguments[0] === 35375) return {{3412}};
                    else if (arguments[0] === 35374) return {{3412}};
                    else if (arguments[0] === 35380) return {{3412}};
                    else if (arguments[0] === 34045) return {{3412}};
                    else if (arguments[0] === 36348) return {{3412}};
                    else if (arguments[0] === 35371) return {{3412}};
                    else if (arguments[0] === 37154) return {{3412}};
                    else if (arguments[0] === 35659) return {{3412}};
                    else if (arguments[0] === 35978) return {{3412}};
                    else if (arguments[0] === 35979) return {{3412}};
                    else if (arguments[0] === 35968) return {{3412}};
                    else if (arguments[0] === 34852) return {{3412}};
                    else if (arguments[0] === 36063) return {{3412}};
                    else if (arguments[0] === 36183) return {{3412}};
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
                  }, configurable: true, writable: true
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
    (function fakeNetwork() {
        function doUpdateProp(obj, prop, newVal){
            let props = Object.getOwnPropertyDescriptor(obj, prop) || {configurable:true};

            props["value"] = newVal;
            props["configurable"] = true;
            Object.defineProperty(obj, prop, props);

            return props;
        }
        var rand = function(max){
            return Math.floor(Math.random()*max);
        };
        var randArr = function(arr){
            return arr[Math.floor(Math.random() * arr.length)];
        };

        let NetworkInformation = function(){
            this.downlink = rand(10);
            this.downlinkMax = Infinity;
            this.effectiveType = "4g"; // randArr(["4g","3g","2g"]);
            this.rtt = randArr([50,75,100,125,150]);
            this.saveData = false;
            this.type = randArr(["wifi","ethernet","other"]);

            this.onchange = null;
            this.ontypechange = null;

            this.__proto__ = NetworkInformation;
        };
        let fakeNet = new NetworkInformation();

        fakeNet.addEventListener = function(){};

        doUpdateProp(navigator,"connection", fakeNet);
        console.log('==fakeNetwork==');
    })();

    '''
    inject_data['fonts'] = '''
    
      (function fakeFonts() {
        function defineobjectproperty(val, e, c, w) {
          // Makes an object describing a property
          return {
            value: val,
            enumerable: !!e,
            configurable: !!c,
            writable: !!w
          }
        }
        
        var DEFAULT = 'auto'
        var originalStyleSetProperty = CSSStyleDeclaration.prototype.setProperty
        var originalSetAttrib = Element.prototype.setAttribute
        var originalNodeAppendChild = Node.prototype.appendChild
        var FontListToUse = {{fonts}}.map(function(x){return x.toLowerCase()});
        var baseFonts= ["default"]
        var keywords = ["inherit", "auto", "default", "!Important"]
        baseFonts.push.apply(baseFonts, FontListToUse)
        baseFonts.push.apply(baseFonts, keywords)

        function getAllowedFontFamily(family) {
          var fonts = family.replace(/"|'/g,'').split(',')
          var allowedFonts = fonts.filter(function(font) {
            if(font && font.length) {
              var normalised = font.trim().toLowerCase()
              // Allow base fonts
              for(var allowed of baseFonts)
                if(normalised == allowed) return true
              // Allow web fonts
              for (var allowed of document.fonts.values())
                if(normalised == allowed) return true
            }
          })
          return allowedFonts.map(function(f){
            var trimmed = f.trim()
            return ~trimmed.indexOf(' ') ? "'" + trimmed + "'" : trimmed
          }).join(", ")
        }
        

        function modifiedCssSetProperty(key, val) {
          if(key.toLowerCase() == 'font-family') {
            var keyresult = key.toLowerCase()
            var allowed = getAllowedFontFamily(val)
            var oldFF = this.fontFamily
            return originalStyleSetProperty.call(this, 'font-family', allowed || DEFAULT)
          }
          return originalStyleSetProperty.call(this, key, val)
        }
        
        function makeModifiedSetCssText(originalSetCssText) {
          return function modifiedSetCssText(css) {
            var fontFamilyMatch = css.match(/\b(?:font-family:([^;]+)(?:;|$))/i)
            if(fontFamilyMatch && fontFamilyMatch.length == 1) {
              css = css.replace(/\b(font-family:[^;]+(;|$))/i, '').trim()
              var allowed = getAllowedFontFamily(fontFamilyMatch[1]) || DEFAULT
              if(css.length && css[css.length - 1] != ';')
                css += ';'
              css += "font-family: " + allowed + ";"
            }
            return originalSetCssText.call(this, css)
          }
        }
        
        var modifiedSetAttribute = (function() {
          var innerModify = makeModifiedSetCssText(function (val) {
            return originalSetAttrib.call(this, 'style', val)
          })
          return function modifiedSetAttribute(key, val) {
            if(key.toLowerCase() == 'style') {
              return innerModify.call(this, val)
            }
            return originalSetAttrib.call(this, key, val)
          }
        })();
        
        function makeModifiedInnerHTML(originalInnerHTML) {
          return function modifiedInnerHTML(html) {
            var retval = originalInnerHTML.call(this, html)
            recursivelyModifyFonts(this.parentNode)
            return retval
          }
        }
        
        function recursivelyModifyFonts(elem) {
          if(elem) {
            if(elem.style && elem.style.fontFamily) {
              modifiedCssSetProperty.call(elem.style, 'font-family', elem.style.fontFamily) // Uses the special setter
            }
            if(elem.childNodes)
              elem.childNodes.forEach(recursivelyModifyFonts)
          }
          return elem
        }

        function modifiedAppend(child) {
          child = recursivelyModifyFonts(child)
          return originalNodeAppendChild.call(this, child)
        }
        
          
        var success = true
        
        function overrideFunc(obj, name, f) {
          try {
            Object.defineProperty(obj.prototype, name, defineobjectproperty(f, true))
          } catch(e) {success=false;}
        }
        
        
        function overrideSetter(obj, name, makeSetter) {
          try {
            var current = Object.getOwnPropertyDescriptor(obj.prototype, name)
            current.set = makeSetter(current.set)
            current.configurable = false
            Object.defineProperty(obj.prototype, name, current)
          } catch(e) {success=false;}
        }
        
        overrideFunc(Node, 'appendChild', modifiedAppend)
        overrideFunc(CSSStyleDeclaration, 'setProperty', modifiedCssSetProperty)
        overrideFunc(Element, 'setAttribute', modifiedSetAttribute)
        
        
        
        try {
          Object.defineProperty(CSSStyleDeclaration.prototype, "fontFamily", {
            set: function fontFamily(f) {
              modifiedCssSetProperty.call(this, 'font-family', f)
            },
            get: function fontFamily() {
              return this.getPropertyValue('font-family')
            }
          })
        } catch(e) {success=false;}
        
        overrideSetter(CSSStyleDeclaration,'cssText', makeModifiedSetCssText)
        overrideSetter(Element,'innerHTML', makeModifiedInnerHTML)
        overrideSetter(Element,'outerHTML', makeModifiedInnerHTML)
        console.log('==fakeFonts=='); 
      })();
    '''
    inject_data['rects'] = '''
    (function fakeRects() {
        function doUpdateProp(obj, prop, newVal){
            let props = Object.getOwnPropertyDescriptor(obj, prop) || {configurable:true};
            props["value"] = newVal;
            props["configurable"] = true;
            Object.defineProperty(obj, prop, props);

            return props;
        }

        // Generate offset
        let off = {{rects}};
        console.log('=====off',off)
        function updatedRect(old,round,overwrite){
            function genOffset(round,val){
                return val + (round ? Math.round(off) : off);
            }
            let temp = overwrite === true ? old : new DOMRect();

            temp.top 	= genOffset(round,old.top);
            temp.right	= genOffset(round,old.right);
            temp.bottom = genOffset(round,old.bottom);
            temp.left 	= genOffset(round,old.left);
            temp.width 	= genOffset(round,old.width);
            temp.height = genOffset(round,old.height);
            temp.x 		= genOffset(round,old.x);
            temp.y 		= genOffset(round,old.y);

            return temp;
        }

        function getClientRectsProtection(el){
            if (window.location.host === "docs.google.com") return;

            let clientRects = self[el].prototype.getClientRects;
            let boundingRects = self[el].prototype.getBoundingClientRect;
            
            doUpdateProp(self[el].prototype,"getClientRects",function(){
                let rects = clientRects.apply(this,arguments);
                console.log('==getClientRects==', rects)
                if (this === undefined || this === null) return rects;
                let krect = Object.keys(rects);

                let DOMRectList = function(){};
                let list = new DOMRectList();
                list.length = krect.length;
                for (let i = 0;i<list.length;i++){
                    if (krect[i] === "length") continue;
                    list[i] = updatedRect(rects[krect[i]],false,false);
                }
                return list;
            });

            
            doUpdateProp(self[el].prototype,"getBoundingClientRect",function(){
                let rect = boundingRects.apply(this,arguments);
                if (this === undefined || this === null) return rect;

                //window.top.postMessage("trace-protection::ran::clientrectsbounding::" + el + "get", '*');

                return updatedRect(rect,true,true);
            });
            
            doUpdateProp(self[el].prototype.getClientRects, "toString",function(){
                //window.top.postMessage("trace-protection::ran::clientrects::" + el + "getstring", '*');
                return "getClientRects() { [native code] }";
            });
            console.log('==getClientRectsProtection==')
            doUpdateProp(self[el].prototype.getBoundingClientRect, "toString",function(){

                return "getBoundingClientRect() { [native code] }";
            });
            
            
            console.log('==getBoundingClientRectsProtection==')
        }

        ["Element","Range"].forEach(function(el){
            // Check for broken frames
            if (el === undefined) return;

            // getClientRects
            getClientRectsProtection(el);

            // getBoundingClientRect
            //getBoundingClientRectsProtection(el);
        });
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
    inject_data['battery'] = '''
      (function fakeBattery() {
        // Random 2 dp value
        let setting_level = Math.floor(Math.random()*100)/100;

        function doUpdateProp(obj, prop, newVal){
            let props = Object.getOwnPropertyDescriptor(obj, prop) || {configurable:true};

            props["value"] = newVal;
            props["configurable"] = true;
            Object.defineProperty(obj, prop, props);

            return props;
        }



        let BatteryPromise = new Promise(function(resolve, reject){
            let BatteryManager = function(){
                this.charging = true;
                this.chargingTime = Infinity;
                this.dischargingTime = Infinity;
                this.level = setting_level;

                this.onchargingchange = null;
                this.onchargingtimechange = null;
                this.ondischargingtimechange = null;
                this.onlevelchange = null;

                //window.top.postMessage("trace-protection::ran::battery::main", '*');
            };

            resolve(new BatteryManager())
        });

        doUpdateProp(navigator,"getBattery",function() {
            return BatteryPromise;
        });
        doUpdateProp(navigator.getBattery,"toString","function getBattery() { [native code] }");
      })();

    '''
    inject_data['ping'] = '''
      (function fakePing() {
        if (!navigator || !navigator.sendBeacon){
          return;
        }
        function doUpdateProp(obj, prop, newVal){
          let props = Object.getOwnPropertyDescriptor(obj, prop) || {configurable:true};

          if (!props["configurable"]) {
            //console.warn("Issue with property not being able to be configured.");
            return;
          }

          props["value"] = newVal;
          Object.defineProperty(obj, prop, props);
          return props;
        }

        doUpdateProp(navigator,"sendBeacon",function() {
          //window.top.postMessage("trace-protection::ran::sendbeacon::main", '*');
          return true;
        });
        doUpdateProp(navigator.sendBeacon,"toString","function sendBeacon() { [native code] }");
    })();    



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
    pks = KeysSearch.objects.values_list('pk', flat=True)
    # KeysSearch.objects.filter()
    random_pk = choice(pks)
    random_obj = KeysSearch.objects.get(pk=random_pk)
    return successResponse({'data': random_obj.value})
  
@api_view(['GET', 'POST', 'PUT'])
@signature_test()
def check_version_for_update(request):
    obj_last = MunAnti.objects.last()
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
def update_munproxies_by_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)

    mun_proxies_objs = MunProxies.objects.filter(pk=update_post['id'], owner=request.user)
    if mun_proxies_objs.exists():
      mun_proxies_objs.update(**update_post['update_data'])
      mun_proxies_obj = MunProxies.objects.get(
          pk=update_post['id'], owner=request.user)
      munproxies_data = MunProxiesSerializer(mun_proxies_obj)
    return successResponse({'data':munproxies_data.data})


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_mun_proxies(request):
  
    munproxies_playload = json.loads(request.body)
    "'socks_port', 'control_port','bridges_string','rotating_time', 'country_code', 'country_name'"
    socks_port = munproxies_playload['socks_port']
    control_port = munproxies_playload['control_port']  
    bridges_string = munproxies_playload['bridges_string']
    rotating_time = munproxies_playload['rotating_time']
    country_code = munproxies_playload['country_code']

    munproxies_obj, created = MunProxies.objects.get_or_create(socks_port=socks_port, owner=request.user)
    munproxies_obj.control_port = control_port
    munproxies_obj.bridges_string = bridges_string
    munproxies_obj.rotating_time = rotating_time
    munproxies_obj.country_code = country_code
    
    munproxies_obj.save()
    munproxies_obj.refresh_from_db()
    data_serializer = MunProxiesSerializer(munproxies_obj, many=False)
    
    return successResponse({'data':data_serializer.data}) 

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def remove_mun_proxies(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    if remove_post['list_id'] == 'all':
        mun_proxies_objs = MunProxies.objects.filter(profile_owner=request.user)
    else:
        mun_proxies_objs = MunProxies.objects.filter(pk__in=remove_post['list_id'], profile_owner=request.user)

    mun_proxies_objs.delete()
    return successResponse()


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_profile_by_id(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)
    if update_post['id'].find('\n') !=-1:
      id_update = update_post['id'].split('\n')[0].strip()
    else:
      id_update = update_post['id']
    browser_profiles = BrowserProfiles.objects.filter(pk=id_update, profile_owner=request.user)
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
      account_obj = accounts_objs.first()
      for key, value in update_post['update_data'].items():
          setattr(account_obj, key, value)
      account_obj.save()
      
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
def remove_emails(request):
    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    remove_post = json.loads(request.body)
    from django.db.models import Q
    if remove_post['list_id'] == 'all':
        list_objects = AccountsEmails.objects.filter(
            Q(owner=request.user) | Q(created_by=request.user))
    else:
        print('remove_post==', remove_post['list_id'])
        list_objects = AccountsEmails.objects.filter(Q(owner=request.user) | Q(created_by=request.user), pk__in=remove_post['list_id'])
        
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
    listFonts = ['Arial', 'Calibri', 'Cambria', 'Cambria Math', 'Candara', 'Comic Sans MS', 'Comic Sans MS Bold', 'Comic Sans', 'Consolas', 'Constantia', 'Corbel', 'Courier New', 'Caurier Regular', 'Ebrima', 'Fixedsys Regular', 'Franklin Gothic', 'Gabriola Regular', 'Gadugi', 'Georgia', 'HoloLens MDL2 Assets Regular', 'Impact Regular', 'Javanese Text Regular', 'Leelawadee UI', 'Lucida Console Regular', 'Lucida Sans Unicode Regular', 'Malgun Gothic', 'Microsoft Himalaya Regular', 'Microsoft JhengHei', 'Microsoft JhengHei UI', 'Microsoft PhangsPa', 'Microsoft Sans Serif Regular', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft YaHei UI', 'Microsoft Yi Baiti Regular', 'MingLiU_HKSCS-ExtB Regular', 'MingLiu-ExtB Regular', 'Modern Regular', 'Mongolia Baiti Regular', 'MS Gothic Regular', 'MS PGothic Regular', 'MS Sans Serif Regular', 'MS Serif Regular', 'MS UI Gothic Regular', 'MV Boli Regular', 'Myanmar Text', 'Nimarla UI', 'Myanmar Tet', 'Nirmala UI', 'NSimSun Regular', 'Palatino Linotype', 'PMingLiU-ExtB Regular', 'Roman Regular', 'Script Regular', 'Segoe MDL2 Assets Regular', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Emoji Regular', 'Segoe UI Historic Regular', 'Segoe UI Symbol Regular', 'SimSun Regular', 'SimSun-ExtB Regular', 'Sitka Banner', 'Sitka Display', 'Sitka Heading', 'Sitka Small', 'Sitka Subheading', 'Sitka Text', 'Small Fonts Regular', 'Sylfaen Regular', 'Symbol Regular', 'System Bold', 'Tahoma', 'Terminal', 'Times New Roman', 'Trebuchet MS', 'Verdana', 'Webdings Regular', 'Wingdings Regular', 'Yu Gothic', 'Yu Gothic UI', 'Arial Black', 'Calibri Light', 'Courier', 'Fixedsys', 'Franklin Gothic Medium', 'Gabriola', 'HoloLens MDL2 Assets', 'Impact', 'Javanese Text', 'Leelawadee UI Semilight', 'Lucida Console', 'Lucida Sans Unicode', 'MS Gothic', 'MS PGothic', 'MS Sans Serif', 'MS Serif', 'MS UI Gothic', 'MV Boli', 'Malgun Gothic Semilight', 'Marlett', 'Microsoft Himalaya', 'Microsoft JhengHei Light', 'Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft YaHei Light', 'Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', 'MingLiU_HKSCS-ExtB', 'Modern', 'Mongolian Baiti', 'NSimSun', 'Nirmala UI Semilight', 'PMingLiU-ExtB', 'Roman', 'Script', 'Segoe MDL2 Assets', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'SimSun', 'SimSun-ExtB', 'Small Fonts', 'Sylfaen', 'Symbol', 'System', 'Webdings', 'Wingdings', 'Yu Gothic Light', 'Yu Gothic Medium', 'Yu Gothic UI Light', 'Yu Gothic UI Semibold', 'Yu Gothic UI Semilight', 'Arial Narrow', 'Arial Unicode MS', 'Book Antiqua', 'Bookman Old Style', 'Century', 'Century Gothic', 'Century Schoolbook', 'Garamond', 'Helvetica', 'Lucida Bright', 'Lucida Calligraphy', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Monotype Corsiva', 'MS Outlook', 'MS Reference Sans Serif', 'Times', 'Wingdings 2', 'Wingdings 3', 'default', 'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'inherit', 'auto', 'Brush Script MT', 'Broadway', 'Bell MT', 'Berlin Sans FB', 'Blackadder ITC', 'Curlz MT', 'Elephant', 'Engravers MT', 'Goudy Old Style', 'Minion Pro', 'Papyrus', 'Wide Latin', 'Snap ITC', 'Stencil', 'Old English Text MT', 'Ubuntu', 'Ubuntu Mono', 'Terminus Font', 'Terminus', 'Ubuntu Mono 13', 'Ubuntu Mono Regular', 'Apple Braille Outline 6 Dot', 'Apple Braille Outline 8 Dot', 'Apple Braille Pinpoint 6 Dot', 'Apple Braille Pinpoint 8 Dot', 'Apple Braille', 'Apple Symbols', 'AppleGothic', 'AquaKana', 'Geeza Pro Bold', 'Geeza Pro', 'Geneva', 'HelveLTMM', 'Helvetica LT MM', 'HelveticaNeue', 'Hiragino Kaku Gothic ProN W3', 'Hiragino Kaku Gothic ProN W6', 'Hiragino Mincho ProN W3', 'Hiragino Mincho ProN W6', 'Keyboard', 'LastResort', 'LiHei Pro', 'LucidaGrande', 'Menlo', 'Monaco', 'STHeiti', 'STHeiti Light', 'STXihei', 'Thonburi', 'ThonburiBold', 'Times LT MM', 'TimesLTMM', 'ZapfDingbats', 'AmericanTypewriter', 'Andale Mono', 'Apple Chancery', 'Apple LiGothic Medium', 'Arial Bold Italic', 'Arial Bold', 'Arial Italic', 'Arial Narrow Bold Italic', 'Arial Narrow Bold', 'Arial Narrow Italic', 'Arial Rounded Bold', 'Arial Unicode', 'Baskerville', 'BigCaslon', 'Brush Script', 'Chalkboard', 'Chalkduster', 'Cochin', 'Copperplate', 'Courier New Bold Italic', 'Courier New Bold', 'Courier New Italic', 'Didot', 'Futura', 'Georgia Bold Italic', 'Georgia Bold', 'Georgia Italic', 'GillSans', 'Hei', 'Herculanum', 'Hiragino Kaku Gothic Pro W3', 'Hiragino Kaku Gothic Pro W6', 'Hiragino Kaku Gothic Std W8', 'Hiragino Kaku Gothic StdN W8', 'Hiragino Maru Gothic Pro W4', 'Hiragino Maru Gothic ProN W4', 'Hiragino Mincho Pro W3', 'Hiragino Mincho Pro W6', 'Hoefler Text', 'Hoefler Text Ornaments', 'Kai', 'MarkerFelt', 'Optima', 'Osaka', 'OsakaMono', 'Skia', 'Tahoma Bold', 'Times New Roman Bold Italic', 'Times New Roman Bold', 'Times New Roman Italic', 'Trebuchet MS Bold Italic', 'Trebuchet MS Bold', 'Trebuchet MS Italic', 'Verdana Bold Italic', 'Verdana Bold', 'Verdana Italic', 'Zapfino', 'Aharoni Bold', 'Andalus Regular', 'Angsana New', 'Angsana New Bold', 'Angsana New Italic', 'Angsana New Bold Italic', 'AngsanaUPC', 'AngsanaUPC Bold', 'AngsanaUPC Italic', 'AngsanaUPC Bold Italic', 'Aparajita', 'Aparajita Bold', 'Aparajita Italic', 'Aparajita Bold Italic', 'Arabic Typesetting Regular', 'Arial Unicode MS Regular', 'Batang', 'BatangChe', 'Browallia New', 'Browallia New Bold', 'Browallia New Italic', 'Browallia New Bold Italic', 'BrowalliaUPC', 'BrowalliaUPC Bold', 'BrowalliaUPC Italic', 'BrowalliaUPC Bold Italic', 'Calibri Bold', 'Calibri Italic', 'Calibri Bold Italic', 'Cambria Bold', 'Cambria Italic', 'Cambria Bold Italic', 'Candara Bold', 'Candara Italic', 'Candara Bold Italic', 'Consolas Bold', 'Consolas Italic', 'Consolas Bold Italic', 'Constantia Bold', 'Constantia Italic', 'Constantia Bold Italic', 'Corbel Bold', 'Corbel Italic', 'Corbel Bold Italic', 'Cordia New', 'Cordia New Bold', 'Cordia New Italic', 'Cordia New Bold Italic', 'CordiaUPC', 'CordiaUPC Bold', 'CordiaUPC Italic', 'CordiaUPC Bold Italic', 'DFKai-SB', 'DaunPenh', 'David', 'David Bold', 'DilleniaUPC', 'DilleniaUPC Bold', 'DilleniaUPC Italic', 'DilleniaUPC Bold Italic', 'DokChampa', 'Dotum', 'DotumChe', 'Ebrima Bold', 'Estrangelo Edessa', 'EucrosiaUPC', 'EucrosiaUPC Bold', 'EucrosiaUPC Italic', 'EucrosiaUPC Bold Italic', 'Euphemia', 'FangSong', 'FrankRuehl', 'Franklin Gothic Medium Italic', 'FreesiaUPC', 'FreesiaUPC Bold', 'FreesiaUPC Italic', 'FreesiaUPC Bold Italic', 'Gautami', 'Gautami Bold', '& Georgia Bold Italic', 'Gisha', 'Gisha Bold', 'Gulim', 'GulimChe', 'Gungsuh', 'GungsuhChe', 'IrisUPC', 'IrisUPC Bold', 'IrisUPC Italic', 'IrisUPC Bold Italic', 'Iskoola Pota', 'IskoolaPota Bold', 'JasmineUPC', 'JasmineUPC Bold', 'JasmineUPC Italic', 'JasmineUPC Bold Italic', 'KaiTi', 'Kalinga', 'Kalinga Bold', 'Kartika', 'Kartika Bold', 'Khmer UI', 'Khmer UI Bold', 'KodchiangUPC', 'KodchiangUPC Bold', 'KodchiangUPC Italic', 'KodchiangUPC Bold Italic', 'Kokila', 'Kokila Bold', 'Kokila Italic', 'Kokila Bold Italic', 'Lao UI', 'Lao UI Bold', 'Latha', 'Latha Bold', 'Leelawadee', 'Leelawadee Bold', 'Levenim MT', 'Levenim MT Bold', 'LilyUPC', 'LilyUPC Bold', 'LilyUPC Italic', 'LilyUPC Bold Italic', 'MS Mincho', 'MS PMincho', 'Malgun Gothic Bold', 'Mangal', 'Mangal Bold', 'Meiryo UI', 'Meiryo UI Bold', 'Meiryo UI Italic', 'Meiryo UI Bold Italic', 'Meiryo', 'Meiryo Bold', 'Meiryo Italic', 'Meiryo Bold Italic', 'Microsoft JhengHei Bold', 'Microsoft New Tai Lue Bold', 'Microsoft PhagsPa Bold', 'Microsoft Tai Le Bold', 'Microsoft Uighur', 'Microsoft YaHei Bold', 'MingLiU', 'MingLiU_HKSCS', 'Miriam', 'Miriam Fixed', 'MoolBoran', 'Narkisim', 'Nyala', 'PMingLiU', 'Palatino Linotype Bold', 'Palatino Linotype Italic', 'Palatino Linotype Bold Italic', 'Plantagenet Cherokee', 'Raavi', 'Raavi Bold', 'Rod', 'Sakkal Majalla', 'Sakkal Majalla Bold', 'Segoe Print Bold', 'Segoe Script Bold', 'Segoe UI Bold', 'Segoe UI Italic', 'Segoe UI Bold Italic', 'Shonar Bangla', 'Shonar Bangla Bold', 'Shruti', 'Shruti Bold', 'SimHei', 'Simplified Arabic', 'Simplified Arabic Bold', 'Simplified Arabic Fixed', ' Times New Roman Bold', 'Traditional Arabic', 'Traditional Arabic Bold', 'Tunga', 'Tunga Bold', 'Utsaah', 'Utsaah Bold', 'Utsaah Italic', 'Utsaah Bold Italic', 'Vani', 'Vani Bold', 'Vijaya', 'Vijaya Bold', 'Vrinda', 'Vrinda Bold']
    fonts_max = random.randint(200, len(listFonts)-1)
    fonts_min = random.randint(0, 150)
    listUse = listFonts[fonts_min:fonts_max]  
    profile_dict['profile_rects'] = str(round(random.uniform(0.2, 0.35), 5))
    profile_dict['profile_font'] = str(listUse)
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
        profile_dict['profile_proxy_type'] = 2
    if profile_post['profile_rects'] == 'Noise':
        profile_dict['profile_rects'] = str(round(random.uniform(0.2, 0.35), 5))
    #fonts
    if profile_post['profile_font'] == 'Noise':
      
        listFonts = ['Arial', 'Calibri', 'Cambria', 'Cambria Math', 'Candara', 'Comic Sans MS', 'Comic Sans MS Bold', 'Comic Sans', 'Consolas', 'Constantia', 'Corbel', 'Courier New', 'Caurier Regular', 'Ebrima', 'Fixedsys Regular', 'Franklin Gothic', 'Gabriola Regular', 'Gadugi', 'Georgia', 'HoloLens MDL2 Assets Regular', 'Impact Regular', 'Javanese Text Regular', 'Leelawadee UI', 'Lucida Console Regular', 'Lucida Sans Unicode Regular', 'Malgun Gothic', 'Microsoft Himalaya Regular', 'Microsoft JhengHei', 'Microsoft JhengHei UI', 'Microsoft PhangsPa', 'Microsoft Sans Serif Regular', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft YaHei UI', 'Microsoft Yi Baiti Regular', 'MingLiU_HKSCS-ExtB Regular', 'MingLiu-ExtB Regular', 'Modern Regular', 'Mongolia Baiti Regular', 'MS Gothic Regular', 'MS PGothic Regular', 'MS Sans Serif Regular', 'MS Serif Regular', 'MS UI Gothic Regular', 'MV Boli Regular', 'Myanmar Text', 'Nimarla UI', 'Myanmar Tet', 'Nirmala UI', 'NSimSun Regular', 'Palatino Linotype', 'PMingLiU-ExtB Regular', 'Roman Regular', 'Script Regular', 'Segoe MDL2 Assets Regular', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Emoji Regular', 'Segoe UI Historic Regular', 'Segoe UI Symbol Regular', 'SimSun Regular', 'SimSun-ExtB Regular', 'Sitka Banner', 'Sitka Display', 'Sitka Heading', 'Sitka Small', 'Sitka Subheading', 'Sitka Text', 'Small Fonts Regular', 'Sylfaen Regular', 'Symbol Regular', 'System Bold', 'Tahoma', 'Terminal', 'Times New Roman', 'Trebuchet MS', 'Verdana', 'Webdings Regular', 'Wingdings Regular', 'Yu Gothic', 'Yu Gothic UI', 'Arial Black', 'Calibri Light', 'Courier', 'Fixedsys', 'Franklin Gothic Medium', 'Gabriola', 'HoloLens MDL2 Assets', 'Impact', 'Javanese Text', 'Leelawadee UI Semilight', 'Lucida Console', 'Lucida Sans Unicode', 'MS Gothic', 'MS PGothic', 'MS Sans Serif', 'MS Serif', 'MS UI Gothic', 'MV Boli', 'Malgun Gothic Semilight', 'Marlett', 'Microsoft Himalaya', 'Microsoft JhengHei Light', 'Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft YaHei Light', 'Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', 'MingLiU_HKSCS-ExtB', 'Modern', 'Mongolian Baiti', 'NSimSun', 'Nirmala UI Semilight', 'PMingLiU-ExtB', 'Roman', 'Script', 'Segoe MDL2 Assets', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'SimSun', 'SimSun-ExtB', 'Small Fonts', 'Sylfaen', 'Symbol', 'System', 'Webdings', 'Wingdings', 'Yu Gothic Light', 'Yu Gothic Medium', 'Yu Gothic UI Light', 'Yu Gothic UI Semibold', 'Yu Gothic UI Semilight', 'Arial Narrow', 'Arial Unicode MS', 'Book Antiqua', 'Bookman Old Style', 'Century', 'Century Gothic', 'Century Schoolbook', 'Garamond', 'Helvetica', 'Lucida Bright', 'Lucida Calligraphy', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Monotype Corsiva', 'MS Outlook', 'MS Reference Sans Serif', 'Times', 'Wingdings 2', 'Wingdings 3', 'default', 'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'inherit', 'auto', 'Brush Script MT', 'Broadway', 'Bell MT', 'Berlin Sans FB', 'Blackadder ITC', 'Curlz MT', 'Elephant', 'Engravers MT', 'Goudy Old Style', 'Minion Pro', 'Papyrus', 'Wide Latin', 'Snap ITC', 'Stencil', 'Old English Text MT', 'Ubuntu', 'Ubuntu Mono', 'Terminus Font', 'Terminus', 'Ubuntu Mono 13', 'Ubuntu Mono Regular', 'Apple Braille Outline 6 Dot', 'Apple Braille Outline 8 Dot', 'Apple Braille Pinpoint 6 Dot', 'Apple Braille Pinpoint 8 Dot', 'Apple Braille', 'Apple Symbols', 'AppleGothic', 'AquaKana', 'Geeza Pro Bold', 'Geeza Pro', 'Geneva', 'HelveLTMM', 'Helvetica LT MM', 'HelveticaNeue', 'Hiragino Kaku Gothic ProN W3', 'Hiragino Kaku Gothic ProN W6', 'Hiragino Mincho ProN W3', 'Hiragino Mincho ProN W6', 'Keyboard', 'LastResort', 'LiHei Pro', 'LucidaGrande', 'Menlo', 'Monaco', 'STHeiti', 'STHeiti Light', 'STXihei', 'Thonburi', 'ThonburiBold', 'Times LT MM', 'TimesLTMM', 'ZapfDingbats', 'AmericanTypewriter', 'Andale Mono', 'Apple Chancery', 'Apple LiGothic Medium', 'Arial Bold Italic', 'Arial Bold', 'Arial Italic', 'Arial Narrow Bold Italic', 'Arial Narrow Bold', 'Arial Narrow Italic', 'Arial Rounded Bold', 'Arial Unicode', 'Baskerville', 'BigCaslon', 'Brush Script', 'Chalkboard', 'Chalkduster', 'Cochin', 'Copperplate', 'Courier New Bold Italic', 'Courier New Bold', 'Courier New Italic', 'Didot', 'Futura', 'Georgia Bold Italic', 'Georgia Bold', 'Georgia Italic', 'GillSans', 'Hei', 'Herculanum', 'Hiragino Kaku Gothic Pro W3', 'Hiragino Kaku Gothic Pro W6', 'Hiragino Kaku Gothic Std W8', 'Hiragino Kaku Gothic StdN W8', 'Hiragino Maru Gothic Pro W4', 'Hiragino Maru Gothic ProN W4', 'Hiragino Mincho Pro W3', 'Hiragino Mincho Pro W6', 'Hoefler Text', 'Hoefler Text Ornaments', 'Kai', 'MarkerFelt', 'Optima', 'Osaka', 'OsakaMono', 'Skia', 'Tahoma Bold', 'Times New Roman Bold Italic', 'Times New Roman Bold', 'Times New Roman Italic', 'Trebuchet MS Bold Italic', 'Trebuchet MS Bold', 'Trebuchet MS Italic', 'Verdana Bold Italic', 'Verdana Bold', 'Verdana Italic', 'Zapfino', 'Aharoni Bold', 'Andalus Regular', 'Angsana New', 'Angsana New Bold', 'Angsana New Italic', 'Angsana New Bold Italic', 'AngsanaUPC', 'AngsanaUPC Bold', 'AngsanaUPC Italic', 'AngsanaUPC Bold Italic', 'Aparajita', 'Aparajita Bold', 'Aparajita Italic', 'Aparajita Bold Italic', 'Arabic Typesetting Regular', 'Arial Unicode MS Regular', 'Batang', 'BatangChe', 'Browallia New', 'Browallia New Bold', 'Browallia New Italic', 'Browallia New Bold Italic', 'BrowalliaUPC', 'BrowalliaUPC Bold', 'BrowalliaUPC Italic', 'BrowalliaUPC Bold Italic', 'Calibri Bold', 'Calibri Italic', 'Calibri Bold Italic', 'Cambria Bold', 'Cambria Italic', 'Cambria Bold Italic', 'Candara Bold', 'Candara Italic', 'Candara Bold Italic', 'Consolas Bold', 'Consolas Italic', 'Consolas Bold Italic', 'Constantia Bold', 'Constantia Italic', 'Constantia Bold Italic', 'Corbel Bold', 'Corbel Italic', 'Corbel Bold Italic', 'Cordia New', 'Cordia New Bold', 'Cordia New Italic', 'Cordia New Bold Italic', 'CordiaUPC', 'CordiaUPC Bold', 'CordiaUPC Italic', 'CordiaUPC Bold Italic', 'DFKai-SB', 'DaunPenh', 'David', 'David Bold', 'DilleniaUPC', 'DilleniaUPC Bold', 'DilleniaUPC Italic', 'DilleniaUPC Bold Italic', 'DokChampa', 'Dotum', 'DotumChe', 'Ebrima Bold', 'Estrangelo Edessa', 'EucrosiaUPC', 'EucrosiaUPC Bold', 'EucrosiaUPC Italic', 'EucrosiaUPC Bold Italic', 'Euphemia', 'FangSong', 'FrankRuehl', 'Franklin Gothic Medium Italic', 'FreesiaUPC', 'FreesiaUPC Bold', 'FreesiaUPC Italic', 'FreesiaUPC Bold Italic', 'Gautami', 'Gautami Bold', '& Georgia Bold Italic', 'Gisha', 'Gisha Bold', 'Gulim', 'GulimChe', 'Gungsuh', 'GungsuhChe', 'IrisUPC', 'IrisUPC Bold', 'IrisUPC Italic', 'IrisUPC Bold Italic', 'Iskoola Pota', 'IskoolaPota Bold', 'JasmineUPC', 'JasmineUPC Bold', 'JasmineUPC Italic', 'JasmineUPC Bold Italic', 'KaiTi', 'Kalinga', 'Kalinga Bold', 'Kartika', 'Kartika Bold', 'Khmer UI', 'Khmer UI Bold', 'KodchiangUPC', 'KodchiangUPC Bold', 'KodchiangUPC Italic', 'KodchiangUPC Bold Italic', 'Kokila', 'Kokila Bold', 'Kokila Italic', 'Kokila Bold Italic', 'Lao UI', 'Lao UI Bold', 'Latha', 'Latha Bold', 'Leelawadee', 'Leelawadee Bold', 'Levenim MT', 'Levenim MT Bold', 'LilyUPC', 'LilyUPC Bold', 'LilyUPC Italic', 'LilyUPC Bold Italic', 'MS Mincho', 'MS PMincho', 'Malgun Gothic Bold', 'Mangal', 'Mangal Bold', 'Meiryo UI', 'Meiryo UI Bold', 'Meiryo UI Italic', 'Meiryo UI Bold Italic', 'Meiryo', 'Meiryo Bold', 'Meiryo Italic', 'Meiryo Bold Italic', 'Microsoft JhengHei Bold', 'Microsoft New Tai Lue Bold', 'Microsoft PhagsPa Bold', 'Microsoft Tai Le Bold', 'Microsoft Uighur', 'Microsoft YaHei Bold', 'MingLiU', 'MingLiU_HKSCS', 'Miriam', 'Miriam Fixed', 'MoolBoran', 'Narkisim', 'Nyala', 'PMingLiU', 'Palatino Linotype Bold', 'Palatino Linotype Italic', 'Palatino Linotype Bold Italic', 'Plantagenet Cherokee', 'Raavi', 'Raavi Bold', 'Rod', 'Sakkal Majalla', 'Sakkal Majalla Bold', 'Segoe Print Bold', 'Segoe Script Bold', 'Segoe UI Bold', 'Segoe UI Italic', 'Segoe UI Bold Italic', 'Shonar Bangla', 'Shonar Bangla Bold', 'Shruti', 'Shruti Bold', 'SimHei', 'Simplified Arabic', 'Simplified Arabic Bold', 'Simplified Arabic Fixed', ' Times New Roman Bold', 'Traditional Arabic', 'Traditional Arabic Bold', 'Tunga', 'Tunga Bold', 'Utsaah', 'Utsaah Bold', 'Utsaah Italic', 'Utsaah Bold Italic', 'Vani', 'Vani Bold', 'Vijaya', 'Vijaya Bold', 'Vrinda', 'Vrinda Bold']
        fonts_max = random.randint(200, len(listFonts)-1)
        fonts_min = random.randint(0, 150)
        listUse = listFonts[fonts_min:fonts_max]  
        profile_dict['profile_font'] = str(listUse)
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

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_check_function(request):

    list_objects = UserCheckFunction.objects.filter(
            user=request.user)
    
    profile_data = UserCheckFunctionSerializer(list_objects, many=True)
    
    return successResponse({'data':profile_data.data}) 
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_create_function(request):

    list_objects = UserCreateFunction.objects.filter(
            user=request.user)
    
    profile_data = UserCreateFunctionSerializer(list_objects, many=True)
    
    return successResponse({'data':profile_data.data})   

# @api_view(['GET', 'POST', 'PUT'])
# @login_required_ajax()
# @signature_test()
# @user_passes_test(banned_check)
# def get_files_map(request):

#     files_map = {}
#     files_map['chrome'] = {'version':'107.0.5304.88'}
#     files_map['ffmpeg'] = ''
#     files_map['ffplay'] = ''
#     files_map['ffprobe'] = ''
#     files_map['MunProxies'] = ''
    
#     return successResponse({'data':profile_data.data})     
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)  
def get_tool_setting(request):
    hwid_status = False
    check_data = []
    create_data = []  
    action = request.GET.get('action')
    if action == 'hwid':
        hwid = request.GET.get('hwid')
        hwid_objs = UserHwid.objects.filter(user=request.user)
        # Check if matching HWID exists AND is active (status=0)
        hwid_obj_check = hwid_objs.filter(value=hwid, status=0)
        if hwid_obj_check.exists() or not hwid_objs.exists():
            # First-time login: auto-register HWID (if not existing at all)
            if not hwid_objs.exists():
                hwid_obj, created = UserHwid.objects.get_or_create(value=hwid, user=request.user, defaults={'status': 0})
            else:
                hwid_obj = hwid_obj_check.first()
            
            # Update last_poll
            hwid_obj.last_poll = timezone.now()
            hwid_obj.save(update_fields=['last_poll'])
            
            # Load tool functions for valid/new machine
            list_objects = UserCreateFunction.objects.filter(user=request.user)
            create_data = list(UserCreateFunctionSerializer(list_objects, many=True).data) if list_objects.exists() else []
            check_objects = UserCheckFunction.objects.filter(user=request.user)
            check_data = list(UserCheckFunctionSerializer(check_objects, many=True).data) if check_objects.exists() else []
            hwid_status = True

    return successResponse({'hwid': hwid_status, 'create_data': create_data, 'check_data': check_data})

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
@transaction.atomic
def get_checker_task(request):
    checker_id = request.GET.get('id')
    with transaction.atomic():
        if request.user.is_staff:
            if checker_id:
                list_objects = CheckerTask.objects.select_for_update().filter(pk=checker_id)
            else:
                list_objects = CheckerTask.objects.select_for_update().filter(status=LinkStatus.working, owner__isnull=False, status_message_id__isnull=False)
        else:
            if checker_id:
                list_objects = CheckerTask.objects.select_for_update().filter(pk=checker_id, owner=request.user)
            else:
                list_objects = CheckerTask.objects.select_for_update().filter(status=LinkStatus.working, owner__isnull=False, status_message_id__isnull=False, owner=request.user)        
        if list_objects.exists():
            checkerObj = list_objects.first()
            profile_data = CheckerTaskSerializer(checkerObj, many=False)
            user = checkerObj.owner
            checkerObj.status = LinkStatus.suspended
            checkerObj.save()
            userTelegram_objs = UserTelegram.objects.filter(user=user)
            user_telegram = userTelegram_objs.first()
            currency_obj, created = AccountCurrency.objects.get_or_create(code='USD', label='USD')
            account_balance_obj, created = AccountBalance.objects.get_or_create(user=user,balance_type=BalanceType.credit,currency=currency_obj)
            current_banlance = UserController.calculateUserBlance(account_balance_obj)
            
            return successResponse({'data':profile_data.data, 'user':{'current_banlance': current_banlance,'username':user.username, 'telegram_id': user_telegram.telegram_id}})  
        else:
            return successResponse({'data':[]})  

@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def get_checker_files(request):
    file_id = request.GET.get('file_id')
    checkTaskObj = CheckerTask.objects.get(pk=file_id)
    
    checkTaskObj.document
    checker_invalid_objs = CheckerInvalid.objects.filter(checker_task=checkTaskObj)
    checker_valid_objs = CheckerValid.objects.filter(checker_task=checkTaskObj)
    file = checkTaskObj.document.open('r') 
    list_checker = file.read().split('\n')
    list_for_checker = []
    for line in list_checker:
        # print(checker_valid_objs.count(), checker_invalid_objs.count())
        check_valid_details = checker_valid_objs.filter(details=line.strip())
        check_invalid_details = checker_invalid_objs.filter(details=line.strip())
        if line.strip() and not check_valid_details.exists() and not check_invalid_details.exists():
            list_for_checker.append(line)
    if list_for_checker:
        string_checker = '\n'.join(x for x in list_for_checker)   
        return HttpResponse(string_checker, content_type="text/plain")   
    else:
        return HttpResponse('', content_type="text/plain")   


@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def update_checker_task(request):

    if request.method == 'GET':
        return successResponse({"ok": "Get request processed"})
    update_post = json.loads(request.body)
    if request.user.is_staff:
        checkTask_obj = CheckerTask.objects.filter(pk=update_post['id'])
    else:
        checkTask_obj = CheckerTask.objects.filter(pk=update_post['id'], owner=request.user)
    if checkTask_obj.exists():
        checkTask_obj.update(**update_post['update_data'])
        checkTask_obj = CheckerTask.objects.get(
            pk=update_post['id'])
        checker_task_data = CheckerTaskSerializer(checkTask_obj)
    return successResponse({'data':checker_task_data.data})
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_checker_valid(request):
    accounts_playload = json.loads(request.body)
    list_update = accounts_playload['data']
    
    objs = [
    
    CheckerValid(
        owner=User.objects.get(username=line['checker_owner']),
        details=line['details'],
        checker_task_id=line['checker_task'],
        checker_type=CheckerType.objects.get(value=line['checker_type'])
      ) for line in list_update
    ]
    msg = CheckerValid.objects.bulk_create(objs)
    return successResponse()   
  
@api_view(['GET', 'POST', 'PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def add_checker_invalid(request):
    accounts_playload = json.loads(request.body)
    list_update = accounts_playload['data']
    objs = [
    CheckerInvalid(
        owner=User.objects.get(username=line['checker_owner']),
        details=line['details'],
        checker_task_id=line['checker_task'],
        checker_type=CheckerType.objects.get(value=line['checker_type'])
      ) for line in list_update
    ]
    msg = CheckerInvalid.objects.bulk_create(objs)
    return successResponse()     
  

@api_view(['POST'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def agent_poll(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return errorResponse("Invalid JSON data", 400)
    
    hwid = data.get("hwid", "").strip()
    if not hwid:
        return errorResponse("HWID is required", 400)
        
    running_profiles = data.get("running_profiles", [])
    
    # 1. Update HWID status and last_poll timestamp
    hwid_objs = UserHwid.objects.filter(user=request.user, value=hwid)
    if hwid_objs.exists():
        hwid_obj = hwid_objs.first()
        hwid_obj.last_poll = timezone.now()
        hwid_obj.save(update_fields=['last_poll'])
    else:
        hwid_obj = UserHwid.objects.create(
            user=request.user, 
            value=hwid, 
            status=0,
            last_poll=timezone.now()
        )
        
    if hwid_obj.status != 0:
        return errorResponse("HWID is banned or inactive", 403)
        
    # 2. Update running profiles list in django cache
    from django.core.cache import cache
    cache.set(f"running_profiles:{request.user.id}", running_profiles, timeout=30)
    
    # 3. Get pending commands for this user and HWID
    pending_commands = AgentCommand.objects.filter(
        user=request.user,
        hwid=hwid,
        status='pending'
    ).order_by('id')
    
    commands_to_send = []
    for cmd in pending_commands:
        commands_to_send.append({
            "id": cmd.id,
            "command_type": cmd.command_type,
            "profile_id": cmd.profile_id,
            "profile_data": json.loads(cmd.profile_data) if cmd.profile_data else {}
        })
        cmd.status = 'sent'
        cmd.save(update_fields=['status'])
        
    return successResponse({
        "success": True,
        "commands": commands_to_send
    })

  

    
