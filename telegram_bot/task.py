from ensurepip import version
import re, telebot, ast, requests
from tkinter import N
from celery import shared_task
from storagon import settings

from servermain.models import AccountBalance, AccountCurrency
from django.contrib.auth.models import User
from telegram_bot.models import *
from storagon.enum import *
from servermain.controllers import UserController
from telegram_bot.api.TelegramBot_RestfulApi import AccountsSellingSerializer, CheckerTypeFunctionSerializer, CreatorTypeFunctionSerializer
from rest_framework.authtoken.models import Token
import random, json, os, pathlib, functools, shutil
from tqdm.auto import tqdm
from pathlib import Path
from telebot import types
from django.core.files import File
import datetime

def send_telegram_notify_to_group(group_id,msg,reply_markup=None,reply_id=None):
    #token='1235501300:AAEWPcah92B1PvsdvTCSHdT12CCg4gq-qZo'
    token = settings.TELEGRAM_TOKEN
    bot = telebot.TeleBot(token)
    send_msg = bot.send_message(group_id,'<b>'+msg+'</b>',reply_to_message_id=reply_id,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=False)
    return send_msg

def edit_telegram_notify_to_group(chat_id,message_id,text,reply_markup=None):
    #token='1235501300:AAEWPcah92B1PvsdvTCSHdT12CCg4gq-qZo'
    token = settings.TELEGRAM_TOKEN
    bot = telebot.TeleBot(token)
    edited_msg = bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=text, reply_markup=reply_markup, parse_mode='HTML')
    return edited_msg

def download_file(url, local_filename):
    # local_filename = url.split('/')[-1]

    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get('Content-Length', 0))

    path = pathlib.Path(local_filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    r.raw.read = functools.partial(r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)
    return path   


def download_file_from_telegram(fileInfo):
    token = settings.TELEGRAM_TOKEN
    bot = telebot.TeleBot(token)
    file_info = bot.get_file(fileInfo['file_id'])
    # print('===file_info===',file_info)
    file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)
    file_path = download_file(file_url, fileInfo['file_unique_id'])
    return file_path
    # print(file_url)
    # file = requests.get(file_url)
    # print(file_path)
    # f = open(file_path, 'r', encoding='utf-8')
    # result = f.read()

    # print('==result==',result)
    # f.close()
    # os.remove(file_path)
    # print('===file===',file_info)
def create_checker_markup(checker_id,valid=0,invalid=0, unknown=0, listing_type='',page=0):
    
    markup = types.InlineKeyboardMarkup()
    callback_valid = '%s|%s|%s' % ('get_valid', checker_id, listing_type)
    callback_invalid = '%s|%s|%s' % ('get_invalid', checker_id, listing_type)
    callback_unknown = '%s|%s|%s' % ('get_unknown', checker_id, listing_type)
    inline_keyboard_valid = types.InlineKeyboardButton('Valid: %s' % (valid) , callback_data=str(callback_valid))
    inline_keyboard_invalid = types.InlineKeyboardButton('Invalid: %s' % (invalid), callback_data=str(callback_invalid))
    inline_keyboard_unknown = types.InlineKeyboardButton('Unknown: %s' % (unknown), callback_data=str(callback_unknown))
    markup.row(inline_keyboard_valid,inline_keyboard_invalid, inline_keyboard_unknown)

    new_markup= create_menu_markup(markup, listing_type, page)    
    return new_markup

def create_checker_markup(checker_id,valid=0,invalid=0, unknown=0, listing_type='',page=0):
    
    markup = types.InlineKeyboardMarkup()
    callback_valid = '%s|%s|%s' % ('get_valid', checker_id, listing_type)
    callback_invalid = '%s|%s|%s' % ('get_invalid', checker_id, listing_type)
    callback_unknown = '%s|%s|%s' % ('get_unknown', checker_id, listing_type)
    inline_keyboard_valid = types.InlineKeyboardButton('Valid: %s' % (valid) , callback_data=str(callback_valid))
    inline_keyboard_invalid = types.InlineKeyboardButton('Invalid: %s' % (invalid), callback_data=str(callback_invalid))
    inline_keyboard_unknown = types.InlineKeyboardButton('Unknown: %s' % (unknown), callback_data=str(callback_unknown))
    markup.row(inline_keyboard_valid,inline_keyboard_invalid, inline_keyboard_unknown)
    new_markup = create_page_navigation_markup(markup, listing_type, page)
    new_markup= create_checker_menu_markup(markup, listing_type, page)    
    return new_markup

def create_page_navigation_markup(markup, listing_type='',page=0):
    backPage = page-1
    nextPage = page+1
    lastPage = -1
    if backPage <=0:
        backPage=0
    callback_data_firstpage = '%s|%s|%s' % ('set_page', 0, listing_type)#{'action': 'set_page', 'value': 0, 'type':listing_type}    
    inline_keyboard_first_page = types.InlineKeyboardButton('First Page \U0001F51D', callback_data=str(callback_data_firstpage))
        
    callback_data_back_page = '%s|%s|%s' % ('set_page', backPage, listing_type)#{'action': 'set_page', 'value': backPage, 'type':listing_type}   
    inline_keyboard_back_page = types.InlineKeyboardButton('Back \U00002B05', callback_data=str(callback_data_back_page))
    
    
    callback_data_next_page = '%s|%s|%s' % ('set_page', nextPage, listing_type)#{'action': 'set_page', 'value': nextPage, 'type':listing_type} 
    inline_keyboard_next_page = types.InlineKeyboardButton('Next \U000027A1', callback_data=str(callback_data_next_page))
    
    
    callback_data_last_page = '%s|%s|%s' % ('set_page', lastPage, listing_type)#{'action': 'set_page', 'value': lastPage, 'type':listing_type}
    inline_keyboard_last_page = types.InlineKeyboardButton('Last Page \U0001F51A', callback_data=str(callback_data_last_page))
    markup.row(inline_keyboard_first_page,inline_keyboard_back_page,inline_keyboard_next_page,inline_keyboard_last_page)
    return markup
    
