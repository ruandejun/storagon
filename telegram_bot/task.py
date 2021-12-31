import re, telebot
from celery import shared_task
from storagon import settings
from telebot import types
# from servermain.models import User


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

def create_html_deposit_details(balance, address, account_id):
    html_show = '''
<b>\U0001F47B MunBot automatic buying accounts \U0001F47D</b>
<b>Balance: </b><code>$%s \U0001F4B3</code>
Here is the details:-
Send crypto to the address shown below .
<a href="https://chart.googleapis.com/chart?chs=200x200&chld=%s&cht=qr&%s"></a>

Address: %s
Charge ID: %s

1. Funds will be automatic convert to USD by your balance.
2. Funds will be added after 2 confirmations.
    ''' % (balance,'L%7C2',address,address, account_id)
    return html_show

@shared_task
def check_cmd_telegram(chat_id,message_id=None,text=None,callback_query=''):
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
                print('==deposit==', value)
                html_show = create_html_deposit_details(0,'0xb83180d174Cde70dd5D9234078475Ba96A144b21','c25f8b11-31c4-5fd6-9ea0-dde56a0a6595')
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
            html_show = create_html_show('amazon', 0, 127831270, 1, 12783127, '2021-11-25 21:02')
            listing = [{'id': 12312, 'account': 'a*****@hotmail.com', 'price': 12.43},
                       {'id': 12341, 'account': 'b****@gmail.com', 'price': 11.55},
                       {'id': 12341, 'account': 'c***@gmail.com', 'price': 12.55}]
            markup_button = creat_listing_markup(listing, 'amazon', page=1)

            send_telegram_notify_to_group(chat_id, msg=html_show,reply_id=message_id, reply_markup=markup_button)
        elif cmd == 'deposit':
            html_show = create_html_deposit(0)
            markup_button = creat_deposit_markup()
            send_telegram_notify_to_group(chat_id, msg=html_show, reply_id=message_id, reply_markup=markup_button)
        else:
            msg = "Hệ thống không thể nhận diện được câu lệnh của bạn! vui lòng liên hệ admin: "+cmd
            #send_message(msg, t_chat["id"])
            send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=message_id)



def createCoinBase(name="BTC"):
    print('==Create Coin Base==')
    from coinbase.wallet.client import Client
    import json
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
    # user = client.get_current_user()
    # user_as_json_string = json.dumps(user)
    # print(user_as_json_string)
    # accounts = client.get_accounts(limit=200)
    # cdict for cdict in my_list if cdict["task"] == 'key'
    # print(accounts.data)
    # for data in accounts.data:
    #     if data.currency == 'ETH':
    #         print(data.id)
        # print('==',data.currency == 'LTC')
    # assert isinstance(accounts.data, list)
    # assert accounts[0] is accounts.data[0]
    # assert len(accounts[::]) == len(accounts.data)
    # account = client.get_primary_account()
    # accountAddress = account.get_addresses()
    # print(accountAddress.data)
    # client.create_checkout()
    # account = client.get_address(account_id,'c25f8b11-31c4-5fd6-9ea0-dde56a0a6595')
    # print(account)
    created = client.create_address(account_id)
    print('created',created)
    return created
    # accountAddress = account.get_addresses()
    # # print(account)
    # print(len(accountAddress.data))
if __name__ == '__main__':
    # get_tbk_coupon('python')
    print('===task===')
    createCoinBase('ETH')
