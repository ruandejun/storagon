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
def check_cmd_telegram(chat_id,t_message_id=None,text=None,callback_query=''):
    if callback_query:
        callback_split = callback_query.split('|')
        action = callback_split[0].strip()
        value = callback_split[1].strip()
        if action == 'success':
            msg = 'Bạn đã thêm telegram:%s vào tài khoản %s thành công!' % (chat_id,value)
            user_obj = User.objects.get(username=value)
            usertelegram_obj, created = UserTelegram.objects.get_or_create(telegram_id=chat_id,user=user_obj)

            send_telegram_notify_to_group(chat_id, msg=msg)
    else:
        list_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if not re.search(r'1688\.',text):
            get_taokouling = taokouling_extract(text)
            if get_taokouling:
                list_urls = get_taokouling
        if list_urls:
            for full_str in list_urls:
                msg = 'Xin lỗi sản phẩm của bạn không có chiết khấu vui lòng tìm sản phâm khác hoặc truy cập chietkhauviet.com để tìm kiếm sản phẩm!'

                referUrl_obj = get_commisstion_obj(full_str,telegram_id=chat_id)

                if referUrl_obj:
                    msg = '<a href="https://chietkhauviet.com/page/thong-tin-chiet-khau/%s">Giá sản phẩm:%s Chiết khấu:%s Phieu KM:%s</a>' % (
                        referUrl_obj.pk, float(referUrl_obj.zk_final_price) - float(referUrl_obj.coupon_amount), round(float(referUrl_obj.commission_price),2), referUrl_obj.coupon_amount)

                send_telegram_notify_to_group(chat_id, msg=msg,reply_id=t_message_id)

        else:
            cmd = text.lstrip("/")
            if cmd == "hello":
                msg = 'Chào bạn đến tới bot của công ty vân mã chuyên mua hộ và vận chuyển xuyên quốc tế!'
                send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=t_message_id)
            elif cmd.find("tk") == 0:
                username = cmd.split('tk')[-1].strip()
                user_objs = User.objects.filter(username=username)
                if user_objs.exists():
                    msg = "Bạn thêm telegram id: %s vào tài khoản: %s" % (chat_id, username)

                    reply_markup = create_markup('taikhoan', call_back_success='success|' + username,call_back_cancelled='cancelled|' + username)
                    send_telegram_notify_to_group(chat_id, msg=msg,reply_id=t_message_id, reply_markup=reply_markup)
                else:
                    msg = 'Không tìm thấy tài khoản bạn đã nhập, vui lòng nhập lại hoặc đăng ký tài khoản tại chietkhauviet.com!'
                    send_telegram_notify_to_group(chat_id, msg=msg)
            else:
                msg = "Hệ thống không thể nhận diện được câu lệnh của bạn! vui lòng liên hệ admin: "+cmd
                #send_message(msg, t_chat["id"])
                send_telegram_notify_to_group(chat_id, msg=str(msg),reply_id=t_message_id)


if __name__ == '__main__':
    # get_tbk_coupon('python')
    print('===task===')
