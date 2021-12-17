import re, telebot
from celery import shared_task
from storagon import settings
from telebot import types
from servermain.models import User


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


def create_html_show(type,balance,total,page,total_page,updated):
    html_show = '''
<b>\U0001F47B MunBot %s accounts listing \U0001F47D</b>
<b>Balance: </b><code>$%s \U0001F4B3</code>
<b>Total: </b> <code>%s \U0001F6D2</code>
<pre>Displaying page %s of %s. Last updated @ %s</pre>
    ''' % (type,balance,total,page,total_page,updated)
    return html_show






@shared_task
def check_cmd_telegram(chat_id,message_id=None,text=None,callback_query=''):
    if callback_query:
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
        edit_telegram_notify_to_group(chat_id,message_id,callback_query,reply_markup=None)
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
        else:
            msg = "Hệ thống không thể nhận diện được câu lệnh của bạn! vui lòng liên hệ admin: "+cmd
            #send_message(msg, t_chat["id"])
            send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=message_id)


if __name__ == '__main__':
    # get_tbk_coupon('python')
    print('===task===')
