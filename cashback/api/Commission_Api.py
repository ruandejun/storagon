import json, decimal, re, os, logging, datetime
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from cashback.models import  payment_models, shop_models, product_models
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.db.models import Sum, F, Count, Q, FloatField, DecimalField, ExpressionWrapper
from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from cashback.api.Serializer import TransactionCommissionSerializer,Transaction1688Serializer,TransactionTaobaoSerializer
import top.api, requests
from http.cookiejar import CookieJar
from cashback.api.Alibaba1688Api import *
from cashback.api.TaobaoApi import *
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from storagon.enum import *
from storagon.decorator import banned_check, login_required_ajax, signature_test
from django.contrib.auth.decorators import user_passes_test

def get_groups(user,request):
    # from ipware import get_client_ip
    # ip, is_routable = get_client_ip(request)
    groups = []
    if request.user.is_authenticated:
        # company_ip = SystemConfigureController.getConfigure('company_ip')
        # if company_ip.find(ip) != -1 or user.profile.administrator:
        list_group = user.groups.all()

        for line_group in list_group:
            groups.append(line_group.name)
    return groups

def detect_url_commission(url):
    if not re.search(r'1688\.', url):
        get_taokouling = taokouling_extract(url)
        if get_taokouling:
            url = get_taokouling[0]
            return url
    if re.search('s\.click\.', url):
        new_link = sclick_extract(url)
        print('new_link', new_link)
        if new_link:
            full_str = new_link
            return full_str
    if re.search(r'qr\.1688', url):
        new_link = alibaba_1688_extract(url)
        print('new_link', new_link)
        if new_link:
            full_str = new_link
            return full_str
    if re.search('tb\.cn', url):
        new_link = tbcn_extract(url)
        if new_link:
            full_str = new_link
            return full_str
    if re.search('taobao\.|tmall\.', url):
        return url
    if re.search('1688\.com', url):
        return url