def create_checker_menu_markup(markup, listing_type='',page=0):	
    callback_data_stop = '%s|%s|%s' % ('stop', 'stop', listing_type)
    inline_keyboard_menu = types.InlineKeyboardButton('Stop \U0001F6AB', callback_data=str(callback_data_stop))
    
    callback_data_refresh = '%s|%s|%s' % ('recheck', 'recheck', listing_type)#{'action': 'set_page', 'value': 'refresh', 'type':listing_type} 

    inline_keyboard_refesh = types.InlineKeyboardButton('ReCheck \U0001F504', callback_data=str(callback_data_refresh))
    inline_keyboard_deposit = types.InlineKeyboardButton('Deposit \U0001F4B3', callback_data='deposit')
    markup.row(inline_keyboard_menu, inline_keyboard_refesh, inline_keyboard_deposit)
    return markup   

def create_menu_markup(markup, listing_type='',page=0):
    backPage = page-1
    nextPage = page+1
    lastPage = -1
    if backPage <=0:
        backPage=0
    callback_data_firstpage = '%s|%s|%s' % ('set_page', 0, listing_type)#{'action': 'set_page', 'value': 0, 'type':listing_type}    
    inline_keyboard_first_page = types.InlineKeyboardButton('First Page \U0001F51D', callback_data=str(callback_data_firstpage))
        
    callback_data_back_page = '%s|%s|%s' % ('set_page', backPage, listing_type)#{'action': 'set_page', 'value': backPage, 'type':listing_type}   
    inline_keyboard_back_page = types.InlineKeyboardButton('Back \U00002B05', callback_data=str(callback_data_back_page))
    
    
    callback_data_next_page = '%s|%s|%s' % ('set_page', nextPage, listing_type)#{'action': 'set_page', 'value': nextPage, 'type':listing_type} 
    inline_keyboard_next_page = types.InlineKeyboardButton('Next \U000027A1', callback_data=str(callback_data_next_page))
    
    
    callback_data_last_page = '%s|%s|%s' % ('set_page', lastPage, listing_type)#{'action': 'set_page', 'value': lastPage, 'type':listing_type}
    inline_keyboard_last_page = types.InlineKeyboardButton('Last Page \U0001F51A', callback_data=str(callback_data_last_page))
    markup.row(inline_keyboard_first_page,inline_keyboard_back_page,inline_keyboard_next_page,inline_keyboard_last_page)

    
    
    inline_keyboard_menu = types.InlineKeyboardButton('Menu \U0001F3D8', callback_data='menu')
    
    callback_data_refresh = '%s|%s|%s' % ('set_page', 'refresh', listing_type)#{'action': 'set_page', 'value': 'refresh', 'type':listing_type} 

    inline_keyboard_refesh = types.InlineKeyboardButton('Refresh \U0001F504', callback_data=str(callback_data_refresh))
    inline_keyboard_deposit = types.InlineKeyboardButton('Deposit \U0001F4B3', callback_data='deposit')
    markup.row(inline_keyboard_menu, inline_keyboard_refesh, inline_keyboard_deposit)
    return markup    
    
def create_function_listing_markup(listing, listing_type='',page=0):
    # backPage = page-1
    # nextPage = page+1
    # lastPage = -1
    # if backPage <=0:
    #     backPage=0
    
    markup = types.InlineKeyboardMarkup()
    i = 0
    while i < len(listing):
        line_function1 = listing[i]
        line_function2 = listing[i+1]
        callback_data1 = '%s|%s|%s' % ('set_checker', line_function1['value'], listing_type)#{'action': 'set_checker', 'value': line_function1['value'], 'type':listing_type}
        callback_data2 = '%s|%s|%s' % ('set_checker', line_function2['value'], listing_type)#{'action': 'set_checker', 'value': line_function2['value'], 'type':listing_type}
        inline_keyboard_function1 = types.InlineKeyboardButton(line_function1['value'], callback_data=str(callback_data1))
        inline_keyboard_function2 = types.InlineKeyboardButton(line_function2['value'], callback_data=str(callback_data2))
        markup.row(inline_keyboard_function1,inline_keyboard_function2)
        i+=2
    new_markup= create_menu_markup(markup, listing_type, page)    
    return new_markup





def create_listing_markup(listing,type,page=0):

    markup = types.InlineKeyboardMarkup()

    for line in listing:
        inline_keyboard_account = types.InlineKeyboardButton(line['account'], callback_data='view|%s' %(line['id']))
        inline_keyboard_buy = types.InlineKeyboardButton('$%s \U0001F6D2' % (line['price']), callback_data='buy|%s' %(line['id']))
        markup.row(inline_keyboard_account,inline_keyboard_buy)
    inline_keyboard_first_page = types.InlineKeyboardButton('First Page \U0001F51D', callback_data='first_page')
    inline_keyboard_back_page = types.InlineKeyboardButton('Back \U00002B05', callback_data='back|%s' % (page-1))
    inline_keyboard_next_page = types.InlineKeyboardButton('Next \U000027A1', callback_data='next|%s' % (page+1))
    inline_keyboard_last_page = types.InlineKeyboardButton('Last Page \U0001F51A', callback_data='last_page')
    markup.row(inline_keyboard_first_page,inline_keyboard_back_page,inline_keyboard_next_page,inline_keyboard_last_page)

    inline_keyboard_menu = types.InlineKeyboardButton('Menu \U0001F3D8', callback_data='menu')
    inline_keyboard_refesh = types.InlineKeyboardButton('Refresh \U0001F504', callback_data='refesh|%s' % (type))
    inline_keyboard_deposit = types.InlineKeyboardButton('Deposit \U0001F4B3', callback_data='deposit')
    markup.row(inline_keyboard_menu, inline_keyboard_refesh, inline_keyboard_deposit)
    return markup

