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



class BankaccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_models.BankAccount

        fields = ('name', 'bank_branch','bank_account','type')

    type = serializers.SlugRelatedField(slug_field='label', read_only=True)





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



class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = product_models.CartItem
        fields = ('id', 'price','customer','vendor','detail_url','name','image_url','short_description','currency','exchange_rate','price','shipping','quantity','min_quantity','price_ranges','options_selected','options_metadata','fragile','insurance','rocket','packing','service','bargain','rocket_ship','note','service_charge','insurance_charge','fragile_charge','rocket_charge','packing_charge','rocket_ship_charge','bargain_charge','product_id','option_selected_tag','total_service_cost')


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
