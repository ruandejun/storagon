#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  serializers.py
#
#
#  Created by MEOMUN on 12/1/15.
#  Copyright (c) 2015 orderus. All rights reserved.
from rest_framework import serializers
from cashback.models import payment_models, product_models
from django.contrib.auth.models import User
from django.db.models import Sum, F, Count, Q
from system_configure.controllers import SystemConfigureController
import decimal

class TranslateKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = translate_models.TranslateKey

        fields = ('key', 'zh_value')

class BankaccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.BankAccount

        fields = ('name', 'bank_branch','bank_account','type')

    type = serializers.SlugRelatedField(slug_field='label', read_only=True)



class KhieuNaiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticketbox_models.TicketBox

        fields = ('id', 'customer','group_care','order','shipment_package','status','created_by','takecare_by','takecare_tag','created_tag','order_item', 'title','body', 'note','first_image_url')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)
    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    takecare_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)
    group_care = serializers.SlugRelatedField(slug_field='label', read_only=True)
    order = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    shipment_package = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    order_item = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    created_tag = serializers.SerializerMethodField()
    takecare_tag = serializers.SerializerMethodField()
    first_image_url = serializers.SerializerMethodField()

    @staticmethod
    def get_created_tag(ticketbox):
        if ticketbox.created:
            return ticketbox.created.strftime("%d-%m-%Y %H:%M")
        else:
            return ticketbox.created

    @staticmethod
    def get_takecare_tag(ticketbox):
        if ticketbox.takecare:
            return ticketbox.takecare.strftime("%d-%m-%Y %H:%M")
        else:
            return ticketbox.takecare

    @staticmethod
    def get_first_image_url(ticketbox):
        if ticketbox.order_item:
            return ticketbox.order_item.image_url
        elif ticketbox.shipment_package:
            return ticketbox.shipment_package.first_image_url
        elif ticketbox.order:
            return ticketbox.order.first_image_url


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.Transaction

        fields = ('id', 'customer', 'order', 'type', 'payment_type', 'purpose_payment', 'partner_company', 'website','bank_account','created_tag','created_by','modified_tag','modified_by','currency','exchange_rate','amount','amount_foreign','weight','detail','reference','note','approved_by','approved_tag','status','from_balance_history','to_balance_history')

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    approved_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    type = serializers.SlugRelatedField(slug_field='label', read_only=True)
    payment_type = serializers.SlugRelatedField(slug_field='label', read_only=True)
    purpose_payment = serializers.SlugRelatedField(slug_field='label', read_only=True)
    website = serializers.SlugRelatedField(slug_field='label', read_only=True)
    status = serializers.SlugRelatedField(slug_field='label', read_only=True)
    currency = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_tag = serializers.SerializerMethodField()
    modified_tag = serializers.SerializerMethodField()
    approved_tag = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    bank_account = BankaccountSerializer(many=False)

    @staticmethod
    def get_order(transaction):
        if hasattr(transaction, 'customerpayment'):
            return transaction.customerpayment.order_id
        else:
            return None
    @staticmethod
    def get_customer(transaction):
        if transaction.transaction_holder:
            return transaction.transaction_holder.account_holder.username
        else:
            return None
    @staticmethod
    def get_created_tag(transaction):
        if transaction.created:
            return transaction.created.strftime("%d-%m-%Y %H:%M")
        else:
            return transaction.created
    @staticmethod
    def get_modified_tag(transaction):
        if transaction.modified:
            return transaction.modified.strftime("%d-%m-%Y %H:%M")
        else:
            return transaction.modified

    @staticmethod
    def get_approved_tag(transaction):
        if transaction.approved:
            return transaction.approved.strftime("%d-%m-%Y %H:%M")
        else:
            return transaction.approved

class CustomerPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = payment_models.CustomerPayment

        fields = ('id', 'created_tag','created_by','transaction_tag','type','note','transaction_id','need_to_pay','payment_left','sum_shipment_cost','sum_shipment_weight','total_service','currency','exchange_rate','transaction_amount')


    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    currency = serializers.SlugRelatedField(slug_field='code', read_only=True)

    type = serializers.SlugRelatedField(slug_field='label', read_only=True)


    transaction_tag = serializers.SerializerMethodField()
    transaction_id = serializers.SerializerMethodField()
    transaction_amount = serializers.SerializerMethodField()



    @staticmethod
    def get_transaction_amount(customerpayment):
        return customerpayment.transaction.amount

    @staticmethod
    def get_transaction_tag(customerpayment):
        return customerpayment.transaction.__str__()
    
    @staticmethod
    def get_transaction_id(customerpayment):
        return customerpayment.transaction.id

class OrderItemTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_models.OrderItem

        fields = ('id','created_tag','ordered_tag','checked_tag', 'order', 'name', 'item_url', 'status', 'item_status', 'currency', 'exchange_rate', 'image_url', 'quantity','order_quantity','sum_arrived_quantity','sum_arrived_shipping_cost','sum_arrived_shipping_cost_vnd', 'options_selected', 'option_selected_tag', 'fragile', 'insurance','rocket','packing', 'service', 'note', 'interal_note', 'customer_note','count_shipmentpackage','count_orderpackage','image_url_big','price','order_price','shipping','order_shipping','paid_quantity','ordered_by_username','checked_by_username','order_employee','check_employee')

class ThanhToanHoTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_models.ThanhToanHo

        fields = ('id','price','customer','note','created_by', 'created_tag','currency','exchange_rate','service_charge','total_price','status')

    status = serializers.SlugRelatedField(slug_field='label', read_only=True)
    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)
    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    currency = serializers.SlugRelatedField(slug_field='code', read_only=True)

class OrderItemTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_models.OrderItem
        fields = ('id', 'price', 'quantity', 'image_url', 'item_url')




class OrderTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order


        fields = ('id','full_name','username','status','status_value','status_processing','ordered_by','need_to_pay','total_item_cost','rocket','prepaid_date_tag','created_tag','ordered_date_tag','modified_by','first_image_url','sum_item_cost','sum_item_shipping','sum_item_total_service_cost','sum_shipment_cost','customer_note','order_discount','total_item_cost_not_shipment','sum_shipment_weight','sum_payment_transaction','count_payment','total_extra_price','extra_charge','tax_cost','payment_left','stop_refund','prepaid_rate','sum_by_currency','count_tickets','count_shipment','count_items','count_quantity','sum_item_price','sum_item_shipping_orig','sum_item_total_service_cost_orig','discount','cost_per_weight','service','count_madathang','prepaid_percent','order_profit')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    ordered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    status_value = serializers.SerializerMethodField()

    # need_to_pay = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    prepaid_rate = serializers.SerializerMethodField()

    sum_by_currency = serializers.SerializerMethodField()

    count_tickets = serializers.SerializerMethodField()

    count_madathang = serializers.SerializerMethodField()



    @staticmethod
    def get_username(order):
        return order.customer.username
    # @staticmethod
    # def get_need_to_pay(order):
    #     return order.need_to_pay
    @staticmethod
    def get_status_value(order):
        return order.status.value

    @staticmethod
    def get_prepaid_rate(order):
        try:
            prepaid_rate = order.customer.customerProfile.prepaid_rate
        except:
            prepaid_rate = 70
        return prepaid_rate

    @staticmethod
    def get_sum_by_currency(order):
        return list(order.sum_by_currency)

    @staticmethod
    def get_count_tickets(order):
        return order.ticketbox_set.count()

    @staticmethod
    def get_count_madathang(order):
        return order.orderpackage_set.all().distinct().count()




class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order

        #fields = (
        #'id', 'full_name', 'username', 'status_processing', 'ordered_by',
        #'total_item_cost', 'created_tag','first_image_url','customer_note','payment_left','sum_payment_transaction','need_to_pay','ordered_date_tag','modified_by')

        fields = ('id', 'full_name','username','status','status_value','status_processing','ordered_by','need_to_pay','sum_payment_transaction','total_item_cost','rocket','prepaid_date_tag','created_tag','ordered_date_tag','modified_by','first_image_url','sum_item_cost','sum_item_shipping','sum_item_total_service_cost','sum_shipment_cost','customer_note','order_discount','total_item_cost_not_shipment','facebook_name','address_tag','receiver_phone','sum_shipment_weight','sum_payment_transaction','count_payment','total_extra_price','extra_charge','tax_cost','payment_left','stop_refund','prepaid_rate','sum_by_currency','count_tickets','count_shipment','count_items','count_quantity','sum_item_price','sum_item_shipping_orig','sum_item_total_service_cost_orig','delivery_address','district','city','receiver_name','discount','cost_per_weight','service','count_madathang','prepaid_percent')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    ordered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    status_value = serializers.SerializerMethodField()

    # need_to_pay = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    prepaid_rate = serializers.SerializerMethodField()

    sum_by_currency = serializers.SerializerMethodField()

    count_tickets = serializers.SerializerMethodField()

    count_madathang = serializers.SerializerMethodField()



    @staticmethod
    def get_username(order):
        return order.customer.username
    # @staticmethod
    # def get_need_to_pay(order):
    #     return order.need_to_pay
    @staticmethod
    def get_status_value(order):
        return order.status.value

    @staticmethod
    def get_prepaid_rate(order):
        try:
            prepaid_rate = order.customer.customerProfile.prepaid_rate
        except:
            prepaid_rate = 70
        return prepaid_rate

    @staticmethod
    def get_sum_by_currency(order):
        return list(order.sum_by_currency)

    @staticmethod
    def get_count_tickets(order):
        return order.ticketbox_set.count()

    @staticmethod
    def get_count_madathang(order):
        return order.orderpackage_set.all().distinct().count()


class OrderInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order

        fields = (
        'id', 'full_name', 'username', 'status', 'status_value', 'status_processing', 'ordered_by', 'need_to_pay',
        'sum_payment_transaction', 'total_item_cost', 'rocket', 'prepaid_date_tag', 'created_tag', 'ordered_date_tag',
        'modified_by', 'first_image_url', 'sum_item_cost', 'sum_item_shipping', 'sum_item_total_service_cost',
        'sum_shipment_cost', 'customer_note', 'order_discount', 'total_item_cost_not_shipment', 'facebook_name',
        'address_tag', 'receiver_phone', 'sum_shipment_weight', 'sum_payment_transaction', 'count_payment',
        'total_extra_price', 'extra_charge', 'tax_cost', 'payment_left', 'stop_refund', 'prepaid_rate',
        'sum_by_currency', 'count_tickets', 'count_shipment', 'count_items', 'count_quantity', 'sum_item_price',
        'sum_item_shipping_orig', 'sum_item_total_service_cost_orig', 'delivery_address', 'district', 'city','receiver_name')



    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    ordered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    status_value = serializers.SerializerMethodField()

    # need_to_pay = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    prepaid_rate = serializers.SerializerMethodField()

    sum_by_currency = serializers.SerializerMethodField()

    count_tickets = serializers.SerializerMethodField()


    @staticmethod
    def get_username(order):
        return order.customer.username
    # @staticmethod
    # def get_need_to_pay(order):
    #     return order.need_to_pay
    @staticmethod
    def get_status_value(order):
        return order.status.value

    @staticmethod
    def get_prepaid_rate(order):
        try:
            prepaid_rate = order.customer.customerProfile.prepaid_rate
        except:
            prepaid_rate = 70
        return prepaid_rate

    @staticmethod
    def get_sum_by_currency(order):
        return list(order.sum_by_currency)

    @staticmethod
    def get_count_tickets(order):
        return order.ticketbox_set.count()

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.Order

        fields = ('id', 'full_name','username','status','status_value','status_processing','ordered_by','need_to_pay','sum_payment_transaction','total_item_cost','rocket','prepaid_date_tag','created_tag','ordered_date_tag','modified_by','first_image_url','sum_item_cost','sum_item_shipping','sum_item_total_service_cost','sum_shipment_cost','customer_note','order_discount','total_item_cost_not_shipment','facebook_name','address_tag','receiver_phone','sum_shipment_weight','sum_payment_transaction','count_payment','total_extra_price','extra_charge','tax_cost','payment_left','stop_refund','prepaid_rate','sum_by_currency','count_tickets','count_shipment','count_items','count_quantity','sum_item_price','sum_item_shipping_orig','sum_item_total_service_cost_orig','delivery_address','district','city','receiver_name','discount','cost_per_weight','service','count_madathang','prepaid_percent','sum_orderpackage_price','sum_shipment_cost_org','sum_orderpackage_price_vnd','sum_orderpackage_price_vnd_org','order_profit','sum_shipment_payment_late_cost','sum_refundcharge_price','sum_refundcharge_price_vnd')



    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    ordered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    status_value = serializers.SerializerMethodField()

    # need_to_pay = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    prepaid_rate = serializers.SerializerMethodField()

    sum_by_currency = serializers.SerializerMethodField()

    count_tickets = serializers.SerializerMethodField()

    count_madathang = serializers.SerializerMethodField()



    @staticmethod
    def get_username(order):
        return order.customer.username
    # @staticmethod
    # def get_need_to_pay(order):
    #     return order.need_to_pay
    @staticmethod
    def get_status_value(order):
        return order.status.value

    @staticmethod
    def get_prepaid_rate(order):
        try:
            prepaid_rate = order.customer.customerProfile.prepaid_rate
        except:
            prepaid_rate = 70
        return prepaid_rate

    @staticmethod
    def get_sum_by_currency(order):
        return list(order.sum_by_currency)

    @staticmethod
    def get_count_tickets(order):
        return order.ticketbox_set.count()

    @staticmethod
    def get_count_madathang(order):
        return order.orderpackage_set.all().distinct().count()