def create_deposit_markup():

    markup = types.InlineKeyboardMarkup()

    inline_keyboard_btc = types.InlineKeyboardButton('BTC', callback_data='deposit|BTC')
    inline_keyboard_eth = types.InlineKeyboardButton('ETH', callback_data='deposit|ETH')
    inline_keyboard_ltc = types.InlineKeyboardButton('LTC', callback_data='deposit|LTC')
    markup.row(inline_keyboard_btc, inline_keyboard_eth, inline_keyboard_ltc)
    return markup

def create_html_show(type='',balance='',total='',page='',total_page='',updated='', status='', plant_text='',displaying_page='Displaying'):
    html_show = '''
<b>\U0001F47B MunBot %s AIO automatic \U0001F47D</b>
<b>Balance: </b> <code>$%s \U0001F4B3</code>
<b>Total: </b> <code>%s \U0001F6D2</code>
<b>Notification: </b> <i>%s</i>
%s
<pre>%s page %s of %s. Last updated @%s</pre>
    ''' % (type, balance, total, status, plant_text, displaying_page, page, total_page, updated)
    return html_show

def create_html_deposit(balance):
    html_show = '''
<b>\U0001F47B MunBot automatic buying accounts \U0001F47D</b>
<b>Balance: </b><code>$%s \U0001F4B3</code>
Choose your deposit amount and the coin type

Payment modes supported are 
BTC | ETH | LTC | More being added soon

Funds will be added after 2 confirmations.
    ''' % (balance)
    return html_show

def create_html_deposit_details(balance,payment_method, address, account_id):
    html_show = '''
<b>\U0001F47B MunBot automatic buying accounts \U0001F47D</b>
<b>Balance: </b><code>$%s \U0001F4B3</code>
Here is the details:-
<code>Send crypto to the address shown below</code><a href="https://chart.googleapis.com/chart?chs=200x200&chld=%s&cht=qr&%s">.</a>
Payment: %s
Address: %s
Charge ID: %s

1. Funds will be automatic convert to USD by your balance.
2. Funds will be added after 2 confirmations.
    ''' % (balance,'L%7C2',address,payment_method,address, account_id)
    return html_show

def get_or_create_user(username):
    User.objects.filter(username=username)


def get_deposit_address(user,name='BTC'):
    currency_obj, created = AccountCurrency.objects.get_or_create(code=name, label=name)
    account_balance_obj, created = AccountBalance.objects.get_or_create(user=user,balance_type=BalanceType.credit,currency=currency_obj)
    # current_banlance = UserController.calculateUserBlance(account_balance_obj)
    if created or len(account_balance_obj.address) < 3:
        walletAddress = createCoinBaseAddress(name)
        if walletAddress:
            account_balance_obj.address = walletAddress['address']
            account_balance_obj.account_id = walletAddress['id']
            account_balance_obj.save()
            return (walletAddress['address'],walletAddress['id'])
        else:
            return
    else:
        return (account_balance_obj.address, account_balance_obj.account_id)


