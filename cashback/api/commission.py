import json, decimal, re, os, logging
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from cashback.models import  payment_models, shop_models, product_models
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.db.models import Sum, F, Count, Q, FloatField, DecimalField, ExpressionWrapper
from admin_angular_webapp.views import get_groups
from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from shop_module.task import get_commisstion_obj, taokouling_extract
from admin_angular_webapp.api.Serializer import TransactionCommissionSerializer,Transaction1688Serializer,TransactionTaobaoSerializer
import aop.api
import top.api

appkey = settings.TAOBAO_APPKEY
secret = settings.TAOBAO_SECRET
adzone_id = settings.TAOBAO_ADZONE_ID



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


@api_view(['POST'])
def get_commisstion(request):

    if request.user.is_authenticated():
        username = request.user.username
    else:
        if not request.session.session_key:
            request.session.save()
        username = request.session.session_key
    status = {'success': False, 'msg': "kiem tra lai thong tin"}
    list_currencies = shop_models.Currency.objects.get(code='CNY')
    exchange_rate = list_currencies.exchange_rate
    html = {"user":None,"config":{"exchange_rate":exchange_rate,"service_cost_1688":"12","service_cost_taobao":"10","service_cost_tmall":"10"}}
    status['config'] = html
    url = request.POST.get('key','')
    if url:
        if not re.search(r'1688\.', url):
            get_taokouling = taokouling_extract(url)
            if get_taokouling:
                url = get_taokouling[0]
        commisstion_obj = get_commisstion_obj(url,username=username)
        if commisstion_obj:
            status['success'] = True
            status['short_title'] = commisstion_obj.short_title
            status['pict_url'] = commisstion_obj.pict_url
            status['url'] = commisstion_obj.url
            status['taokouling'] = commisstion_obj.taokouling
            status['zk_final_price'] = commisstion_obj.zk_final_price
            status['commission_price'] = commisstion_obj.commission_price
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


def get_material_optional(keyword,page_no=1,page_size=20):
    req = top.api.TbkDgMaterialOptionalRequest()
    req.set_app_info(top.appinfo(appkey, secret))

    # req.start_dsr = 10
    req.page_size = page_size
    req.page_no =page_no
    req.platform = 1
    # req.end_tk_rate = 1234
    # req.start_tk_rate = 1234
    # req.end_price = 10
    # req.start_price = 10
    req.is_overseas = 'false'
    # req.is_tmall = false
    # req.sort = "tk_rate_des"
    # req.itemloc = "杭州"
    # req.cat = "16,18"
    # req.q = keyword
    req.material_id = 30443
    req.cat = "16,18"
    req.q = keyword
    # req.has_coupon = false
    # req.ip = "13.2.33.4"
    req.adzone_id = adzone_id
    # req.need_free_shipment = true
    # req.need_prepay = true
    # req.include_pay_rate_30 = true
    # req.include_good_rate = true
    # req.include_rfd_rate = true
    # req.npx_level = 2
    # req.end_ka_tk_rate = 1234
    # req.start_ka_tk_rate = 1234
    req.device_encrypt = "MD5"
    req.device_value = "xxx"
    req.device_type = "IMEI"

    resp = req.getResponse()
    # print(resp)
    if resp['tbk_dg_material_optional_response']['result_list']['map_data']:
        return resp['tbk_dg_material_optional_response']['result_list']['map_data']
    else:
        return


def get_optimus_optional(material_id,page_no=1,page_size=20):
    req = top.api.TbkDgOptimusMaterialRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    # san pham:6708
    # ban chay:28026
    # flash sale:4094
    # ifashion:4093
    req.page_size = page_size
    req.page_no = page_no
    req.material_id = material_id
    req.platform = 1
    req.adzone_id = adzone_id
    req.device_encrypt = "MD5"
    req.device_value = "xxx"
    req.device_type = "IMEI"
    resp = req.getResponse()
    if resp['tbk_dg_optimus_material_response']['result_list']['map_data']:
        return resp['tbk_dg_optimus_material_response']['result_list']['map_data']
    else:
        return