def get_commission_obj(full_str,telegram_id=None,wechat_id=None,zalo_id=None,username=None):
    data_item = {}
    data_1688 = {}
    data = {}
    ext_1688 = ''
    if telegram_id:
        data['telegram_id'] = telegram_id
        ext_1688 = telegram_id
    if wechat_id:
        data['wechat_id'] = wechat_id
        ext_1688 = wechat_id
    if zalo_id:
        data['zalo_id'] = zalo_id
        ext_1688 = zalo_id
    if username:
        data['customer'] = username
        ext_1688 = username
    print(full_str)
    if re.search('s\.click\.', full_str):
        new_link = sclick_extract(full_str)
        print('new_link', new_link)
        if new_link:
            full_str = new_link
    if re.search(r'qr\.1688', full_str):
        new_link = alibaba_1688_extract(full_str)
        print('new_link', new_link)
        if new_link:
            full_str = new_link
    if re.search('tb\.cn', full_str):
        new_link = tbcn_extract(full_str)
        if new_link:
            full_str = new_link

    if re.search('taobao\.|tmall\.', full_str):

        data_item = get_taobao_commission(full_str, ext_1688)
        # msg = data_item
    elif re.search('1688\.com', full_str):
        link_re = re.search('offer\/(\d+)\.html', full_str)
        if link_re:
            offer_id = link_re.group(1).strip()
            one_week = datetime.date.today() - datetime.timedelta(days=1)
            referUrl_objs = product_models.ReferUrl.objects.filter(Q(telegram_id=ext_1688) | Q(customer=ext_1688),item_id=offer_id, created__gte=one_week)
            if referUrl_objs.exists():
                return referUrl_objs.first()
            data_1688 = get_1688_commission(full_str,ext_1688)
        # msg = link_1688
    if data_item:
        data['commission_rate'] = data_item['commission_rate']
        if 'coupon_amount' in data_item:
            data['coupon_amount'] = data_item['coupon_amount']
        if 'coupon_end_time' in data_item:
            data['coupon_end_time'] = data_item['coupon_end_time']
        if 'coupon_id' in data_item:
            data['coupon_id'] = data_item['coupon_id']
        if 'coupon_info' in data_item:
            data['coupon_info'] = data_item['coupon_info']
        if 'coupon_remain_count' in data_item:
            data['coupon_remain_count'] = data_item['coupon_remain_count']
        if 'coupon_share_url' in data_item:
            data['coupon_share_url'] = data_item['coupon_share_url']
        if 'coupon_start_time' in data_item:
            data['coupon_start_time'] = data_item['coupon_start_time']
        if 'coupon_total_count' in data_item:
            data['coupon_total_count'] = data_item['coupon_total_count']
        if 'item_description' in data_item:
            data['item_description'] = data_item['item_description']
        data['customer'] = ext_1688
        data['item_id'] = data_item['item_id']
        data['item_url'] = data_item['item_url']
        data['nick'] = data_item['nick']
        data['pict_url'] = data_item['pict_url']
        data['real_post_fee'] = data_item['real_post_fee']
        data['reserve_price'] = data_item['reserve_price']
        data['seller_id'] = data_item['seller_id']
        data['shop_title'] = data_item['shop_title']
        data['short_title'] = data_item['short_title']
        data['tk_total_commi'] = data_item['tk_total_commi']
        data['tk_total_sales'] = data_item['tk_total_sales']
        data['url'] = data_item['url']
        data['volume'] = data_item['volume']
        data['x_id'] = data_item['x_id']
        data['zk_final_price'] = data_item['zk_final_price']
        if 'coupon_amount' in data:
            commission_price_org = (float(data['zk_final_price']) - float(data['coupon_amount'])) * (float(data['commission_rate']) / float(10000))
            commission_price = round(commission_price_org - (commission_price_org * float(0.35)), 2)
        else:
            commission_price_org = float(data['zk_final_price']) * (float(data['commission_rate']) / float(10000))

            commission_price = round(commission_price_org - (commission_price_org * float(0.35)), 2)
        print('commission_price_org',commission_price_org)
        print('===',commission_price)
        data['commission_price'] = decimal.Decimal(round(commission_price, 2))
        referUrl_obj = product_models.ReferUrl.objects.create(**data)

        print(data_item)

        print(referUrl_obj.url)

        if referUrl_obj.coupon_share_url:
            tkl_create = generate_ttoken('https:' + referUrl_obj.coupon_share_url, 'chietkhauviet.com')
        else:
            tkl_create = generate_ttoken('https:' + referUrl_obj.url, 'chietkhauviet.com')
        if tkl_create:
            referUrl_obj.taokouling = tkl_create
            referUrl_obj.save(update_fields=["taokouling"])
        return referUrl_obj

    if data_1688:
        item_info = data_1688['item_info'][0]
        link_commissions = data_1688['link_commissions']['result'][0]
        data['customer'] = ext_1688
        data['coupon_share_url'] = link_commissions['shortClickUrl']
        data['item_url'] = 'https://detail.1688.com/offer/%s.html' % (item_info['offerId'])
        data['commission_rate'] = item_info['ratio']
        data['item_id'] = item_info['offerId']
        data['pict_url'] = item_info['imgUrl']
        data['seller_id'] = item_info['sellerId']
        data['short_title'] = item_info['title']
        data['zk_final_price'] = item_info['price']
        data['item_description'] = link_commissions['searchCode']
        data['taokouling'] = link_commissions['alipayUrl']
        data['url'] = link_commissions['shortClickUrl']
        data['short_url'] = link_commissions['shortClickUrl']
        commission_price = float(data['zk_final_price']) * float(data['commission_rate'])
        commission_price = round(commission_price - (commission_price * float(0.45)), 2)
        data['commission_price'] = decimal.Decimal(round(commission_price, 2))
        referUrl_obj = product_models.ReferUrl.objects.create(**data)

        return referUrl_obj
    

@api_view(['GET','POST','PUT'])
def thong_tin_chiet_khau(request,commission_id):
    template = 'new_index/commission.html'
    referUrl_objs = product_models.ReferUrl.objects.filter(pk=commission_id)
    if referUrl_objs.exists():
        referUrl = referUrl_objs.first()
    else:
        referUrl = None
    context = {'commission':referUrl}
    return render(request, template, context)
class CustomSchemeRedirect(HttpResponseRedirect):
    allowed_schemes = ['taobao','wireless1688', 'https']
    # allowed_schemes = ['1688']
def get_link_pc(request):
    refer_id = request.GET.get('id')
    refer_obj = product_models.ReferUrl.objects.get(pk=refer_id)
    if refer_obj.coupon_share_url:
        link_redirect = refer_obj.coupon_share_url
    else:
        link_redirect = refer_obj.url
    link_redirect = link_redirect.replace('https://','//')    
    # if link_redirect.find('taobao') != -1:
    #     prefix = 'taobao'
    # else:
    #     prefix = '1688'
    return CustomSchemeRedirect('https:'+link_redirect)