@shared_task
def check_cmd_telegram(chat_id,message_id=None,text=None,callback_query=None, chat=None, document=None, original_text=''):

    userTelegram_objs = UserTelegram.objects.filter(telegram_id=chat_id)
    if not userTelegram_objs.exists():
        print('===create new user===')
        user, created = User.objects.get_or_create(username=chat_id)
        # user.save()
        user.set_password('telegrambot123')
        
        if chat:
            user_telegram = UserTelegram(user=user, telegram_id=chat_id)
        else:
            user_telegram = UserTelegram(user=user, telegram_id=chat_id)
        user_telegram.save()
        userTelegram_objs = UserTelegram.objects.filter(telegram_id=chat_id)

    user_telegram = userTelegram_objs.first()
    user = user_telegram.user
    currency_obj, created = AccountCurrency.objects.get_or_create(code='USD', label='USD')
    account_balance_obj, created = AccountBalance.objects.get_or_create(user=user,balance_type=BalanceType.credit,currency=currency_obj)
    current_banlance = UserController.calculateUserBlance(account_balance_obj)

    if callback_query:
        print('callback_query==', callback_query)
        if callback_query.find('|') != -1:
            # callback_query_json = ast.literal_eval(callback_query.strip())
            
            # edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)
            # {'action': 'checker', 'value': 'ccn gate 2', 'type': 'checker'}
            callback_split = callback_query.split('|')
            reply_action = callback_split[0].strip()
            reply_value = callback_split[1].strip()
            reply_type = callback_split[2].strip()
            if reply_action == 'set_checker':
                checker_objs = CheckerType.objects.filter(value=reply_value.strip())
                if checker_objs.exists():
                    user_telegram.checker_type = checker_objs[0]
                    user_telegram.save()
                    status_text = 'Your checker mode has been set as %s' % (reply_value.strip())
                    checker_objs = CheckerType.objects.all()
                    limit = 10
                    account_page = 1
                    account_total = checker_objs.count()
                    import math
                    page_total = math.ceil(float(account_total) / 10)
                    # print(page_total)
                    list_accounta_show = checker_objs[(account_page-1)*limit:account_page*limit]      
                    
                    listing_show_sers = CheckerTypeFunctionSerializer(list_accounta_show, many=True)
                    
                    checker_last_obj = checker_objs.first()
                    
                    html_show = create_html_show('Checker', current_banlance, checker_objs.count(), account_page, page_total, checker_last_obj.created.strftime("%d-%m-%Y %H:%M"), status=status_text)

                    markup_button = create_function_listing_markup(listing_show_sers.data, listing_type='checker', page=account_page)

                    # send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
                    
                    edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)
            elif reply_action == 'get_invalid' or reply_action == 'get_valid':
                checktask_objs = CheckerTask.objects.filter(pk=int(reply_value))
                if checktask_objs.exists():
                    checktask_obj = checktask_objs.first()
                    document_valid = checktask_obj.document_valid
                    document_invalid = checktask_obj.document_invalid
                    if document_valid:
                        f = document_valid.open('r')
                        valid_result = f.read()
                    else:
                        list_valid_objs = CheckerValid.objects.filter(checker_task_id=int(reply_value))
                        
                        valid_result = '\n'.join('<code>'+str(x.details)+'</code>' for x in list_valid_objs)

                        
                    if document_invalid:
                        f = document_valid.open('r')
                        invalid_result = f.read()
                    else:
                        list_invalid_objs = CheckerInvalid.objects.filter(checker_task_id=int(reply_value))
                        
                        invalid_result = '\n'.join('<code>'+str(x.details)+'</code>' for x in list_invalid_objs) 
                      
                    if valid_result:
                        list_display_valid = valid_result.strip().split('\n')
                    else:
                        list_display_valid = []
                    if invalid_result:
                        list_display_invalid = invalid_result.strip().split('\n')  
                    else:
                        list_display_invalid = []
                    
                    if reply_action == 'get_invalid':
                        list_display_result = list_display_invalid
                        display_page = checktask_obj.display_page_invalid
                    else:
                        list_display_result = list_display_valid
                        display_page = checktask_obj.display_page_valid
                    import math
                    page_total = math.ceil(float(len(list_display_result)) / 50)
                    list_display = []
                    i = (display_page-1)*50
                    while i < len(list_display_result) and len(list_display) < 50:
                        list_display.append(list_display_result[i])
                        i+=1  
                    plant_text = '\n'.join('<code>'+str(x)+'</code>' for x in list_display)
                    status_text = 'Checked %s/%s Left %s: %s valid, %s invalid.' % (len(list_display_valid)+len(list_display_invalid), checktask_obj.total_value, checktask_obj.total_value-(len(list_display_valid)+len(list_display_invalid)), len(list_display_valid), len(list_display_invalid))
                    html_show = create_html_show('Checker '+ checktask_obj.checker_type.value, current_banlance, checktask_obj.total_value, display_page, page_total, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), status=status_text, plant_text=plant_text, displaying_page='Invalid')

                    markup_button = create_checker_markup(reply_value,listing_type='checker_status', valid=len(list_display_valid), invalid=len(list_display_invalid))
                    try:
                        send_msg = edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)	
                    except Exception as e:
                        print(e)                    
                
                    
        elif callback_query == 'deposit':
            html_show = create_html_deposit(0)
            markup_button = create_deposit_markup()
            edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)
    elif document:
        if user_telegram.checker_type:
            if document['mime_type'] == 'text/plain' and document['file_size'] <= 62500:
                file_path = download_file_from_telegram(document)
                
                path_file = Path(file_path)
                with path_file.open(mode='rb') as f:
                    check_task = CheckerTask()
                    check_task.checker_type = user_telegram.checker_type
                    check_task.file_id = document['file_id']
                    check_task.file_name = document['file_name']
                    check_task.file_unique_id = document['file_unique_id']
                    check_task.file_size = document['file_size']
                    check_task.document = File(f, name=document['file_unique_id'])
                    check_task.owner = user
                    check_task.save()
                    check_task.refresh_from_db()
                    
                with path_file.open(mode='r') as f:
                    result = f.read()
                    checker_split = result.split('\n')
                    list_valid = [line for line in checker_split if line.find('|') != -1]
                    # checker_count = len(result.split('\n'))
                    import math
                    page_total = math.ceil(float(len(list_valid)) / 50)
                    # print(page_total)  
                    status_text = 'Waiting for worker...'                 
                    html_show = create_html_show('Checker '+ str(user_telegram.checker_type.value), current_banlance, len(list_valid), 1, 1, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), status=status_text, displaying_page='Valid')

                    markup_button = create_checker_markup(check_task.pk,listing_type='checker_status')

                    send_msg = send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
                    print(send_msg)
                    print('send_msg==', send_msg.message_id)
                    check_task.total_value = len(checker_split)
                    check_task.status_message_id = send_msg.message_id
                    check_task.save()
                    # edit_telegram_notify_to_group(chat_id, message_id=send_msg['message_id'], msg=html_show,reply_id=message_id, reply_markup=markup_button)
                os.remove(path_file)

            else:
                msg = 'You have to send the TXT file and not over 50kb file!'
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
    
    elif text:    
        cmd = text.lstrip("/").strip()
        extra_text = ''
        if cmd.find(' ') != -1:
            new_cmds = cmd.split(' ')
            first_cmd = new_cmds[0].strip()
            #cmd
            extra_text = cmd.split(first_cmd)[-1].strip()
            cmd = first_cmd
        elif not cmd:
            print('===text===', user_telegram.checker_type)
            print(text)

        if cmd == "listing":
            print('===listing===')
            list_account_objs = AccountsSelling.objects.filter(type__value='amazon', selling_status=SellingStatus.listed)
            if list_account_objs.exists():
                limit = 10
                account_page = 1
                account_total = list_account_objs.count()
                import math
                page_total = math.ceil(float(list_account_objs.count()) / 10)
                print(page_total)
                list_accounta_show = list_account_objs[(account_page-1)*limit:account_page*limit]
                data = AccountsSellingSerializer(list_accounta_show, many=True).data
                html_show = create_html_show('amazon', current_banlance, account_total, account_page, page_total, '2021-11-25 21:02')

                markup_button = create_listing_markup(data, 'amazon', page=1)

                send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
            else:
                msg = "The all of account sold out."
                # send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        elif cmd == 'deposit':
            html_show = create_html_deposit(0)
            markup_button = create_deposit_markup()
            send_telegram_notify_to_group(chat_id, msg=html_show, reply_id=message_id, reply_markup=markup_button)
        elif cmd == 'token':
            print('==get token user==')
            user = User.objects.get(username=chat_id)
            token, created = Token.objects.get_or_create(user=user)
            # user.set_password('telegrambot123')
            # user.save()
            msg = "token:%s" %(token.key)
            # send_message(msg, t_chat["id"])
            send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        elif cmd == 'setversion':
            print('==set version==')
            if str(chat_id) == '892844098':
                mun_obj = MunAnti.objects.create(version=extra_text.strip())
                msg = 'New version %s already updated!' % (extra_text)
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        elif cmd == 'addhwid':
            
            if str(chat_id) == '892844098':
                print('==set addhwid==')
                if extra_text.find(' ') != -1:
                    new_cmds = extra_text.split(' ')
                    user_id = new_cmds[0].strip()
                    # user_id = new_cmds[1].strip()
                    function_add = extra_text.split(user_id)[-1].strip()
                    userObj = User.objects.get(username=user_id)
                    print(cmd, user_id, function_add)
                    mun_obj, created = UserHwid.objects.get_or_create(value=function_add, user=userObj)
                    msg = 'Your hwid %s already updated!' % (mun_obj.value)
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
            else:
                hwid_objs = UserHwid.objects.filter(user=user)
                if not hwid_objs.exists():
                    mun_obj, created = UserHwid.objects.get_or_create(value=extra_text.strip(), user=user)  
                    msg = 'Your hwid %s already updated!' % (mun_obj.value)
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
                else:
                    # hwid_obj = hwid_objs.first()
                    # hwid_obj.value = extra_text.strip()
                    # hwid_obj.save()
                    mun_obj, created = UserHwid.objects.get_or_create(value=extra_text.strip(), user=user)  
                    msg = 'Your hwid %s already updated!' % (mun_obj.value)
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id) 
        elif cmd == 'addcheck':
            
            if str(chat_id) == '892844098':
                print('==set addcheck==')
                if extra_text.find(' ') != -1:
                    new_cmds = extra_text.split(' ')
                    user_id = new_cmds[0].strip()
                    # user_id = new_cmds[1].strip()
                    function_add = extra_text.split(user_id)[-1].strip()
                    userObj = User.objects.get(username=user_id)
                    print(cmd, user_id, function_add)
                    mun_obj, created = UserCheckFunction.objects.get_or_create(value=function_add.strip(), label=function_add.strip(), user=userObj)
                    msg = 'Your check function %s already updated!' % (mun_obj.value)
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        elif cmd == 'addcreate':
            
            if str(chat_id) == '892844098':
                print('==set addcreate==')
                if extra_text.find(' ') != -1:
                    new_cmds = extra_text.split(' ')
                    user_id = new_cmds[0].strip()
                    # user_id = new_cmds[1].strip()
                    function_add = extra_text.split(user_id)[-1].strip()
                    userObj = User.objects.get(username=user_id)
                    print(cmd, user_id, function_add)
                    mun_obj, created = UserCreateFunction.objects.get_or_create(value=function_add.strip(), label=function_add.strip(), user=userObj)
                    msg = 'Your create function %s already updated!' % (mun_obj.value)
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id )         
                    
        elif cmd == 'addchecker':
            if str(chat_id) == '892844098':
                print('==set addchecker==')
                function_add = extra_text.strip()
                mun_obj, created = CheckerType.objects.get_or_create(value=function_add.strip(), label=function_add.strip())
                msg = 'Your checker function %s already updated!' % (mun_obj.value)
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id )        
        elif cmd == 'addcreator':
            if str(chat_id) == '892844098':
                print('==set addchecker==')
                function_add = extra_text.strip()
                mun_obj, created = CreatorType.objects.get_or_create(value=function_add.strip(), label=function_add.strip())
                msg = 'Your checker function %s already updated!' % (mun_obj.value)
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id )                       
        elif cmd == 'version' or cmd == 'v':
            print('==get version==')
            obj_last = MunAnti.objects.last()
            if obj_last.update_url:
                update_url = obj_last.update_url
            else:
                update_url = 'https://munanti.s3.ap-southeast-1.amazonaws.com/Update.zip'
            msg = '''
MunAnti AIO Automator.
Version:%s
Update URL:%s
Updateded:%s
                ''' % (obj_last.version, update_url, obj_last.modified.strftime("%d-%m-%Y %H:%M"))
            send_telegram_notify_to_group(chat_id, msg=msg, reply_id=message_id)
              
        elif cmd == 'setpassword':
            print('==set password user==')
            user = User.objects.get(username=chat_id)
            
            if len(extra_text) <= 3:
                msg = 'Your password must be longer that 3 characters'
                send_telegram_notify_to_group(
                    chat_id, msg=str(msg), reply_id=message_id)
                return
            else:
                # token, created = Token.objects.get_or_create(user=user)
                user.set_password(extra_text)
                user.save()
                msg = '''
Your password have been changed successfully.
Username:%s
Password:%s
                ''' % (chat_id, extra_text)
                # send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        
        elif cmd == 'checker':
            print('==set checker==')
            if not extra_text.strip():
                checker_objs = CheckerType.objects.all()
                limit = 10
                account_page = 1
                account_total = checker_objs.count()
                import math
                page_total = math.ceil(float(account_total) / 10)
                print(page_total)
                list_accounta_show = checker_objs[(account_page-1)*limit:account_page*limit]      
                
                listing_show_sers = CheckerTypeFunctionSerializer(list_accounta_show, many=True)
                
                checker_last_obj = checker_objs.first()
                
                html_show = create_html_show('Checker', current_banlance, checker_objs.count(), account_page, page_total, checker_last_obj.created.strftime("%d-%m-%Y %H:%M"))

                markup_button = create_function_listing_markup(listing_show_sers.data, listing_type='checker', page=account_page)

                send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
            else:
                checker_objs = CheckerType.objects.filter(value=extra_text.strip())
                if checker_objs.exists():
                    user_telegram.checker_type = checker_objs[0]
                    user_telegram.save()
                    msg = 'Your checker mode has been set as %s' % (extra_text.strip())
                    send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
                else:
                    checker_objs = CheckerType.objects.all()
                    limit = 10
                    account_page = 1
                    account_total = checker_objs.count()
                    import math
                    page_total = math.ceil(float(account_total) / 10)
                    print(page_total)
                    list_accounta_show = checker_objs[(account_page-1)*limit:account_page*limit]      
                    
                    listing_show_sers = CheckerTypeFunctionSerializer(list_accounta_show, many=True)
                    
                    checker_last_obj = checker_objs.last()
                    
                    html_show = create_html_show('Checker', current_banlance, checker_objs.count(), account_page, page_total, checker_last_obj.created.strftime("%d-%m-%Y %H:%M"))

                    markup_button = create_function_listing_markup(listing_show_sers.data, listing_type='checker', page=account_page)

                    send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)

        elif cmd == 'task':
            check_task_objs = CheckerTask.objects.filter(user=user)
            msg = 'You are having %s tasks' % (check_task_objs.count())
            send_telegram_notify_to_group(
                chat_id, msg=str(msg), reply_id=message_id)
        # else:
        #     import math
        #     page_total = math.ceil(float(123) / 10)
        #     print('test page==',page_total)
        #     msg = "The system cannot recognize your command! please contact admin: "+cmd
        #     #send_message(msg, t_chat["id"])
        #     send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=message_id)

