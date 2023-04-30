from celery import shared_task
from storagon import settings
from cashback.models import payment_models, product_models, shop_models
import datetime
import json, re, pytz, decimal
# from django.conf import settings
import top.api, requests, aop
from http.cookiejar import CookieJar
from django.contrib.auth.models import User
from django.db.models import Sum, F, Count, Q
from telegram_bot.task import send_telegram_notify_to_group
from django.utils import timezone

appkey = settings.TAOBAO_APPKEY
secret = settings.TAOBAO_SECRET
adzone_id = settings.TAOBAO_ADZONE_ID


APP_KEY_1688 = settings.APP_KEY_1688
APP_SECRET_1688 = settings.APP_SECRET_1688
ACCESS_TOKEN_1688 = settings.ACCESS_TOKEN_1688
MEDIAID_1688 = settings.MEDIAID_1688
MEDIAZONEID_1688 = settings.MEDIAZONEID_1688


@shared_task
def get_taobao_transaction(start_time=None, end_time=None):

    req = top.api.TbkOrderDetailsGetRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    time_range = 3
    time_limit = 3600
    list_create_transaction = []
    time = 0
    # while time <= time_limit:
    if not start_time:
        start_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=3)).strftime(
        '%Y-%m-%d %H:%M:%S')
    if not end_time:
        end_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai'))).strftime('%Y-%m-%d %H:%M:%S')
    # print(appkey,end_time)
    print(start_time,end_time)
    # req.start_dsr = 10
    req.page_size = 200
    req.start_time = start_time
    req.end_time = end_time
    req.page_no = 1
    req.tk_status = None
    req.query_type = 4
    try:
        resp = req.getResponse()
    except:
        return
    print(resp)
    # result = json.loads(resp)
    results = resp['tbk_order_details_get_response']['data']['results']
    # print(results)
    time = time + time_range
    if 'publisher_order_dto' not in results:
        return
    else:
        data = results['publisher_order_dto']
    model_dict = {'adzone_id': 109959950065, 'adzone_name': 'chuyenhang365', 'alimama_rate': '10.00', 'alimama_share_fee': '0.26', 'alipay_total_price': '37.80', 'click_time': '2023-04-15 15:29:47', 'deposit_price': '0.00', 'flow_source': '--', 'income_rate': '7.00', 'is_lx': '0', 'item_category_name': '女装/女士精品', 'item_id': '0jtNUGt0BmS2t6-m80Wn0di7K7G7qOoUBg', 'item_img': '//img.alicdn.com/tfscom/i3/2820556330/O1CN01XAJ0ed1wdBvMkLPT9_!!2820556330.jpg', 'item_link': '//uland.taobao.com/item/edetail?id=0jtNUGt0BmS2t6-m80Wn0di7K7G7qOoUBg', 'item_num': 1, 'item_price': '128.00', 'item_title': '夏装2023年新款女装时尚刺绣纯棉衬衫女洋气全棉衬衣蕾丝拼接上衣', 'marketing_type': '', 'modified_time': '2023-04-26 17:32:30', 'order_type': '淘宝', 'pay_price': '37.80', 'pub_id': 859350174, 'pub_share_fee': '2.65', 'pub_share_pre_fee': '2.65', 'pub_share_rate': '100.00', 'refund_tag': 0, 'seller_nick': '韩都女装服饰馆', 'seller_shop_title': '韩都女装服饰馆', 'site_id': 1251850405, 'site_name': 'chuyenhang365', 'subsidy_fee': '0.00', 'subsidy_rate': '0.00', 'subsidy_type': '--', 'tb_deposit_time': '--', 'tb_paid_time': '2023-04-15 17:57:09', 'terminal_type': 'PC', 'tk_commission_fee_for_media_platform': '0.00', 'tk_commission_pre_fee_for_media_platform': '0.00', 'tk_commission_rate_for_media_platform': '0.00', 'tk_create_time': '2023-04-15 16:56:11', 'tk_deposit_time': '--', 'tk_earning_time': '2023-04-26 17:32:30', 'tk_order_role': 2, 'tk_paid_time': '2023-04-15 17:57:24', 'tk_status': 3, 'tk_total_rate': '7.00', 'total_commission_fee': '2.65', 'total_commission_rate': '7.00', 'trade_id': '3306979983228993420', 'trade_parent_id': '3306979983227993420'}   
    for line in data:
        print(line)
        list_key_remove = []
        for key in line.keys():
            if line[key] == '--':
                line[key] = None
            if key not in model_dict:
                # line.pop(key, None)
                list_key_remove.append(key)
        if list_key_remove:
            for line_remove in list_key_remove:
                line.pop(line_remove, None)
        trade_id = line.get('trade_id')

        ##create taobao transaction  
        tran_taobao_objs = payment_models.TransactionTaobao.objects.filter(trade_id=trade_id)
        if tran_taobao_objs.exists():
            tran_taobao_objs.update(**line)            
            tran_commission_objs = payment_models.TransactionCommission.objects.filter(reference=trade_id)
            if tran_commission_objs.exists():
                tran_commission_objs.update(status=line['tk_status'])

            continue
        if line['tk_status']  == 13:
            continue
        tran_taobao = payment_models.TransactionTaobao(**line)
        list_create_transaction.append(tran_taobao)
        


    print(len(list_create_transaction))
    if list_create_transaction:
        payment_models.TransactionTaobao.objects.bulk_create(list_create_transaction)
    else:
        print(payment_models.TransactionTaobao.objects.count())
        
    #find transactiontaobao not add commission and create conmmision
    for line in payment_models.TransactionTaobao.objects.filter(commission_paid=0):

        time_check = (datetime.datetime.now() - datetime.timedelta(hours=3))
        referUrl_obj = product_models.ReferUrl.objects.filter(item_id=line.item_id)
        account_holder = None
        if referUrl_obj.exists():
            customer_list = referUrl_obj.values_list('customer',flat=True)
            if customer_list.count() > 1:
                account_holder = None
                for line_cus in customer_list:
                    # print(line_cus)
                    account_holder_objs = User.objects.filter(
                        Q(username=line_cus) | Q(telegram__telegram_id=line_cus)).distinct()
                    if not account_holder_objs.exists():
                        account_holder_recheck = None
                    else:
                        account_holder_recheck = account_holder_objs[0]

                    if hasattr(account_holder_recheck, 'user_telegram'):
                        print(account_holder_recheck.user_telegram.telegram_id)
                        trade_number = line.trade_parent_id.replace(line.trade_parent_id[5:len(line.trade_parent_id)-5],'xxxxxxxx')
                        print(trade_number, line.tradeAmount, line.commission_paid)
                        msg = '%s, %s, chiết khấu:%s Cần xác nhận, vui lòng xác nhận bằng /mdh mã đặt hàng' % (
                        trade_number, line.alipay_total_price, line.commission_paid)
                        print(msg)
                        send_telegram_notify_to_group(account_holder.user_telegram.telegram_id, msg=msg, bot_type='cashback')
            else:
                customer_refer = customer_list[0]
                account_holder_objs = User.objects.filter(Q(username=customer_refer) | Q(user_telegram__telegram_id=customer_refer)).distinct()
                if not account_holder_objs.exists():
                    account_holder = None
                else:
                    account_holder = account_holder_objs[0]     
            
        ##create commission transaction
        tran_commission_objs = payment_models.TransactionCommission.objects.filter(reference=line.trade_id)
        if line.account_holder:
            balance_objs = payment_models.BalanceAccount.objects.filter(currency__value='CNY', account_holder=line.account_holder)
            if not balance_obj.exists():
                currency_obj, created = shop_models.Currency.objects.get_or_create(value='CNY', label='CNY')
                balance_obj = payment_models.BalanceAccount.objects.create(account_holder=line.account_holder, currency=currency_obj)
            else:
                balance_obj = balance_objs[0]
        else:
            balance_obj = None  
        if not tran_commission_objs.exists():
            print('===create new commission===')
            data_create = {}
            data_create['amount'] = decimal.Decimal('{0:.2f}'.format(line.pub_share_pre_fee))
            data_create['reference'] = line.trade_id
            data_create['commission_amount'] = decimal.Decimal('{0:.2f}'.format(line.pub_share_pre_fee * decimal.Decimal(0.65)))
            data_create['customer_ratio'] = decimal.Decimal(0.65)
            if line.tk_status  == 3:
                data_create['approved'] = line.tk_earning_time
            data_create['share_fee'] = line.alimama_share_fee
            data_create['status'] = line.tk_status
            commission_type_obj, created = payment_models.CommissionType.objects.get_or_create(value='taobao', label='taobao')
            tran_commission_obj = payment_models.TransactionCommission(**data_create)
            tran_commission_obj.transaction_holder = balance_obj
            tran_commission_obj.commission_type = commission_type_obj
            tran_commission_obj.save()
        else:
            tran_commission_obj = tran_commission_objs[0]
            if tran_commission_obj.status != line.tk_status:
                tran_commission_obj.status = line.tk_status
                tran_commission_obj.save(update_fields=['status'])
                
        line.commission_paid = decimal.Decimal('{0:.2f}'.format(line.pub_share_pre_fee * decimal.Decimal(0.65)))
        line.account_holder = account_holder
        line.transaction_commission = tran_commission_obj
        line.save(update_fields=['commission_paid','account_holder', 'transaction_commission'])                 
        ##send telegram notification
        if hasattr(account_holder, 'telegram'):
            print(account_holder.telegram.telegram_id)
            print(line.trade_parent_id,line.tradeAmount,line.commission_paid)
            msg = '%s, %s, chiết khấu:%s Đã thanh toán' % (line.trade_parent_id,line.alipay_total_price,line.commission_paid)
            # print(msg)
            send_telegram_notify_to_group(account_holder.user_telegram.telegram_id, msg=msg, bot_type='cashback')            
            