def get_link_mobile(request):
    refer_id = request.GET.get('id')
    refer_obj = product_models.ReferUrl.objects.get(pk=refer_id)
    if refer_obj.coupon_share_url:
        link_redirect = refer_obj.coupon_share_url
    else:
        link_redirect = refer_obj.url
    link_redirect = link_redirect.replace('https://','//')
    if link_redirect.find('taobao') != -1:
        prefix = 'taobao'
    else:
        prefix = 'wireless1688'
    print('====',prefix+':'+link_redirect)    
    return CustomSchemeRedirect(prefix+':'+link_redirect)
    # status = {}
    # return Response(status, status=HTTP_200_OK)


@api_view(['POST'])
def get_commission(request):

    if request.user.is_authenticated:
        username = request.user.username
    else:
        if not request.session.session_key:
            request.session.save()
        username = request.session.session_key
    status = {'success': False, 'msg': "kiem tra lai thong tin"}
    list_currencies, created = shop_models.Currency.objects.get_or_create(code='CNY', label='CNY')
    exchange_rate = list_currencies.exchange_rate
    html = {"user":None,"config":{"exchange_rate":exchange_rate,"service_cost_1688":"12","service_cost_taobao":"10","service_cost_tmall":"10"}}
    status['config'] = html
    url = request.POST.get('key','')
    if url:
        if not re.search(r'1688\.', url):
            get_taokouling = taokouling_extract(url)
            if get_taokouling:
                url = get_taokouling[0]
        commission_obj = get_commission_obj(url,username=username)
        if commission_obj:
            status['success'] = True
            status['short_title'] = commission_obj.short_title
            status['pict_url'] = commission_obj.pict_url
            status['url'] = commission_obj.url
            status['taokouling'] = commission_obj.taokouling
            status['zk_final_price'] = commission_obj.zk_final_price
            status['commission_price'] = commission_obj.commission_price
            status['msg'] = 'Đã tìm thấy sản phẩm của bạn!'
        else:
            status['msg'] = 'Sản phẩm của bạn không có chiết khấu vui lòng chọn sản phẩm khác!'
    return Response(status, status=HTTP_200_OK)

@api_view(['GET','POST','PUT'])
def get_list_1688_order_commission(request):
    groups = get_groups(request.user,request)
    # currency_obj = shop_models.Currency.objects.get(code='CNY')
    # balance_account_obj = payment_models.BalanceAccount.objects.get_or_create(account_holder=request.user,currency=currency_obj)
    if not groups:
        tran_commission_objs = payment_models.Transaction1688.objects.filter(account_holder=request.user).order_by('-created')
    else:
        tran_commission_objs = payment_models.Transaction1688.objects.all().order_by('-created')
    my_search = request.GET.get('search')
    if my_search:
        tran_commission_objs = tran_commission_objs.filter(Q(id__icontains=my_search) | Q(
            bizId__icontains=my_search) | Q(
            bizSubId__icontains=my_search) ).order_by('-created')

    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])

    count = tran_commission_objs.count()
    list_get = tran_commission_objs[offset:offset+limit]

    data = Transaction1688Serializer(list_get, many=True).data

    data_table = {'total': count, 'rows': data}
    return Response(data_table, status=HTTP_200_OK)

@api_view(['GET','POST','PUT'])
def get_1688_commission_statistics(request):
    groups = get_groups(request.user,request)
    # currency_obj = shop_models.Currency.objects.get(code='CNY')
    # balance_account_obj = payment_models.BalanceAccount.objects.get_or_create(account_holder=request.user,currency=currency_obj)

    username = request.POST.get('username',None)
    if not groups:
        tran_commission_objs = payment_models.Transaction1688.objects.filter(account_holder=request.user)
    elif username:
        tran_commission_objs = payment_models.Transaction1688.objects.filter(account_holder__username=username)
    else:
        tran_commission_objs = payment_models.Transaction1688.objects.all()

    tran_commission_objs_paid = tran_commission_objs.filter(orderState=20)
    tran_commission_objs_completed = tran_commission_objs.filter(orderState=50)

    commission_statistics = tran_commission_objs.aggregate(
                    count=Count(F('id')),
                    sum_tradeAmount=Sum(F('tradeAmount'),output_field=DecimalField()),
                    sum_commission=Sum(F('commission_paid'), output_field=DecimalField())
    )

    commission_paid_statistics = tran_commission_objs_paid.aggregate(
                    count=Count(F('id')),
                    sum_tradeAmount=Sum(F('tradeAmount'),output_field=DecimalField()),
                    sum_commission=Sum(F('commission_paid'), output_field=DecimalField())
    )

    commission_completed_statistics = tran_commission_objs_completed.aggregate(
                    count=Count(F('id')),
                    sum_tradeAmount=Sum(F('tradeAmount'),output_field=DecimalField()),
                    sum_commission=Sum(F('commission_paid'), output_field=DecimalField())
    )

    data = {
        'all':commission_statistics,
        'paid':commission_paid_statistics,
        'completed':commission_completed_statistics
    }
    return Response(data, status=HTTP_200_OK)