# def update_checker_status(chat_id, message_id, checkerTaskInfo):
#     print('==update_checker_status==')
#     markup = create_checker_markup()
    
#     html_show = create_html_show('Checker', current_banlance, checker_objs.count(), account_page, page_total, checker_last_obj.created.strftime("%d-%m-%Y %H:%M"))

#     markup_button = create_function_listing_markup(listing_show_sers.data, listing_type='checker', page=account_page)

#     send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
    # send_telegram_notify_to_group(
    #     chat_id, msg=str(msg), reply_id=message_id)    


def createCoinBaseAddress(name="BTC"):
    print('==Create Coin Base==')
    from coinbase.wallet.client import Client
    api_key='11MXKS7siI92KbqW'
    api_secret='bjWdjutsdhUxq7MZPiBHCNO1zCPVqvvp'
    client = Client(api_key, api_secret)
    if name=='BTC':
        account_id = '7c85e01f-b6ea-51d6-89b1-708a019257ab'
    elif name == 'LTC':
        account_id = '696babe5-d4d4-57df-864e-98b19dc24854'
    elif name == 'ETH':
        account_id = '3131d761-0b89-5458-b8ea-e87d5ab2d77b'
    else:
        return
    created = client.create_address(account_id)
    print('created',created)

    return created
def import_account_data():
    print('==import_account_data==')
    # | 1 | Thomas | Neumann | 321 BERKLEY PL | STAUNTON | VA | 24401 | 540-255-7790 | 461791163 | Aug  8 1973 12:00AM | tan5f@virginia.edu | University Of Virginia | 0.00 | 434-243-2833
    f = open('account_data.txt', 'r', encoding="ISO-8859-1")
    list_create = []
    dict_ssn={}
    result = f.read()
    for line in result.split('\n'):
        print(line)
        line_split = line.split('|')
        if line_split:
            try:
                data = {}
                data['first_name'] = line_split[2].strip()
                data['last_name'] = line_split[3].strip()
                data['address1'] = line_split[4].strip()
                data['city'] = line_split[5].strip()
                data['state'] = line_split[6].strip()
                data['zipcode'] = line_split[7].strip()
                data['ssn'] = line_split[9].strip()
                data['dob'] = line_split[10].strip()
                if line_split[9].strip() not in dict_ssn:
                    list_create.append(AccountsData(**data))
                    dict_ssn[line_split[9].strip()] = 1
            except Exception as e:
                print(e)
                continue
    if list_create:
        AccountsData.objects.bulk_create(list_create)
        