@shared_task
def get_1688_transaction():
    aop.set_default_server('gw.open.1688.com')

    aop.set_default_appinfo(APP_KEY_1688, APP_SECRET_1688)  # default

    start_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=3)).strftime(
        '%Y-%m-%d %H:%M:%S')
    end_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai'))).strftime(
        '%Y-%m-%d %H:%M:%S')

    # start_time = (timezone.now().date() - timedelta(30)).strftime("%Y-%m-%d")
    # end_time = timezone.now().date().strftime("%Y-%m-%d")
    print(start_time,end_time)
    req = aop.api.AlibabaCpsTradeBillListParam()
    req.access_token = ''
    req.queryOrderType = 'orderAll'
    req.orderState = 20
    req.queryTimeType = 'gmtCreateTime'
    req.queryStartTime = start_time
    req.queryEndTime = end_time
    req.pageNo = 1
    req.pageSize = 200
    resp = req.get_response(timeout=30)
    if 'totalRow' not in resp:
        return
    print(resp)
    totalrow = resp['totalRow']
    print(totalrow)
    lastPage = round(totalrow / 200, 0)
    # # payment_models.Transaction1688.objects.all().delete()
    list_id = []
    list_paid = []
    list_success = []
    i = 1
    while i <= int(lastPage):
        req.pageNo = i
        req.pageSize = 200
        resp = req.get_response(timeout=30)
        # print(resp)
        for line in resp['tradeBillList']:
            print(line)
            # print(line['orderState'])
            if not line['ext'] or line['orderState'] == 10 or line['orderState'] == 80:
                continue

            tran_1688_objs = payment_models.Transaction1688.objects.filter(bizSubId=line['bizSubId'])
            if tran_1688_objs.exists():
                if tran_1688_objs.first().orderState != line['orderState']:
                    if line['orderState'] == 20:
                        list_paid.append(tran_1688_objs.first().pk)
                    elif line['orderState'] == 50:
                        list_success.append(tran_1688_objs.first().pk)
                    print('===', tran_1688_objs.first().orderState, line['orderState'])
                    tran_1688_objs.update(**line)
                    tran_commission_objs = payment_models.TransactionCommission.objects.filter(reference=line['bizSubId'])
                    if tran_commission_objs.exists():
                        tran_commission_objs.update(status=line['orderState'])                    
                continue
            referUrl_obj = product_models.ReferUrl.objects.filter(Q(telegram_id=line['ext']) | Q(customer=line['ext']),
                                                                  item_id=line['feedId']).distinct()
            if not referUrl_obj.exists():
                continue
            print(line, referUrl_obj.count())
            tran_1688 = payment_models.Transaction1688(**line)
            list_id.append(tran_1688)
        i+=1

    print(len(list_id))
    if list_id:
        payment_models.Transaction1688.objects.bulk_create(list_id)
    else:
        print(payment_models.Transaction1688.objects.count())

    for line in payment_models.Transaction1688.objects.filter(commission_paid=0):
        account_holder_objs = User.objects.filter(Q(username=line.ext) | Q(user_telegram__telegram_id=line.ext)).distinct()
        if not account_holder_objs.exists():
            account_holder = None
        else:
            account_holder = account_holder_objs[0]
            
        ##create commission transaction
        tran_commission_objs = payment_models.TransactionCommission.objects.filter(reference=line.bizId)
        if line.account_holder:
            balance_objs = payment_models.BalanceAccount.objects.filter(currency__value='CNY', account_holder=line.account_holder)
            if not balance_obj.exists():
                currency_obj, created = shop_models.Currency.objects.get_or_create(value='CNY', label='CNY')
                balance_obj = payment_models.BalanceAccount.objects.create(account_holder=line.account_holder, currency=currency_obj)
            else:
                balance_obj = balance_objs[0]
        else:
            balance_obj = None  
        if not tran_commission_objs.exists():
            print('===create new commission===')
            data_create = {}
            data_create['amount'] = decimal.Decimal('{0:.2f}'.format(line.commission))
            data_create['reference'] = line.bizSubId
            data_create['commission_amount'] = decimal.Decimal('{0:.2f}'.format(line.commission * decimal.Decimal(0.55)))
            data_create['customer_ratio'] = decimal.Decimal(0.55)
            # if line['tk_status']  == 3:
                # data_create['approved'] = line['tk_earning_time']
            # data_create['share_fee'] = line['alimama_share_fee']
            # data_create['status'] = line['tk_status']
            commission_type_obj, created = payment_models.CommissionType.objects.get_or_create(value='1688', label='1688')
            tran_commission_obj = payment_models.TransactionCommission(**data_create)
            tran_commission_obj.transaction_holder = balance_obj
            tran_commission_obj.commission_type = commission_type_obj
            tran_commission_obj.save()
        else:
            tran_commission_obj = tran_commission_objs[0]
            if tran_commission_obj.status != line['orderState']:
                tran_commission_obj.status = line['orderState']
                tran_commission_obj.save(update_fields=['status'])
                            
        line.commission_paid = decimal.Decimal('{0:.2f}'.format(line.commission * decimal.Decimal(0.55)))
        line.account_holder = account_holder
        line.save(update_fields=['commission_paid','account_holder'])
        if hasattr(account_holder, 'user_telegram'):
            print(account_holder.user_telegram.telegram_id)
            print(line.bizSubId,line.tradeAmount,line.commission_paid)
            msg = '%s, %s, chiết khấu:%s Đã thanh toán' % (line.bizId,line.tradeAmount,line.commission_paid)
            print(msg)
            send_telegram_notify_to_group(account_holder.user_telegram.telegram_id, msg=msg)


def get_all_taobao_transaction():
    current_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai'))).strftime('%Y-%m-%d %H:%M:%S')
    time_range = 3
    time_limit = 2160
    list_id = []
    time = 0
    while time <= time_limit:
        end_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=time)).strftime(
        '%Y-%m-%d %H:%M:%S')
        
        time+=time_range
        
        start_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=time)).strftime(
        '%Y-%m-%d %H:%M:%S')
        get_taobao_transaction(start_time=start_time, end_time=end_time)
        
    # if not start_time:
    #     start_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=3)).strftime(
    #     '%Y-%m-%d %H:%M:%S')
    # if not end_time:
    #     end_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai'))).strftime('%Y-%m-%d %H:%M:%S')