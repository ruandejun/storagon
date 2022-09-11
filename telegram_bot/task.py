import re, telebot
from celery import shared_task
from storagon import settings
from telebot import types
from servermain.models import AccountBalance, AccountCurrency
from django.contrib.auth.models import User
from telegram_bot.models import UserTelegram, AccountsSelling
from storagon.enum import *
from servermain.controllers import UserController
from telegram_bot.api.TelegramBot_RestfulApi import AccountsSellingSerializer
from rest_framework.authtoken.models import Token
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


def creat_listing_markup(listing,type,page=0):

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
def creat_deposit_markup():

    markup = types.InlineKeyboardMarkup()

    inline_keyboard_btc = types.InlineKeyboardButton('BTC', callback_data='deposit|BTC')
    inline_keyboard_eth = types.InlineKeyboardButton('ETH', callback_data='deposit|ETH')
    inline_keyboard_ltc = types.InlineKeyboardButton('LTC', callback_data='deposit|LTC')
    markup.row(inline_keyboard_btc, inline_keyboard_eth, inline_keyboard_ltc)
    return markup

def create_html_show(type,balance,total,page,total_page,updated):
    html_show = '''
<b>\U0001F47B MunBot %s accounts listing \U0001F47D</b>
<b>Balance: </b><code>$%s \U0001F4B3</code>
<b>Total: </b> <code>%s \U0001F6D2</code>
<pre>Displaying page %s of %s. Last updated @ %s</pre>
    ''' % (type,balance,total,page,total_page,updated)
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
def check_cmd_telegram(chat_id,message_id=None,text=None,callback_query=None, chat=None):

    userTelegram_objs = UserTelegram.objects.filter(telegram_id=chat_id)
    if not userTelegram_objs.exists():
        print('==create new user==')
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
        if callback_query.find('|') != -1:
            callback_split = callback_query.split('|')
            action = callback_split[0].strip()
            value = callback_split[1].strip()
            print(callback_query)
            if action == 'buy':
                print('==buy==', value)
            elif action == 'view':
                print('==view==', value)
            elif action == 'refesh':
                print('==refesh==', value)
            elif action == 'deposit':
                # print('==create deposit==', value)
                adddress_info = get_deposit_address(user, value)
                if adddress_info:
                    account_address, account_id = adddress_info
                    print('==create deposit==', account_address, account_id)
                    payment_method=value
                    html_show = create_html_deposit_details(current_banlance,payment_method,account_address,account_id)
                    markup_button = creat_deposit_markup()
                    edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)
        elif callback_query == 'deposit':
            html_show = create_html_deposit(0)
            markup_button = creat_deposit_markup()
            edit_telegram_notify_to_group(chat_id, message_id, html_show, reply_markup=markup_button)
    else:
        cmd = text.lstrip("/")
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

                markup_button = creat_listing_markup(data, 'amazon', page=1)

                send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
            else:
                msg = "The all of account sold out."
                # send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        elif cmd == 'deposit':
            html_show = create_html_deposit(0)
            markup_button = creat_deposit_markup()
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
        elif cmd == 'setpassword':
            print('==set password user==')
            user = User.objects.get(username=chat_id)
            new_password = text.split("/setpassword")[-1].strip()
            if len(new_password) <=3:
                msg = 'Your password must be longer that 3 characters'
                send_telegram_notify_to_group(
                    chat_id, msg=str(msg), reply_id=message_id)
                return
            else:
                # token, created = Token.objects.get_or_create(user=user)
                user.set_password(new_password)
                user.save()
                msg = '''Your password have been changed successfully.
    Username:%s
    Password:%s
                ''' % (chat_id, new_password)
                # send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
        # else:
        #     import math
        #     page_total = math.ceil(float(123) / 10)
        #     print('test page==',page_total)
        #     msg = "The system cannot recognize your command! please contact admin: "+cmd
        #     #send_message(msg, t_chat["id"])
        #     send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=message_id)


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

# if __name__ == '__main__':
#     # get_tbk_coupon('python')
#     print('===task===')
#     createCoinBaseAddress('ETH')
