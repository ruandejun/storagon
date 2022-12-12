from ensurepip import version
import re, telebot
from celery import shared_task
from storagon import settings
from telebot import types
from servermain.models import AccountBalance, AccountCurrency
from django.contrib.auth.models import User
from telegram_bot.models import AccountsData, MunAnti, UserTelegram, AccountsSelling, BrowserProfiles
from storagon.enum import *
from servermain.controllers import UserController
from telegram_bot.api.TelegramBot_RestfulApi import AccountsSellingSerializer
from rest_framework.authtoken.models import Token
import random
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
        
        cmd = text.lstrip("/").strip()
        extra_text = ''
        if cmd.find(' ') != -1:
            new_cmd = cmd.split(' ')[0]
            extra_text = cmd.split(' ')[1]
            cmd = new_cmd.strip()
            
        print('cmd==', cmd, text)
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
        elif cmd == 'setversion':
            print('==set version==')
            if str(chat_id) == '892844098':
                mun_obj = MunAnti.objects.create(version=extra_text.strip())
                msg = 'New version %s already updated!' % (extra_text)
                send_telegram_notify_to_group(chat_id, msg=str(msg), reply_id=message_id)
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
# if __name__ == '__main__':
#     # get_tbk_coupon('python')
#     print('===task===')
#     createCoinBaseAddress('ETH')