def import_created_account(account_type):
    print('==import_created_account==')
    # | 1 | Thomas | Neumann | 321 BERKLEY PL | STAUNTON | VA | 24401 | 540-255-7790 | 461791163 | Aug  8 1973 12:00AM | tan5f@virginia.edu | University Of Virginia | 0.00 | 434-243-2833
    typeobj, created = AccountsType.objects.get_or_create(value=account_type, label=account_type)
    f = open('account.txt', 'r', encoding="utf8")
    list_create = []
    dict_ssn={}
    result = f.read()
    for line in result.split('\n'):
        print(line)
        line_split = line.split('|')
        if line_split:
            try:
                data = {}
                data['email'] = line_split[0].strip()
                data['password'] = line_split[1].strip()
                objFileter = AccountsCreated.objects.filter(email=line_split[0].strip())
                if not objFileter.exists():
                    list_create.append(AccountsCreated(email=line_split[0].strip(), password=line_split[1].strip(), type=typeobj))
            except Exception as e:
                print(e)
                continue
    if list_create:
        AccountsCreated.objects.bulk_create(list_create)     
    print('==created==', len(list_create))   
# if __name__ == '__main__':
#     # get_tbk_coupon('python')
#     print('===task===')
#     createCoinBaseAddress('ETH')

def fix_font_and_rects():
    list_obj = BrowserProfiles.objects.all()
    for line_obj in list_obj:
        if line_obj.profile_rects == 'Noise':
            line_obj.profile_rects = str(round(random.uniform(0.2, 0.35), 5))
        if line_obj.profile_font == 'Noise':
            listFonts = ['Arial', 'Calibri', 'Cambria', 'Cambria Math', 'Candara', 'Comic Sans MS', 'Comic Sans MS Bold', 'Comic Sans', 'Consolas', 'Constantia', 'Corbel', 'Courier New', 'Caurier Regular', 'Ebrima', 'Fixedsys Regular', 'Franklin Gothic', 'Gabriola Regular', 'Gadugi', 'Georgia', 'HoloLens MDL2 Assets Regular', 'Impact Regular', 'Javanese Text Regular', 'Leelawadee UI', 'Lucida Console Regular', 'Lucida Sans Unicode Regular', 'Malgun Gothic', 'Microsoft Himalaya Regular', 'Microsoft JhengHei', 'Microsoft JhengHei UI', 'Microsoft PhangsPa', 'Microsoft Sans Serif Regular', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft YaHei UI', 'Microsoft Yi Baiti Regular', 'MingLiU_HKSCS-ExtB Regular', 'MingLiu-ExtB Regular', 'Modern Regular', 'Mongolia Baiti Regular', 'MS Gothic Regular', 'MS PGothic Regular', 'MS Sans Serif Regular', 'MS Serif Regular', 'MS UI Gothic Regular', 'MV Boli Regular', 'Myanmar Text', 'Nimarla UI', 'Myanmar Tet', 'Nirmala UI', 'NSimSun Regular', 'Palatino Linotype', 'PMingLiU-ExtB Regular', 'Roman Regular', 'Script Regular', 'Segoe MDL2 Assets Regular', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Emoji Regular', 'Segoe UI Historic Regular', 'Segoe UI Symbol Regular', 'SimSun Regular', 'SimSun-ExtB Regular', 'Sitka Banner', 'Sitka Display', 'Sitka Heading', 'Sitka Small', 'Sitka Subheading', 'Sitka Text', 'Small Fonts Regular', 'Sylfaen Regular', 'Symbol Regular', 'System Bold', 'Tahoma', 'Terminal', 'Times New Roman', 'Trebuchet MS', 'Verdana', 'Webdings Regular', 'Wingdings Regular', 'Yu Gothic', 'Yu Gothic UI', 'Arial Black', 'Calibri Light', 'Courier', 'Fixedsys', 'Franklin Gothic Medium', 'Gabriola', 'HoloLens MDL2 Assets', 'Impact', 'Javanese Text', 'Leelawadee UI Semilight', 'Lucida Console', 'Lucida Sans Unicode', 'MS Gothic', 'MS PGothic', 'MS Sans Serif', 'MS Serif', 'MS UI Gothic', 'MV Boli', 'Malgun Gothic Semilight', 'Marlett', 'Microsoft Himalaya', 'Microsoft JhengHei Light', 'Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft YaHei Light', 'Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', 'MingLiU_HKSCS-ExtB', 'Modern', 'Mongolian Baiti', 'NSimSun', 'Nirmala UI Semilight', 'PMingLiU-ExtB', 'Roman', 'Script', 'Segoe MDL2 Assets', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'SimSun', 'SimSun-ExtB', 'Small Fonts', 'Sylfaen', 'Symbol', 'System', 'Webdings', 'Wingdings', 'Yu Gothic Light', 'Yu Gothic Medium', 'Yu Gothic UI Light', 'Yu Gothic UI Semibold', 'Yu Gothic UI Semilight', 'Arial Narrow', 'Arial Unicode MS', 'Book Antiqua', 'Bookman Old Style', 'Century', 'Century Gothic', 'Century Schoolbook', 'Garamond', 'Helvetica', 'Lucida Bright', 'Lucida Calligraphy', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Monotype Corsiva', 'MS Outlook', 'MS Reference Sans Serif', 'Times', 'Wingdings 2', 'Wingdings 3', 'default', 'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'inherit', 'auto', 'Brush Script MT', 'Broadway', 'Bell MT', 'Berlin Sans FB', 'Blackadder ITC', 'Curlz MT', 'Elephant', 'Engravers MT', 'Goudy Old Style', 'Minion Pro', 'Papyrus', 'Wide Latin', 'Snap ITC', 'Stencil', 'Old English Text MT', 'Ubuntu', 'Ubuntu Mono', 'Terminus Font', 'Terminus', 'Ubuntu Mono 13', 'Ubuntu Mono Regular', 'Apple Braille Outline 6 Dot', 'Apple Braille Outline 8 Dot', 'Apple Braille Pinpoint 6 Dot', 'Apple Braille Pinpoint 8 Dot', 'Apple Braille', 'Apple Symbols', 'AppleGothic', 'AquaKana', 'Geeza Pro Bold', 'Geeza Pro', 'Geneva', 'HelveLTMM', 'Helvetica LT MM', 'HelveticaNeue', 'Hiragino Kaku Gothic ProN W3', 'Hiragino Kaku Gothic ProN W6', 'Hiragino Mincho ProN W3', 'Hiragino Mincho ProN W6', 'Keyboard', 'LastResort', 'LiHei Pro', 'LucidaGrande', 'Menlo', 'Monaco', 'STHeiti', 'STHeiti Light', 'STXihei', 'Thonburi', 'ThonburiBold', 'Times LT MM', 'TimesLTMM', 'ZapfDingbats', 'AmericanTypewriter', 'Andale Mono', 'Apple Chancery', 'Apple LiGothic Medium', 'Arial Bold Italic', 'Arial Bold', 'Arial Italic', 'Arial Narrow Bold Italic', 'Arial Narrow Bold', 'Arial Narrow Italic', 'Arial Rounded Bold', 'Arial Unicode', 'Baskerville', 'BigCaslon', 'Brush Script', 'Chalkboard', 'Chalkduster', 'Cochin', 'Copperplate', 'Courier New Bold Italic', 'Courier New Bold', 'Courier New Italic', 'Didot', 'Futura', 'Georgia Bold Italic', 'Georgia Bold', 'Georgia Italic', 'GillSans', 'Hei', 'Herculanum', 'Hiragino Kaku Gothic Pro W3', 'Hiragino Kaku Gothic Pro W6', 'Hiragino Kaku Gothic Std W8', 'Hiragino Kaku Gothic StdN W8', 'Hiragino Maru Gothic Pro W4', 'Hiragino Maru Gothic ProN W4', 'Hiragino Mincho Pro W3', 'Hiragino Mincho Pro W6', 'Hoefler Text', 'Hoefler Text Ornaments', 'Kai', 'MarkerFelt', 'Optima', 'Osaka', 'OsakaMono', 'Skia', 'Tahoma Bold', 'Times New Roman Bold Italic', 'Times New Roman Bold', 'Times New Roman Italic', 'Trebuchet MS Bold Italic', 'Trebuchet MS Bold', 'Trebuchet MS Italic', 'Verdana Bold Italic', 'Verdana Bold', 'Verdana Italic', 'Zapfino', 'Aharoni Bold', 'Andalus Regular', 'Angsana New', 'Angsana New Bold', 'Angsana New Italic', 'Angsana New Bold Italic', 'AngsanaUPC', 'AngsanaUPC Bold', 'AngsanaUPC Italic', 'AngsanaUPC Bold Italic', 'Aparajita', 'Aparajita Bold', 'Aparajita Italic', 'Aparajita Bold Italic', 'Arabic Typesetting Regular', 'Arial Unicode MS Regular', 'Batang', 'BatangChe', 'Browallia New', 'Browallia New Bold', 'Browallia New Italic', 'Browallia New Bold Italic', 'BrowalliaUPC', 'BrowalliaUPC Bold', 'BrowalliaUPC Italic', 'BrowalliaUPC Bold Italic', 'Calibri Bold', 'Calibri Italic', 'Calibri Bold Italic', 'Cambria Bold', 'Cambria Italic', 'Cambria Bold Italic', 'Candara Bold', 'Candara Italic', 'Candara Bold Italic', 'Consolas Bold', 'Consolas Italic', 'Consolas Bold Italic', 'Constantia Bold', 'Constantia Italic', 'Constantia Bold Italic', 'Corbel Bold', 'Corbel Italic', 'Corbel Bold Italic', 'Cordia New', 'Cordia New Bold', 'Cordia New Italic', 'Cordia New Bold Italic', 'CordiaUPC', 'CordiaUPC Bold', 'CordiaUPC Italic', 'CordiaUPC Bold Italic', 'DFKai-SB', 'DaunPenh', 'David', 'David Bold', 'DilleniaUPC', 'DilleniaUPC Bold', 'DilleniaUPC Italic', 'DilleniaUPC Bold Italic', 'DokChampa', 'Dotum', 'DotumChe', 'Ebrima Bold', 'Estrangelo Edessa', 'EucrosiaUPC', 'EucrosiaUPC Bold', 'EucrosiaUPC Italic', 'EucrosiaUPC Bold Italic', 'Euphemia', 'FangSong', 'FrankRuehl', 'Franklin Gothic Medium Italic', 'FreesiaUPC', 'FreesiaUPC Bold', 'FreesiaUPC Italic', 'FreesiaUPC Bold Italic', 'Gautami', 'Gautami Bold', '& Georgia Bold Italic', 'Gisha', 'Gisha Bold', 'Gulim', 'GulimChe', 'Gungsuh', 'GungsuhChe', 'IrisUPC', 'IrisUPC Bold', 'IrisUPC Italic', 'IrisUPC Bold Italic', 'Iskoola Pota', 'IskoolaPota Bold', 'JasmineUPC', 'JasmineUPC Bold', 'JasmineUPC Italic', 'JasmineUPC Bold Italic', 'KaiTi', 'Kalinga', 'Kalinga Bold', 'Kartika', 'Kartika Bold', 'Khmer UI', 'Khmer UI Bold', 'KodchiangUPC', 'KodchiangUPC Bold', 'KodchiangUPC Italic', 'KodchiangUPC Bold Italic', 'Kokila', 'Kokila Bold', 'Kokila Italic', 'Kokila Bold Italic', 'Lao UI', 'Lao UI Bold', 'Latha', 'Latha Bold', 'Leelawadee', 'Leelawadee Bold', 'Levenim MT', 'Levenim MT Bold', 'LilyUPC', 'LilyUPC Bold', 'LilyUPC Italic', 'LilyUPC Bold Italic', 'MS Mincho', 'MS PMincho', 'Malgun Gothic Bold', 'Mangal', 'Mangal Bold', 'Meiryo UI', 'Meiryo UI Bold', 'Meiryo UI Italic', 'Meiryo UI Bold Italic', 'Meiryo', 'Meiryo Bold', 'Meiryo Italic', 'Meiryo Bold Italic', 'Microsoft JhengHei Bold', 'Microsoft New Tai Lue Bold', 'Microsoft PhagsPa Bold', 'Microsoft Tai Le Bold', 'Microsoft Uighur', 'Microsoft YaHei Bold', 'MingLiU', 'MingLiU_HKSCS', 'Miriam', 'Miriam Fixed', 'MoolBoran', 'Narkisim', 'Nyala', 'PMingLiU', 'Palatino Linotype Bold', 'Palatino Linotype Italic', 'Palatino Linotype Bold Italic', 'Plantagenet Cherokee', 'Raavi', 'Raavi Bold', 'Rod', 'Sakkal Majalla', 'Sakkal Majalla Bold', 'Segoe Print Bold', 'Segoe Script Bold', 'Segoe UI Bold', 'Segoe UI Italic', 'Segoe UI Bold Italic', 'Shonar Bangla', 'Shonar Bangla Bold', 'Shruti', 'Shruti Bold', 'SimHei', 'Simplified Arabic', 'Simplified Arabic Bold', 'Simplified Arabic Fixed', ' Times New Roman Bold', 'Traditional Arabic', 'Traditional Arabic Bold', 'Tunga', 'Tunga Bold', 'Utsaah', 'Utsaah Bold', 'Utsaah Italic', 'Utsaah Bold Italic', 'Vani', 'Vani Bold', 'Vijaya', 'Vijaya Bold', 'Vrinda', 'Vrinda Bold']
            fonts_max = random.randint(200, len(listFonts)-1)
            fonts_min = random.randint(0, 150)
            listUse = listFonts[fonts_min:fonts_max]  
            line_obj.profile_font = str(listUse)
        line_obj.save()