@api_view(['GET','POST','PUT'])
def get_taobao_commission_statistics(request):
    groups = get_groups(request.user,request)

    username = request.POST.get('username',None)
    if not groups:
        tran_commission_objs = payment_models.TransactionTaobao.objects.filter(account_holder=request.user)
    elif username:
        tran_commission_objs = payment_models.TransactionTaobao.objects.filter(account_holder__username=username)
    else:
        tran_commission_objs =payment_models.TransactionTaobao.objects.all()


    tran_commission_objs_paid = tran_commission_objs.filter(tk_status=12)
    tran_commission_objs_completed = tran_commission_objs.filter(tk_status=3)

    commission_statistics = tran_commission_objs.aggregate(
                    count=Count(F('id')),
                    sum_alipay_total_price=Sum(F('alipay_total_price'),output_field=DecimalField()),
                    sum_commission_paid=Sum(F('commission_paid'), output_field=DecimalField())
    )

    commission_paid_statistics = tran_commission_objs_paid.aggregate(
                    count=Count(F('id')),
                    sum_alipay_total_price=Sum(F('alipay_total_price'),output_field=DecimalField()),
                    sum_commission_paid=Sum(F('commission_paid'), output_field=DecimalField())
    )

    commission_completed_statistics = tran_commission_objs_completed.aggregate(
                    count=Count(F('id')),
                    sum_alipay_total_price=Sum(F('alipay_total_price'),output_field=DecimalField()),
                    sum_commission_paid=Sum(F('commission_paid'), output_field=DecimalField())
    )
    data = {
        'all':commission_statistics,
        'paid':commission_paid_statistics,
        'completed':commission_completed_statistics
    }
    return Response(data, status=HTTP_200_OK)

@api_view(['GET','POST','PUT'])
def get_list_taobao_order_commission(request):
    groups = get_groups(request.user,request)
    # currency_obj = shop_models.Currency.objects.get(code='CNY')
    # balance_account_obj = payment_models.BalanceAccount.objects.get_or_create(account_holder=request.user,currency=currency_obj)
    if not groups:
        tran_commission_objs = payment_models.TransactionTaobao.objects.filter(account_holder=request.user).order_by('-created')
    else:
        tran_commission_objs = payment_models.TransactionTaobao.objects.all().order_by('-created')
    my_search = request.GET.get('search')
    if my_search:
        tran_commission_objs = tran_commission_objs.filter(Q(id__icontains=my_search) | Q(
            trade_parent_id__icontains=my_search) | Q(
            item_title__icontains=my_search) ).order_by('-created')
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])

    count = tran_commission_objs.count()
    list_get = tran_commission_objs[offset:offset+limit]

    data = TransactionTaobaoSerializer(list_get, many=True).data

    data_table = {'total': count, 'rows': data}

    return Response(data_table, status=HTTP_200_OK)

@api_view(['GET','POST','PUT'])
def get_all_commission(request):
    groups = get_groups(request.user,request)
    # currency_obj = shop_models.Currency.objects.get(code='CNY')
    # balance_account_obj = payment_models.BalanceAccount.objects.get_or_create(account_holder=request.user,currency=currency_obj)
    if not groups:
        tran_commission_objs = payment_models.TransactionCommission.objects.filter(account_holder=request.user).order_by('-created')
    else:
        tran_commission_objs = payment_models.TransactionCommission.objects.all().order_by('-created')
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])

    count = tran_commission_objs.count()
    list_get = tran_commission_objs[offset:offset+limit]

    data = TransactionCommissionSerializer(list_get, many=True).data

    data_table = {'total': count, 'rows': data}
    return Response(data_table, status=HTTP_200_OK)