def fix_font_and_rects():
    list_obj = BrowserProfiles.objects.all()
    for line_obj in line_obj:
        if line_obj.profile_rects == 'Noise':
            line_obj.profile_rects = str(round(random.uniform(0.2, 0.35), 5))
        if line_obj.profile_font == 'Noise':
            listFonts = ['Arial', 'Calibri', 'Cambria', 'Cambria Math', 'Candara', 'Comic Sans MS', 'Comic Sans MS Bold', 'Comic Sans', 'Consolas', 'Constantia', 'Corbel', 'Courier New', 'Caurier Regular', 'Ebrima', 'Fixedsys Regular', 'Franklin Gothic', 'Gabriola Regular', 'Gadugi', 'Georgia', 'HoloLens MDL2 Assets Regular', 'Impact Regular', 'Javanese Text Regular', 'Leelawadee UI', 'Lucida Console Regular', 'Lucida Sans Unicode Regular', 'Malgun Gothic', 'Microsoft Himalaya Regular', 'Microsoft JhengHei', 'Microsoft JhengHei UI', 'Microsoft PhangsPa', 'Microsoft Sans Serif Regular', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft YaHei UI', 'Microsoft Yi Baiti Regular', 'MingLiU_HKSCS-ExtB Regular', 'MingLiu-ExtB Regular', 'Modern Regular', 'Mongolia Baiti Regular', 'MS Gothic Regular', 'MS PGothic Regular', 'MS Sans Serif Regular', 'MS Serif Regular', 'MS UI Gothic Regular', 'MV Boli Regular', 'Myanmar Text', 'Nimarla UI', 'Myanmar Tet', 'Nirmala UI', 'NSimSun Regular', 'Palatino Linotype', 'PMingLiU-ExtB Regular', 'Roman Regular', 'Script Regular', 'Segoe MDL2 Assets Regular', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Emoji Regular', 'Segoe UI Historic Regular', 'Segoe UI Symbol Regular', 'SimSun Regular', 'SimSun-ExtB Regular', 'Sitka Banner', 'Sitka Display', 'Sitka Heading', 'Sitka Small', 'Sitka Subheading', 'Sitka Text', 'Small Fonts Regular', 'Sylfaen Regular', 'Symbol Regular', 'System Bold', 'Tahoma', 'Terminal', 'Times New Roman', 'Trebuchet MS', 'Verdana', 'Webdings Regular', 'Wingdings Regular', 'Yu Gothic', 'Yu Gothic UI', 'Arial Black', 'Calibri Light', 'Courier', 'Fixedsys', 'Franklin Gothic Medium', 'Gabriola', 'HoloLens MDL2 Assets', 'Impact', 'Javanese Text', 'Leelawadee UI Semilight', 'Lucida Console', 'Lucida Sans Unicode', 'MS Gothic', 'MS PGothic', 'MS Sans Serif', 'MS Serif', 'MS UI Gothic', 'MV Boli', 'Malgun Gothic Semilight', 'Marlett', 'Microsoft Himalaya', 'Microsoft JhengHei Light', 'Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft YaHei Light', 'Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', 'MingLiU_HKSCS-ExtB', 'Modern', 'Mongolian Baiti', 'NSimSun', 'Nirmala UI Semilight', 'PMingLiU-ExtB', 'Roman', 'Script', 'Segoe MDL2 Assets', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'SimSun', 'SimSun-ExtB', 'Small Fonts', 'Sylfaen', 'Symbol', 'System', 'Webdings', 'Wingdings', 'Yu Gothic Light', 'Yu Gothic Medium', 'Yu Gothic UI Light', 'Yu Gothic UI Semibold', 'Yu Gothic UI Semilight', 'Arial Narrow', 'Arial Unicode MS', 'Book Antiqua', 'Bookman Old Style', 'Century', 'Century Gothic', 'Century Schoolbook', 'Garamond', 'Helvetica', 'Lucida Bright', 'Lucida Calligraphy', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Monotype Corsiva', 'MS Outlook', 'MS Reference Sans Serif', 'Times', 'Wingdings 2', 'Wingdings 3', 'default', 'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'inherit', 'auto', 'Brush Script MT', 'Broadway', 'Bell MT', 'Berlin Sans FB', 'Blackadder ITC', 'Curlz MT', 'Elephant', 'Engravers MT', 'Goudy Old Style', 'Minion Pro', 'Papyrus', 'Wide Latin', 'Snap ITC', 'Stencil', 'Old English Text MT', 'Ubuntu', 'Ubuntu Mono', 'Terminus Font', 'Terminus', 'Ubuntu Mono 13', 'Ubuntu Mono Regular', 'Apple Braille Outline 6 Dot', 'Apple Braille Outline 8 Dot', 'Apple Braille Pinpoint 6 Dot', 'Apple Braille Pinpoint 8 Dot', 'Apple Braille', 'Apple Symbols', 'AppleGothic', 'AquaKana', 'Geeza Pro Bold', 'Geeza Pro', 'Geneva', 'HelveLTMM', 'Helvetica LT MM', 'HelveticaNeue', 'Hiragino Kaku Gothic ProN W3', 'Hiragino Kaku Gothic ProN W6', 'Hiragino Mincho ProN W3', 'Hiragino Mincho ProN W6', 'Keyboard', 'LastResort', 'LiHei Pro', 'LucidaGrande', 'Menlo', 'Monaco', 'STHeiti', 'STHeiti Light', 'STXihei', 'Thonburi', 'ThonburiBold', 'Times LT MM', 'TimesLTMM', 'ZapfDingbats', 'AmericanTypewriter', 'Andale Mono', 'Apple Chancery', 'Apple LiGothic Medium', 'Arial Bold Italic', 'Arial Bold', 'Arial Italic', 'Arial Narrow Bold Italic', 'Arial Narrow Bold', 'Arial Narrow Italic', 'Arial Rounded Bold', 'Arial Unicode', 'Baskerville', 'BigCaslon', 'Brush Script', 'Chalkboard', 'Chalkduster', 'Cochin', 'Copperplate', 'Courier New Bold Italic', 'Courier New Bold', 'Courier New Italic', 'Didot', 'Futura', 'Georgia Bold Italic', 'Georgia Bold', 'Georgia Italic', 'GillSans', 'Hei', 'Herculanum', 'Hiragino Kaku Gothic Pro W3', 'Hiragino Kaku Gothic Pro W6', 'Hiragino Kaku Gothic Std W8', 'Hiragino Kaku Gothic StdN W8', 'Hiragino Maru Gothic Pro W4', 'Hiragino Maru Gothic ProN W4', 'Hiragino Mincho Pro W3', 'Hiragino Mincho Pro W6', 'Hoefler Text', 'Hoefler Text Ornaments', 'Kai', 'MarkerFelt', 'Optima', 'Osaka', 'OsakaMono', 'Skia', 'Tahoma Bold', 'Times New Roman Bold Italic', 'Times New Roman Bold', 'Times New Roman Italic', 'Trebuchet MS Bold Italic', 'Trebuchet MS Bold', 'Trebuchet MS Italic', 'Verdana Bold Italic', 'Verdana Bold', 'Verdana Italic', 'Zapfino', 'Aharoni Bold', 'Andalus Regular', 'Angsana New', 'Angsana New Bold', 'Angsana New Italic', 'Angsana New Bold Italic', 'AngsanaUPC', 'AngsanaUPC Bold', 'AngsanaUPC Italic', 'AngsanaUPC Bold Italic', 'Aparajita', 'Aparajita Bold', 'Aparajita Italic', 'Aparajita Bold Italic', 'Arabic Typesetting Regular', 'Arial Unicode MS Regular', 'Batang', 'BatangChe', 'Browallia New', 'Browallia New Bold', 'Browallia New Italic', 'Browallia New Bold Italic', 'BrowalliaUPC', 'BrowalliaUPC Bold', 'BrowalliaUPC Italic', 'BrowalliaUPC Bold Italic', 'Calibri Bold', 'Calibri Italic', 'Calibri Bold Italic', 'Cambria Bold', 'Cambria Italic', 'Cambria Bold Italic', 'Candara Bold', 'Candara Italic', 'Candara Bold Italic', 'Consolas Bold', 'Consolas Italic', 'Consolas Bold Italic', 'Constantia Bold', 'Constantia Italic', 'Constantia Bold Italic', 'Corbel Bold', 'Corbel Italic', 'Corbel Bold Italic', 'Cordia New', 'Cordia New Bold', 'Cordia New Italic', 'Cordia New Bold Italic', 'CordiaUPC', 'CordiaUPC Bold', 'CordiaUPC Italic', 'CordiaUPC Bold Italic', 'DFKai-SB', 'DaunPenh', 'David', 'David Bold', 'DilleniaUPC', 'DilleniaUPC Bold', 'DilleniaUPC Italic', 'DilleniaUPC Bold Italic', 'DokChampa', 'Dotum', 'DotumChe', 'Ebrima Bold', 'Estrangelo Edessa', 'EucrosiaUPC', 'EucrosiaUPC Bold', 'EucrosiaUPC Italic', 'EucrosiaUPC Bold Italic', 'Euphemia', 'FangSong', 'FrankRuehl', 'Franklin Gothic Medium Italic', 'FreesiaUPC', 'FreesiaUPC Bold', 'FreesiaUPC Italic', 'FreesiaUPC Bold Italic', 'Gautami', 'Gautami Bold', '& Georgia Bold Italic', 'Gisha', 'Gisha Bold', 'Gulim', 'GulimChe', 'Gungsuh', 'GungsuhChe', 'IrisUPC', 'IrisUPC Bold', 'IrisUPC Italic', 'IrisUPC Bold Italic', 'Iskoola Pota', 'IskoolaPota Bold', 'JasmineUPC', 'JasmineUPC Bold', 'JasmineUPC Italic', 'JasmineUPC Bold Italic', 'KaiTi', 'Kalinga', 'Kalinga Bold', 'Kartika', 'Kartika Bold', 'Khmer UI', 'Khmer UI Bold', 'KodchiangUPC', 'KodchiangUPC Bold', 'KodchiangUPC Italic', 'KodchiangUPC Bold Italic', 'Kokila', 'Kokila Bold', 'Kokila Italic', 'Kokila Bold Italic', 'Lao UI', 'Lao UI Bold', 'Latha', 'Latha Bold', 'Leelawadee', 'Leelawadee Bold', 'Levenim MT', 'Levenim MT Bold', 'LilyUPC', 'LilyUPC Bold', 'LilyUPC Italic', 'LilyUPC Bold Italic', 'MS Mincho', 'MS PMincho', 'Malgun Gothic Bold', 'Mangal', 'Mangal Bold', 'Meiryo UI', 'Meiryo UI Bold', 'Meiryo UI Italic', 'Meiryo UI Bold Italic', 'Meiryo', 'Meiryo Bold', 'Meiryo Italic', 'Meiryo Bold Italic', 'Microsoft JhengHei Bold', 'Microsoft New Tai Lue Bold', 'Microsoft PhagsPa Bold', 'Microsoft Tai Le Bold', 'Microsoft Uighur', 'Microsoft YaHei Bold', 'MingLiU', 'MingLiU_HKSCS', 'Miriam', 'Miriam Fixed', 'MoolBoran', 'Narkisim', 'Nyala', 'PMingLiU', 'Palatino Linotype Bold', 'Palatino Linotype Italic', 'Palatino Linotype Bold Italic', 'Plantagenet Cherokee', 'Raavi', 'Raavi Bold', 'Rod', 'Sakkal Majalla', 'Sakkal Majalla Bold', 'Segoe Print Bold', 'Segoe Script Bold', 'Segoe UI Bold', 'Segoe UI Italic', 'Segoe UI Bold Italic', 'Shonar Bangla', 'Shonar Bangla Bold', 'Shruti', 'Shruti Bold', 'SimHei', 'Simplified Arabic', 'Simplified Arabic Bold', 'Simplified Arabic Fixed', ' Times New Roman Bold', 'Traditional Arabic', 'Traditional Arabic Bold', 'Tunga', 'Tunga Bold', 'Utsaah', 'Utsaah Bold', 'Utsaah Italic', 'Utsaah Bold Italic', 'Vani', 'Vani Bold', 'Vijaya', 'Vijaya Bold', 'Vrinda', 'Vrinda Bold']
            fonts_max = random.randint(200, len(listFonts)-1)
            fonts_min = random.randint(0, 150)
            listUse = listFonts[fonts_min:fonts_max]  
            line_obj.profile_font = str(listUse)
        line_obj.save()