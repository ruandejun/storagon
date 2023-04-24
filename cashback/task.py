from cashback.models import payment_models, product_models
import datetime
import json, re, pytz, decimal
from django.conf import settings
import top.api, requests, aop
from http.cookiejar import CookieJar
from django.contrib.auth.models import User
from celery import shared_task
from django.db.models import Sum, F, Count, Q
from telegram_bot.task import send_telegram_notify_to_group


appkey = settings.TAOBAO_APPKEY
secret = settings.TAOBAO_SECRET
adzone_id = settings.TAOBAO_ADZONE_ID


APP_KEY_1688 = settings.APP_KEY_1688
APP_SECRET_1688 = settings.APP_SECRET_1688
ACCESS_TOKEN_1688 = settings.ACCESS_TOKEN_1688
MEDIAID_1688 = settings.MEDIAID_1688
MEDIAZONEID_1688 = settings.MEDIAZONEID_1688

@shared_task
def get_taobao_transaction():
    req = top.api.TbkOrderDetailsGetRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    time_range = 3
    time_limit = 3600
    list_id = []
    time = 0
    # while time <= time_limit:

    start_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(hours=24)).strftime(
        '%Y-%m-%d %H:%M:%S')
    end_time = (datetime.datetime.now().astimezone(pytz.timezone('Asia/Shanghai'))).strftime('%Y-%m-%d %H:%M:%S')
    print(appkey,end_time)
    print(start_time,end_time)
    # req.start_dsr = 10
    req.page_size = 200
    req.start_time = start_time
    req.end_time = end_time
    req.page_no = 1
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
    for line in data:
        print(line)
        for key in line.keys():
            if line[key] == '--':
                line[key] = None
        trade_id = line.get('trade_id')
        tran_taobao_objs = payment_models.TransactionTaobao.objects.filter(trade_id=trade_id)
        if tran_taobao_objs.exists():
            tran_taobao_objs.update(**line)
            continue
        if line['tk_status']  == 13:
            continue
        tran_taobao = payment_models.TransactionTaobao(**line)
        list_id.append(tran_taobao)


    print(len(list_id))
    if list_id:
        payment_models.TransactionTaobao.objects.bulk_create(list_id)
    else:
        print(payment_models.TransactionTaobao.objects.count())

    for line in payment_models.TransactionTaobao.objects.filter(commission_paid=0):

        time_check = (pytz.timezone.now() - datetime.timedelta(hours=3))
        referUrl_obj = product_models.ReferUrl.objects.filter(item_id=line.item_id, created__gte=time_check)
        account_holder = None
        if referUrl_obj.exists():
            customer_list = referUrl_obj.values_list('customer',flat=True)
            if customer_list.count() > 1:
                account_holder = None
                for line_cus in customer_list:
                    print(line_cus)
                    account_holder_objs = User.objects.filter(
                        Q(username=line_cus) | Q(telegram__telegram_id=line_cus)).distinct()
                    if not account_holder_objs.exists():
                        account_holder_recheck = None
                    else:
                        account_holder_recheck = account_holder_objs[0]

                    if hasattr(account_holder_recheck, 'telegram'):
                        print(account_holder_recheck.telegram.telegram_id)
                        trade_number = line.trade_parent_id.replace(line.trade_parent_id[5:len(line.trade_parent_id)-5],'xxxxxxxx')
                        print(trade_number, line.tradeAmount, line.commission_paid)
                        msg = '%s, %s, chiết khấu:%s Cần xác nhận, vui lòng xác nhận bằng /mdh mã đặt hàng' % (
                        trade_number, line.alipay_total_price, line.commission_paid)
                        print(msg)
                        send_telegram_notify_to_group(account_holder.telegram.telegram_id, msg=msg, bot_type='cashback')
            else:
                customer_refer = customer_list[0]
                account_holder_objs = User.objects.filter(Q(username=customer_refer) | Q(telegram__telegram_id=customer_refer)).distinct()
                if not account_holder_objs.exists():
                    account_holder = None
                else:
                    account_holder = account_holder_objs[0]


        line.commission_paid = decimal.Decimal('{0:.2f}'.format(line.pub_share_pre_fee * decimal.Decimal(0.8)))
        line.account_holder = account_holder
        line.save(update_fields=['commission_paid','account_holder'])
        if hasattr(account_holder, 'telegram'):
            print(account_holder.telegram.telegram_id)
            print(line.trade_parent_id,line.tradeAmount,line.commission_paid)
            msg = '%s, %s, chiết khấu:%s Đã thanh toán' % (line.trade_parent_id,line.alipay_total_price,line.commission_paid)
            print(msg)
            send_telegram_notify_to_group(account_holder.telegram.telegram_id, msg=msg, bot_type='cashback')


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
        print(resp)
        for line in resp['tradeBillList']:
            # print(line)
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
        account_holder_objs = User.objects.filter(Q(username=line.ext) | Q(telegram__telegram_id=line.ext)).distinct()
        if not account_holder_objs.exists():
            account_holder = None
        else:
            account_holder = account_holder_objs[0]
        line.commission_paid = decimal.Decimal('{0:.2f}'.format(line.commission * decimal.Decimal(0.55)))
        line.account_holder = account_holder
        line.save(update_fields=['commission_paid','account_holder'])
        if hasattr(account_holder, 'telegram'):
            print(account_holder.telegram.telegram_id)
            print(line.bizSubId,line.tradeAmount,line.commission_paid)
            msg = '%s, %s, chiết khấu:%s Đã thanh toán' % (line.bizId,line.tradeAmount,line.commission_paid)
            print(msg)
            send_telegram_notify_to_group(account_holder.telegram.telegram_id, msg=msg)