@api_view(['GET','POST','PUT'])
@login_required_ajax()
# @signature_test()
# @user_passes_test(banned_check)
def get_commission_information(request):
    # groups = get_groups(request.user,request)
    
    balance_currency = request.GET.get('currency','VND')

    currency_obj, created = shop_models.Currency.objects.get_or_create(code=balance_currency.upper(), label=balance_currency.upper())
    
    accountBalance_objs = payment_models.BalanceAccount.objects.filter(currency__code=balance_currency.upper(), account_holder=request.user)
    if accountBalance_objs.exists():
        accountBalance = accountBalance_objs.first()
    else:
        accountBalance, created = payment_models.BalanceAccount.objects.get_or_create(currency=currency_obj, account_holder=request.user, name=request.user.username)
        
    print('==get deposit==')
    transaction_deposits = payment_models.TransactionCommission.objects.filter(account_holder=request.user, transaction_type=TransactionCommissionType.deposit, status=TransactionStatus.success).aggregate(
            sum_amount=Sum(F('amount') * F('exchange_rate')), count=Count(F('id')))
    
    print('==get paid==')
    #paid some orders by currency
    transaction_paids = payment_models.TransactionCommission.objects.filter(account_holder=request.user, transaction_type=TransactionCommissionType.pay, status=TransactionStatus.success).aggregate(
            sum_amount=Sum(F('amount') * F('exchange_rate')), count=Count(F('id')))
    
    print('==get withdrawns==')
    transaction_withdrawns = payment_models.TransactionCommission.objects.filter(account_holder=request.user, transaction_type=TransactionCommissionType.withdrawn, status=TransactionStatus.success).aggregate(
            sum_amount=Sum(F('amount') * F('exchange_rate')), count=Count(F('id')))

    transaction_pending = payment_models.TransactionCommission.objects.filter(account_holder=request.user, transaction_type=TransactionCommissionType.agency, status=TransactionStatus.pending).aggregate(
            sum_amount=Sum(F('amount') * F('exchange_rate')), count=Count(F('id')))
    
    if not transaction_deposits['sum_amount']:
        sum_deposits_amount = 0
    else:
        sum_deposits_amount = transaction_deposits['sum_amount']

    if not transaction_paids['sum_amount']:
        sum_pays_amount = 0
    else:
        sum_pays_amount = transaction_paids['sum_amount']
    if not transaction_withdrawns['sum_amount']:
        sum_withdrawns_amount = 0
    else:
        sum_withdrawns_amount = transaction_withdrawns['sum_amount']
    current_banlance = sum_deposits_amount - sum_pays_amount - sum_withdrawns_amount
    accountBalance.amount = current_banlance
    accountBalance.save(update_fields=['amount'])
    

    data_table = {'account_balance':{'username': request.user.username, 'currency': balance_currency,'current_banlance': current_banlance},'total_deposit': dict(transaction_deposits), 'total_paid': dict(transaction_paids), 'total_withdrawns': dict(transaction_withdrawns), 'total_pending': dict(transaction_pending)}
    return Response(data_table, status=HTTP_200_OK)


@api_view(['GET'])
def get_item_selections(request):
    page_size = request.GET.get('page_size',20)
    page_no = request.GET.get('page_no',1)
    resq = get_optimus_optional(6708,page_no=page_no,page_size=page_size)
    return Response(resq, status=HTTP_200_OK)

@api_view(['GET'])
def get_item_quantity_sale(request):

    page_size = request.GET.get('page_size',20)
    page_no = request.GET.get('page_no',1)
    resq = get_optimus_optional(28026,page_no=page_no,page_size=page_size)
    return Response(resq, status=HTTP_200_OK)

@api_view(['GET'])
def get_item_flash_sale(request):

    page_size = request.GET.get('page_size',20)
    page_no = request.GET.get('page_no',1)
    resq = get_optimus_optional(4094,page_no=page_no,page_size=page_size)
    return Response(resq, status=HTTP_200_OK)

@api_view(['GET'])
def get_item_ifashions(request):
    page_size = request.GET.get('page_size',20)
    page_no = request.GET.get('page_no',1)
    resq = get_optimus_optional(4093,page_no=page_no,page_size=page_size)
    return Response(resq, status=HTTP_200_OK)