class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = product_models.CartItem
        fields = ('id', 'price','customer','vendor','detail_url','name','image_url','short_description','currency','exchange_rate','price','shipping','quantity','min_quantity','price_ranges','options_selected','options_metadata','fragile','insurance','rocket','packing','service','bargain','rocket_ship','note','service_charge','insurance_charge','fragile_charge','rocket_charge','packing_charge','rocket_ship_charge','bargain_charge','product_id','option_selected_tag','total_service_cost')

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = order_models.OrderItem
        fields = ('id', 'shopping_domain', 'vendor', 'customer_note', 'note','interal_note', 'name', 'item_url', 'image_url','order_employee','check_employee','ordered_date','checked_date','completed_date','option_selected_tag', 'quantity','order_quantity','paid_quantity', 'currency', 'exchange_rate', 'price', 'order_price', 'paid_price', 'shipping', 'order_shipping', 'paid_shipping','total','order_total','paid_total', 'insurance_charge', 'service_charge', 'fragile_charge', 'rocket_charge','rocket_charge_vnd', 'packing_charge','packing_charge_vnd','bargain_charge','bargain_charge_vnd','bargain','rocket_ship', 'tax_cost', 'fragile', 'insurance','rocket','packing', 'service','total_service_cost','total_service_cost_vnd', 'status', 'status_value','created','modified',
                  'total_vnd','price_vnd','shipping_vnd','service_charge_vnd','insurance_charge_vnd',
                  'order_total_vnd','order_price_vnd','order_shipping_vnd',
                  'paid_total_vnd', 'paid_price_vnd', 'paid_shipping_vnd','count_orderpackage','count_shipmentpackage','sum_arrived_quantity','sum_arrived_shipping_cost','sum_arrived_shipping_cost_vnd','image_url_big','name_tag','sum_delivery_cost','created_tag','ordered_tag','checked_tag','order','username','full_name','checkitem','item_url_commi')

    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    order_employee = serializers.SlugRelatedField(slug_field='username', read_only=True)

    check_employee = serializers.SlugRelatedField(slug_field='username', read_only=True)

    order = serializers.SlugRelatedField(slug_field='pk', read_only=True)

    status_value = serializers.SerializerMethodField()

    completed_date = serializers.SerializerMethodField()

    modified = serializers.SerializerMethodField()

    created = serializers.SerializerMethodField()

    ordered_date = serializers.SerializerMethodField()

    checked_date = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()


    @staticmethod
    def get_username(orderPackage):
        if orderPackage.order:
            return orderPackage.order.customer.username
        else:
            return

    @staticmethod
    def get_full_name(orderPackage):
        if orderPackage.order:
            return orderPackage.order.customer.profile.full_name
        else:
            return
    @staticmethod
    def get_status_value(order):
        return order.status.value

    @staticmethod
    def get_completed_date(order):
        if  order.completed_date:
            return order.completed_date.strftime("%d-%m-%Y %H:%M")
        else:
            return None
    @staticmethod
    def get_modified(order):
        if  order.modified:
            return order.modified.strftime("%d-%m-%Y %H:%M")
        else:
            return None

    @staticmethod
    def get_created(order):
        if  order.modified:
            return order.modified.strftime("%d-%m-%Y %H:%M")
        else:
            return None
    @staticmethod
    def get_ordered_date(order):
        if  order.ordered_date:
            return order.ordered_date.strftime("%d-%m-%Y %H:%M")
        else:
            return None
    @staticmethod
    def get_checked_date(order):
        if  order.checked_date:
            return order.checked_date.strftime("%d-%m-%Y %H:%M")
        else:
            return None

class RefundchargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_models.Refundcharge

        fields = ('id','ordernumber_id','price','order_number','paid_price','total_order_number_price','total_item_price','total_refund_price','note','status','full_name','username','order','type','created_by','note','created_by','created','created_tag','first_image_url','modified_by','modified_tag')
        # read_only_fields = ('order_item_set')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)


    ordernumber_id = serializers.SerializerMethodField()
    paid_price = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    total_order_number_price = serializers.SerializerMethodField()
    total_item_price = serializers.SerializerMethodField()
    total_refund_price = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    created_tag = serializers.SerializerMethodField()
    modified_tag = serializers.SerializerMethodField()
    first_image_url = serializers.SerializerMethodField()

    @staticmethod
    def get_modified_tag(refund_charge):
        if refund_charge.modified:
            return refund_charge.modified.strftime("%d-%m-%Y %H:%M")
        else:
            return
    @staticmethod
    def get_created_tag(refund_charge):
        if refund_charge.created:
            return refund_charge.created.strftime("%d-%m-%Y %H:%M")
        else:
            return
    @staticmethod
    def get_first_image_url(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.first_image_url
        else:
            return
    @staticmethod
    def get_ordernumber_id(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.pk
        else:
            return
    @staticmethod
    def get_paid_price(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.price
        else:
            return

    @staticmethod
    def get_order_number(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.order_number
        else:
            return

    @staticmethod
    def get_total_order_number_price(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.total_order_number_price
        else:
            return

    @staticmethod
    def get_total_item_price(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.total_item_price
        else:
            return
    @staticmethod
    def get_total_refund_price(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.total_refund_price
        else:
            return


    @staticmethod
    def get_username(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.order.customer.username
        else:
            return

    @staticmethod
    def get_full_name(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.order.customer.profile.full_name
        else:
            return
    @staticmethod
    def get_order(refund_charge):
        if refund_charge.orderpackage_id:
            return refund_charge.orderpackage.order.id
        else:
            return
    @staticmethod
    def get_type(refund_charge):
        if refund_charge.refund_type:
            return refund_charge.refund_type.value
        else:
            return


class TransactionCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.TransactionCommission

        fields = ('transaction_holder', 'amount','detail','reference','note','status','approved','approved_by')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

class Transaction1688Serializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.Transaction1688
        fields = ('id','quantity','customer_commission','status','create_tag','confirm_tag','settle_tag','tradeAmount','feedId','bizId','ext','buyerType','name','transaction_commission','account_holder')

    account_holder = serializers.SlugRelatedField(slug_field='username', read_only=True)

class TransactionTaobaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.TransactionTaobao
        fields = ('id','account_holder','trade_parent_id','alipay_total_price','item_num','customer_commission', 'item_title','status','tk_create_time_tag','tk_earning_time_tag','item_link','item_img')

    account_holder = serializers.SlugRelatedField(slug_field='username', read_only=True)

class OrderPackageOrderItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.OrderPackage

        fields = ('value', 'text')

    value = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    @staticmethod
    def get_value(order_package):

        return order_package.pk

    @staticmethod
    def get_text(order_package):
        return order_package.order_number

class OrderPackageOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.OrderPackage

        fields = ('id','status','created_by','price','order_number','created','created_tag')



    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)




class OrderPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.OrderPackage

        fields = ('id','created_tag','paid_date_tag','status','note','rocket','order_number','order','item_count','username','full_name','total_order_number_price','total_item_price','total_refund_price','price','note','created_by','shipping','date_waiting','tracking_count','first_image_url')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    order = serializers.SlugRelatedField(slug_field='pk', read_only=True)

    username = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()


    @staticmethod
    def get_username(orderPackage):
        if orderPackage.order:
            return orderPackage.order.customer.username
        else:
            return

    @staticmethod
    def get_full_name(orderPackage):
        if orderPackage.order:
            return orderPackage.order.customer.profile.full_name
        else:
            return

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShippingAddress
        fields = ('id','customer','full_name','address','city','country','zipcode','phone','default')

    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)

class ExportedshipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.Exportedshipment
        fields = ('id','status','note','count_shipment_package_exported','sum_weight_shipment_package_exported','created_by','modified_by','exported_by','delivered_by','price','paid_price','item_price','created_tag','modified_tag','delivered_tag','exported_tag','full_name','username','extra_charge','shipping_address_tag','need_to_pay','shipping_type','shipping_method','shipping_address','shipping_full_name','shipping_shipment_address','shipping_city','shipping_phone','shipping_type_value','sum_shipping_cost_shipment_package_exported','sum_shipping_cost_shipment_package_exported_vnd','first_image_url','shipping_number')

    shipping_address = ShippingAddressSerializer(read_only=True)

    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    delivered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    exported_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    shipping_type = serializers.SlugRelatedField(slug_field='label', read_only=True)
    shipping_method = serializers.SlugRelatedField(slug_field='label', read_only=True)



    created_tag = serializers.SerializerMethodField()
    modified_tag = serializers.SerializerMethodField()
    delivered_tag = serializers.SerializerMethodField()
    exported_tag = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    shipping_address_tag = serializers.SerializerMethodField()
    # need_to_pay = serializers.SerializerMethodField()
    first_image_url = serializers.SerializerMethodField()

    ##
    shipping_full_name = serializers.SerializerMethodField()
    shipping_shipment_address = serializers.SerializerMethodField()
    shipping_city = serializers.SerializerMethodField()
    shipping_phone = serializers.SerializerMethodField()
    shipping_type_value = serializers.SerializerMethodField()
    # shipping_type_tag = serializers.SerializerMethodField()

    # @staticmethod
    # def get_shipping_type_tag(exportedshipment):
    #     if exportedshipment.shipping_type:
    #         if exportedshipment.shipping_type.value == 'company':
    #             return 'Công ty'
    #         else:
    #             return 'Địa chỉ'
    #     else:
    #         return None
    @staticmethod
    def get_first_image_url(exportedshipment):
        if exportedshipment.exported_shipment_service.exists():
            order_item = exportedshipment.exported_shipment_service.first().order_item.exclude(
                Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved'))
            if order_item.exists():
                return order_item.first().image_url
            else:
                return

        else:
            return

    # @staticmethod
    # def get_need_to_pay(exportedshipment):
    #     if exportedshipment.price:
    #         return exportedshipment.price + exportedshipment.extra_charge+exportedshipment.sum_shipping_cost_shipment_package_exported_vnd - exportedshipment.sum_payment_transaction
    #     else:
    #         return None
    @staticmethod
    def get_shipping_full_name(exportedshipment):
        if exportedshipment.shipping_address:
            return exportedshipment.shipping_address.full_name
        else:
            return None

    @staticmethod
    def get_shipping_type_value(exportedshipment):
        if exportedshipment.shipping_type:
            return exportedshipment.shipping_type.value
        else:
            return None


    @staticmethod
    def get_shipping_shipment_address(exportedshipment):
        if exportedshipment.shipping_address:
            return exportedshipment.shipping_address.address
        else:
            return None

    @staticmethod
    def get_shipping_city(exportedshipment):
        if exportedshipment.shipping_address:
            return exportedshipment.shipping_address.city
        else:
            return None

    @staticmethod
    def get_shipping_phone(exportedshipment):
        if exportedshipment.shipping_address:
            return exportedshipment.shipping_address.phone
        else:
            return None


    @staticmethod
    def get_shipping_address_tag(exportedshipment):
        if exportedshipment.shipping_address:
            shipping_address_tag = '%s, %s, %s, %s' % (exportedshipment.shipping_address.full_name,exportedshipment.shipping_address.phone,exportedshipment.shipping_address.address,exportedshipment.shipping_address.city)
            return shipping_address_tag.replace(', , ,','...')
        else:
            return None

    @staticmethod
    def get_full_name(exportedshipment):
        if exportedshipment.customer:
            return exportedshipment.customer.profile.full_name
        else:
            return None

    @staticmethod
    def get_username(exportedshipment):
        if exportedshipment.customer:
            return exportedshipment.customer.username
        else:
            return None

    @staticmethod
    def get_created_tag(exportedshipment):
        if exportedshipment.created:
            return exportedshipment.created.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.created

    @staticmethod
    def get_modified_tag(exportedshipment):
        if exportedshipment.exported:
            return exportedshipment.exported.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.exported

    @staticmethod
    def get_delivered_tag(exportedshipment):
        if exportedshipment.delivered:
            return exportedshipment.delivered.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.delivered

    @staticmethod
    def get_exported_tag(exportedshipment):
        if exportedshipment.exported:
            return exportedshipment.exported.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.exported


class ShipmentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShipmentLocation

        fields = '__all__'

class ShipmentPackageSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = logistic_models.ShipmentPackage
        fields = ('id','tracking_number','website','order')

    website = serializers.SerializerMethodField()
    @staticmethod
    def get_website(shipmentpackage):
        company_information = SystemConfigureController.getConfigure('company_information')
        if 'Website' in company_information:
            return company_information['Website']
        else:
            return ''



class ShipmentPackageTemSerializer(serializers.ModelSerializer):
    location = ShipmentLocationSerializer(many=False)
    destination = ShipmentLocationSerializer(many=False)
    class Meta:
        model = logistic_models.ShipmentPackage

        fields = ('id','weight','weight_real','customer_tag','tracking_number','shipping_cost','count_order_item','customer_full_name','order','note','sum_price_item','exchange_rate','location','destination','ecommerce','details','arrived_quantity')
        # read_only_fields = ('order_item_set')



class ShipmentPackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShipmentPackage

        fields = ('id','created_tag','arrived_tag','delivered_tag','exported_tag','weight','weight_real','calculate_mass','customer_tag','tracking_number','shipping_cost','weight_cost','created_by_username','arrived_by_username','delivered_by_username','exported_by_username','count_order_item','sum_order_order_item','status_tag','customer_full_name','export_shipment','order','imported_shipment','exported_shipment','note','delivery_cost','status','created_by','exported_by','delivered_by','first_image_url','shipping_cost_vnd')
        # read_only_fields = ('order_item_set')


    exported_shipment = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    export_shipment = serializers.SlugRelatedField(slug_field='pk', read_only=True)

    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    exported_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    delivered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

class ShipmentPackageImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = logistic_models.ShipmentPackageImages

        fields = ('id','image_url','created_tag')
        # read_only_fields = ('order_item_set')

    created_tag = serializers.SerializerMethodField()

    @staticmethod
    def get_created_tag(shipmentpackageImages):
        if shipmentpackageImages.created:
            return shipmentpackageImages.created.strftime("%d-%m-%Y %H:%M")
        else:
            return shipmentpackageImages.created


class ShipmentPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShipmentPackage

        fields = (
        'id', 'created_tag', 'arrived_tag','departed_tag', 'delivered_tag', 'exported_tag', 'weight', 'weight_real', 'calculate_mass',
        'customer_tag', 'tracking_number', 'shipping_cost', 'weight_cost', 'created_by_username', 'arrived_by_username',
        'delivered_by_username', 'exported_by_username', 'count_order_item', 'sum_order_order_item', 'status_tag',
        'customer_full_name', 'export_shipment', 'order', 'imported_shipment', 'exported_shipment', 'note',
        'delivery_cost', 'status', 'created_by', 'exported_by', 'delivered_by', 'first_image_url', 'shipping_cost_vnd',
        'length','height','width','packing','fragile','fake_sum_price','ecommerce','details','shipment_images_set')

    shipment_images_set = ShipmentPackageImagesSerializer(many=True, read_only=True)

    exported_shipment = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    export_shipment = serializers.SlugRelatedField(slug_field='pk', read_only=True)
    status = serializers.SlugRelatedField(slug_field='label', read_only=True)
    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    exported_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    delivered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    departed_tag = serializers.SerializerMethodField()

    @staticmethod
    def get_departed_tag(shipmentPackage):
        if shipmentPackage.departed:
            return shipmentPackage.departed.strftime("%d-%m-%Y %H:%M")
        else:
            return shipmentPackage.departed

class ShipmentPackageImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShipmentPackage

        fields = (
        'id', 'weight', 'weight_real',
        'customer_tag', 'tracking_number', 'shipping_cost', 'count_order_item',
        'customer_full_name','imported_shipment', 'note', 'status','first_image_url','length','height','width','packing','fragile','ecommerce','details','origin_details','item_names','website_id','website_service','first_item_name')


    status = serializers.SlugRelatedField(slug_field='label', read_only=True)
    website_service = serializers.SlugRelatedField(slug_field='label', read_only=True)
    first_item_name = serializers.SerializerMethodField()
    @staticmethod
    def get_first_item_name(shipment):
        order_items = shipment.order_item.exclude(Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved'))
        if order_items.exists():

            return order_items.first().name
        else:
            return ''


class ImagesDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.ShipmentPackageImages

        fields = '__all__'

class ImportshipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.Importshipment

        fields = ('id','created_tag','arrived_tag','delivered_tag','note','status','customer','weight','price','extra_charge','sum_weight_shipment_package_import','sum_weight_real_shipment_package_import','count_shipment_package_import','website_service')
        # read_only_fields = ('order_item_set')

    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)

    website_service = serializers.SlugRelatedField(slug_field='name', read_only=True)
    # order_item = OrderItemTrackingSerializer(many=True)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticketbox_models.CommentTicketBox

        fields = ('id','created_tag','created_by_tag','body')
        # read_only_fields = ('order_item_set')

    # order_item = OrderItemTrackingSerializer(many=True)

class TicketBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticketbox_models.TicketBox

        fields = ('id','created_tag','customer_tag','type_tag','group_care_tag','order','shipment_package','order_item','title','body','status_tag','note','takecare_by_tag','takecare_tag','closed_tag','deadline_tag','closed_by_tag','full_name_tag','created_by_tag','commentticketbox_set')
        # read_only_fields = ('order_item_set')


    commentticketbox_set = CommentSerializer(many=True)

class ReportBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.ReportBalance

        fields = ('id','created_tag','created_by','note','refund_amount','paid_amount','deposit_amount','amount','account','group','type')
        # read_only_fields = ('order_item_set')

    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    type = serializers.SlugRelatedField(slug_field='value', read_only=True)
    created_tag = serializers.SerializerMethodField()

    @staticmethod
    def get_created_tag(reportbalance):
        if reportbalance.created:
            return reportbalance.created.strftime("%d-%m-%Y %H:%M")
        else:
            return reportbalance.created


class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ('id','username','email','profile','full_name','phone_number','address','facebook','dob','created_tag','ordered_count','ordered_date_tag', 'balance_vnd','sum_amount_payment_left','shipmentpackage_checked_count','sum_shipmentpackage_checked_weight','sum_shipmentpackage_checked_weight_cost','ordered_payment_left_count','sum_amount_need_to_pay','ordered_need_to_pay_count','sum_exported_shipment_amount_need_to_pay','exported_shipment_count','shipmentpackage_kygui_checked_count','sum_shipmentpackage_kygui_checked_weight','sum_shipmentpackage_kygui_checked_weight_cost','sum_amount_order_profit','completed_order_profit_count')

    full_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    dob = serializers.SerializerMethodField()
    created_tag = serializers.SerializerMethodField()
    ordered_count = serializers.SerializerMethodField()
    ordered_date_tag = serializers.SerializerMethodField()
    balance_vnd = serializers.SerializerMethodField()
    sum_amount_payment_left = serializers.SerializerMethodField()
    shipmentpackage_checked_count = serializers.SerializerMethodField()
    sum_shipmentpackage_checked_weight = serializers.SerializerMethodField()
    sum_shipmentpackage_checked_weight_cost = serializers.SerializerMethodField()
    ordered_payment_left_count = serializers.SerializerMethodField()
    sum_amount_need_to_pay = serializers.SerializerMethodField()
    ordered_need_to_pay_count = serializers.SerializerMethodField()
    sum_exported_shipment_amount_need_to_pay = serializers.SerializerMethodField()
    exported_shipment_count = serializers.SerializerMethodField()
    shipmentpackage_kygui_checked_count = serializers.SerializerMethodField()
    sum_shipmentpackage_kygui_checked_weight = serializers.SerializerMethodField()
    sum_shipmentpackage_kygui_checked_weight_cost = serializers.SerializerMethodField()

    sum_amount_order_profit = serializers.SerializerMethodField()
    completed_order_profit_count = serializers.SerializerMethodField()


    @staticmethod
    def get_balance_vnd(user):
        balance_obj = user.balanceaccount_set.filter(currency__code='VND')
        if balance_obj.exists():
            amount = balance_obj.first().amount
        else:
            amount = 0
        return amount



    def get_sum_exported_shipment_amount_need_to_pay(self, user):
        sum_user = user.customer_exported_shipmentpackages_set.exclude(Q(
            status__value='unapproved') | Q(amount_need_to_pay=0) | Q(amount_need_to_pay=decimal.Decimal(-1)) | Q(amount_need_to_pay=decimal.Decimal(1))).distinct().aggregate(
            sum_amount_need_to_pay=Sum(F('amount_need_to_pay')))
        if sum_user['sum_amount_need_to_pay']:
            return sum_user['sum_amount_need_to_pay']
        else:
            return 0


    def get_exported_shipment_count(self, user):
        return user.customer_exported_shipmentpackages_set.exclude(Q(
            status__value='unapproved') | Q(amount_need_to_pay=0) | Q(amount_need_to_pay=decimal.Decimal(-1)) | Q(amount_need_to_pay=decimal.Decimal(1))).distinct().count()


    def get_sum_amount_payment_left(self,user):
        #is_code_filter = self.context.get("is_code_filter")
        sum_user = user.order_customer_set.exclude(Q(status__value='WaitingForPrePaid') | Q(status__value='canceled') | Q(
            status__value='Failed') | Q(amount_payment_left=0) | Q(amount_payment_left=decimal.Decimal(-1)) | Q(amount_payment_left=decimal.Decimal(1))).distinct().aggregate(
            sum_amount_payment_left=Sum(F('amount_payment_left')))
        if sum_user['sum_amount_payment_left']:
            return sum_user['sum_amount_payment_left']
        else:
            return 0


    def get_sum_amount_need_to_pay(self,user):
        sum_user = user.order_customer_set.exclude(Q(status__value='WaitingForPrePaid') | Q(status__value='canceled') | Q(
            status__value='Failed') | Q(amount_need_to_pay=0) | Q(amount_need_to_pay=decimal.Decimal(-1)) | Q(amount_need_to_pay=decimal.Decimal(1))).distinct().aggregate(
            sum_amount_need_to_pay=Sum(F('amount_need_to_pay')))
        if sum_user['sum_amount_need_to_pay']:
            return sum_user['sum_amount_need_to_pay']
        else:
            return 0


    def get_sum_amount_order_profit(self,user):
        sum_user = user.order_customer_set.filter(status__value='delivered_ship').aggregate(
            sum_amount_order_profit=Sum(F('amount_order_profit')))
        if sum_user['sum_amount_order_profit']:
            return sum_user['sum_amount_order_profit']
        else:
            return 0


    def get_completed_order_profit_count(self,user):
        return user.order_customer_set.filter(status__value='delivered_ship').count()


    def get_shipmentpackage_kygui_checked_count(self,user):
        return user.customer_packages.filter(order__isnull=True,status__value='checked').count()



    def get_sum_shipmentpackage_kygui_checked_weight(self,user):
        sum_shipment = user.customer_packages.filter(order__isnull=True, status__value='checked').aggregate(
            sum_weight=Sum(F('weight')))
        if sum_shipment['sum_weight']:
            return sum_shipment['sum_weight']
        else:
            return 0

    def get_sum_shipmentpackage_kygui_checked_weight_cost(self,user):
        sum_shipment = user.customer_packages.filter(order__isnull=True, status__value='checked').aggregate(
            sum_weight_cost=Sum(F('weight') * F('weight_cost')))
        if sum_shipment['sum_weight_cost']:
            return sum_shipment['sum_weight_cost']
        else:
            return 0


    def get_shipmentpackage_checked_count(self,user):
        return user.customer_packages.filter(order__isnull=False,status__value='checked').count()


    def get_sum_shipmentpackage_checked_weight(self,user):
        sum_shipment = user.customer_packages.filter(order__isnull=False, status__value='checked').aggregate(
            sum_weight=Sum(F('weight')))
        if sum_shipment['sum_weight']:
            return sum_shipment['sum_weight']
        else:
            return 0

    def get_sum_shipmentpackage_checked_weight_cost(self,user):
        sum_shipment = user.customer_packages.filter(order__isnull=False, status__value='checked').aggregate(
            sum_weight_cost=Sum(F('weight') * F('weight_cost')))
        if sum_shipment['sum_weight_cost']:
            return sum_shipment['sum_weight_cost']
        else:
            return 0


    def get_ordered_payment_left_count(self,user):
        return user.order_customer_set.exclude(Q(status__value='WaitingForPrePaid') | Q(status__value='canceled') | Q(
            status__value='Failed') | Q(amount_payment_left=0) | Q(amount_payment_left=decimal.Decimal(-1)) | Q(amount_payment_left=decimal.Decimal(1))).distinct().count()

    def get_ordered_need_to_pay_count(self,user):
        return user.order_customer_set.exclude(Q(status__value='WaitingForPrePaid') | Q(status__value='canceled') | Q(
            status__value='Failed') | Q(amount_need_to_pay=0) | Q(amount_need_to_pay=decimal.Decimal(-1)) | Q(amount_need_to_pay=decimal.Decimal(1))).distinct().count()

    def get_ordered_count(self,user):
        return user.order_customer_set.count()

    @staticmethod
    def get_ordered_date_tag(user):
        if user.order_customer_set.exists():
            return user.order_customer_set.last().created.strftime("%d-%m-%Y %H:%M")
        else:
            return ''
    @staticmethod
    def get_full_name(user):
        if user.profile:
            return user.profile.full_name
        else:
            return ''

    @staticmethod
    def get_phone_number(user):
        if user.profile:
            return user.profile.phone_number
        else:
            return ''

    @staticmethod
    def get_address(user):
        if user.profile:
            return user.profile.address
        else:
            return ''

    @staticmethod
    def get_facebook(user):
        if user.profile:
            return user.profile.user_facebook
        else:
            return ''

    @staticmethod
    def get_dob(user):
        if user.profile:
            return user.profile.dob
        else:
            return ''


    @staticmethod
    def get_created_tag(user):
        if user.date_joined:
            return user.date_joined.strftime("%d-%m-%Y %H:%M")
        else:
            return user.date_joined



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ('id','username')


class ExportedSerializer(serializers.ModelSerializer):
    class Meta:
        model = logistic_models.Exportedshipment

        fields = ('id','created_by','created_tag','modified_by','modified_tag','exported_by','exported_tag','delivered_tag','delivered_by','status','price','note','weight')
        # read_only_fields = ('phone_number')
    status = serializers.SlugRelatedField(slug_field='label', read_only=True)

    ordered_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    created_tag = serializers.SerializerMethodField()
    modified_tag = serializers.SerializerMethodField()
    delivered_tag = serializers.SerializerMethodField()
    exported_tag = serializers.SerializerMethodField()

    @staticmethod
    def get_created_tag(exportedshipment):
        if exportedshipment.created:
            return exportedshipment.created.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.created

    @staticmethod
    def get_modified_tag(exportedshipment):
        if exportedshipment.modified:
            return exportedshipment.modified.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.modified

    @staticmethod
    def get_exported_tag(exportedshipment):
        if exportedshipment.exported:
            return exportedshipment.exported.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.exported
    @staticmethod
    def get_delivered_tag(exportedshipment):
        if exportedshipment.delivered:
            return exportedshipment.delivered.strftime("%d-%m-%Y %H:%M")
        else:
            return exportedshipment.delivered
