#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  payment_models.py
#
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#

import decimal
import uuid

from django.utils.functional import cached_property

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..constants.DefaultSettings import *
from storagon.enum import *
# from .order_models import AlipayAccounts


# ================= Payment ====================

class AlipayAccounts(models.Model):
    class Meta:
        verbose_name = _("AlipayAccounts")
        verbose_name_plural = _("AlipayAccounts")
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    note = models.TextField(verbose_name=_("note"), blank=True, default='')  # payment note
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    def __str__(self):
        return str("%s" % (self.value))

class PaymentType(models.Model):
    class Meta:
        verbose_name = _("PaymentType")
        verbose_name_plural = _("PaymentType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)

    is_customerpayment = models.BooleanField(verbose_name=_("is_customerpayment"), default=True, db_index=True)
    is_vendorpayment = models.BooleanField(verbose_name=_("is_vendorpayment"), default=False, db_index=True)
    is_logisticspayment = models.BooleanField(verbose_name=_("is_logisticspayment"), default=False, db_index=True)

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __str__(self):
        return str(self.label)

class TransactionType(models.Model):
    class Meta:
        verbose_name = _("TransactionType")
        verbose_name_plural = _("TransactionType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class CommissionType(models.Model):
    class Meta:
        verbose_name = _("CommissionType")
        verbose_name_plural = _("CommissionType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class PurposePayment(models.Model):
    class Meta:
        verbose_name = _("PurposePayment")
        verbose_name_plural = _("PurposePayment")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    note = models.CharField(verbose_name=_("note"), max_length=255, default='')
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class WebsiteType(models.Model):
    class Meta:
        verbose_name = _("WebsiteType")
        verbose_name_plural = _("WebsiteType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class Partnercompany(models.Model):
    class Meta:
        verbose_name = _("Partnercompany")
        verbose_name_plural = _("Partnercompany")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)


def migrate_getFirstUserID():
    firstUser = User.objects.all().first();
    if firstUser:
        return firstUser.pk
    else:
        return firstUser


class VendorPayment(models.Model):
    class Meta:
        verbose_name = _("VendorPayment")
        verbose_name_plural = _("VendorPayment")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    vendor = models.ForeignKey("Vendor", verbose_name=_("vendor"), on_delete=models.PROTECT)
    type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"), limit_choices_to={'is_vendorpayment': True},
                             on_delete=models.PROTECT)
    transaction = models.OneToOneField("Transaction", verbose_name=_("transaction"), on_delete=models.PROTECT)
    note = models.TextField(verbose_name=_("note"), blank=True)  # payment note

    def __str__(self):
        return str(self.transaction) if self.transaction_id else ""

# class LogisticsPayment(models.Model):
#     class Meta:
#         verbose_name = _("LogisticsPayment")
#         verbose_name_plural = _("LogisticsPayment")

#     created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
#     modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
#     created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
#     modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

#     shipment_service = models.ForeignKey("ShipmentService", verbose_name=_("shipment_service"),
#                                          on_delete=models.PROTECT)
#     type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"),
#                              limit_choices_to={'is_logisticspayment': True}, on_delete=models.PROTECT)
#     transaction = models.OneToOneField("Transaction", verbose_name=_("transaction"), on_delete=models.PROTECT)
#     note = models.TextField(verbose_name=_("note"), blank=True)  # payment note

#     def __str__(self):
#         return str(self.transaction) if self.transaction_id else ""

class GenericPayment(models.Model):
    class Meta:
        verbose_name = _("General Payment")
        verbose_name_plural = _("General Payment")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, verbose_name=_("content_type"), on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(verbose_name=_("object_id"), )
    content_object = GenericForeignKey('content_type', 'object_id')

    type = models.ForeignKey("PaymentType", verbose_name=_("type"), on_delete=models.PROTECT)

    transaction = models.OneToOneField("Transaction", verbose_name=_("transaction"), on_delete=models.PROTECT)
    note = models.TextField(verbose_name=_("note"), blank=True)  # payment note

    def __str__(self):
        return str(self.transaction) if self.transaction_id else ""

class CustomerPayment(models.Model):
    class Meta:
        verbose_name = _("CustomerPayment")
        verbose_name_plural = _("CustomerPayment")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    # order = models.ForeignKey("Order", verbose_name=_("order"), null=True, blank=True, on_delete=models.PROTECT)

    # thanhtoanho = models.ForeignKey("ThanhToanHo", verbose_name=_("ThanhToanHo"), null=True, blank=True, on_delete=models.PROTECT)

    # order_billing = models.ForeignKey("OrderBilling", verbose_name=_("order_billing"), null=True, blank=True, on_delete=models.PROTECT)

    # exported_shipment = models.ForeignKey("Exportedshipment", verbose_name=_("exported_shipment"), null=True, blank=True, on_delete=models.PROTECT)

    type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"),
                             limit_choices_to={'is_customerpayment': True}, on_delete=models.PROTECT)

    need_to_pay = models.DecimalField(verbose_name=_("need_to_pay"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True, null=True, blank=True)

    payment_left = models.DecimalField(verbose_name=_("payment_left"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True, null=True, blank=True)

    sum_shipment_cost = models.DecimalField(verbose_name=_("sum_shipment_cost"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True, null=True, blank=True)

    sum_shipment_weight = models.DecimalField(verbose_name=_("sum_shipment_weight"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True, null=True, blank=True)

    total_service = models.DecimalField(verbose_name=_("total_service"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True, null=True, blank=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT, null=True, blank=True)


    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    transaction = models.OneToOneField("Transaction", verbose_name=_("transaction"), on_delete=models.PROTECT)

    note = models.TextField(verbose_name=_("note"), blank=True)  # payment note

    def __str__(self):
        return str(self.transaction) if self.transaction_id else ""

    def amount_tag(self):
        return self.transaction.currency.display(self.transaction.amount)

    # @cached_property
    # def customer_tag(self):
    #     return self.order.customer.username

    @cached_property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created

class TransactionTaobao(models.Model):
    class Meta:
        verbose_name = _("TransactionTaobao")
        verbose_name_plural = _("TransactionTaobao")
        #unique_together = ("transaction_holder", "type", 'payment_type', 'created_by', 'amount', 'reference')



    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    pay_price = models.DecimalField(verbose_name=_("pay_price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    pub_share_fee = models.DecimalField(verbose_name=_("pub_share_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    pub_share_rate = models.DecimalField(verbose_name=_("pub_share_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    subsidy_rate = models.DecimalField(verbose_name=_("subsidy_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    tk_total_rate = models.DecimalField(verbose_name=_("tk_total_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    alimama_rate = models.DecimalField(verbose_name=_("alimama_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    pub_share_pre_fee = models.DecimalField(verbose_name=_("pub_share_pre_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    alipay_total_price = models.DecimalField(verbose_name=_("alipay_total_price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    subsidy_fee = models.DecimalField(verbose_name=_("subsidy_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    alimama_share_fee = models.DecimalField(verbose_name=_("alimama_share_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    item_price = models.DecimalField(verbose_name=_("item_price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    total_commission_rate = models.DecimalField(verbose_name=_("total_commission_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    income_rate = models.DecimalField(verbose_name=_("income_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    deposit_price = models.DecimalField(verbose_name=_("deposit_price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    total_commission_fee = models.DecimalField(verbose_name=_("total_commission_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    tk_commission_pre_fee_for_media_platform = models.DecimalField(verbose_name=_("tk_commission_pre_fee_for_media_platform"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    tk_commission_fee_for_media_platform = models.DecimalField(verbose_name=_("tk_commission_fee_for_media_platform"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    tk_commission_rate_for_media_platform = models.DecimalField(verbose_name=_("tk_commission_rate_for_media_platform"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)


    commission_paid = models.DecimalField(verbose_name=_("commission_paid"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)


    item_title = models.CharField(verbose_name=_("item_title"), max_length=2048, blank=True)
    site_name = models.CharField(verbose_name=_("site_name"), max_length=2048, blank=True)
    item_img = models.CharField(verbose_name=_("item_img"), max_length=2048, blank=True)
    item_link = models.CharField(verbose_name=_("item_link"), max_length=2048, blank=True)
    seller_shop_title = models.CharField(verbose_name=_("seller_shop_title"), max_length=2048, blank=True)
    marketing_type = models.CharField(verbose_name=_("marketing_type"), null=True, blank=True, max_length=512)
    item_category_name = models.CharField(verbose_name=_("item_category_name"), null=True, blank=True, max_length=512)
    alsc_pid = models.CharField(verbose_name=_("alsc_pid"), null=True, blank=True, max_length=512)
    alsc_id = models.CharField(verbose_name=_("alsc_id"), null=True, blank=True, max_length=512)
    trade_id = models.CharField(verbose_name=_("trade_id"), null=True, blank=True, max_length=512)
    site_id = models.CharField(verbose_name=_("site_id"), null=True, blank=True, max_length=512)
    item_id = models.CharField(verbose_name=_("item_id"), null=True, blank=True, max_length=512)
    special_id = models.CharField(verbose_name=_("special_id"), null=True, blank=True, max_length=512)
    relation_id = models.CharField(verbose_name=_("relation_id"), null=True, blank=True, max_length=512)
    adzone_name = models.CharField(verbose_name=_("adzone_name"), null=True, blank=True, max_length=512)
    trade_parent_id = models.CharField(verbose_name=_("trade_parent_id"), null=True, blank=True, max_length=512)
    order_type = models.CharField(verbose_name=_("order_type"), null=True, blank=True, max_length=512)
    flow_source = models.CharField(verbose_name=_("flow_source"), null=True, blank=True, max_length=512)
    terminal_type = models.CharField(verbose_name=_("terminal_type"), null=True, blank=True, max_length=512)
    pub_id = models.CharField(verbose_name=_("pub_id"), null=True, blank=True, max_length=512)
    subsidy_type = models.CharField(verbose_name=_("subsidy_type"), null=True, blank=True, max_length=512)

    adzone_id = models.CharField(verbose_name=_("adzone_id"), null=True, blank=True, max_length=512)

    seller_nick = models.CharField(verbose_name=_("seller_nick"), null=True, blank=True, max_length=512)
    tk_order_role = models.CharField(verbose_name=_("tk_order_role"), null=True, blank=True, max_length=512)

    refund_tag = models.PositiveIntegerField(verbose_name=_("refund_tag"), null=True, blank=True, default=0)

    item_num = models.PositiveIntegerField(verbose_name=_("item_num"), null=True, blank=True, default=1)

    tk_status = models.PositiveIntegerField(verbose_name=_("tk_status"), null=True, blank=True, default=0)
    is_lx = models.PositiveIntegerField(verbose_name=_("is_lx"), null=True, blank=True, default=0)

    tb_deposit_time = models.DateTimeField(verbose_name=_("tb_deposit_time"), null=True, blank=True)
    tk_deposit_time = models.DateTimeField(verbose_name=_("tk_deposit_time"), null=True, blank=True)
    click_time = models.DateTimeField(verbose_name=_("click_time"), null=True, blank=True)
    tk_create_time = models.DateTimeField(verbose_name=_("tk_create_time"), null=True, blank=True)
    modified_time = models.DateTimeField(verbose_name=_("modified_time"), null=True, blank=True)
    tk_paid_time = models.DateTimeField(verbose_name=_("tk_paid_time"), null=True, blank=True)
    tb_paid_time = models.DateTimeField(verbose_name=_("tb_paid_time"), null=True, blank=True)
    tk_earning_time = models.DateTimeField(verbose_name=_("tk_earning_time"), null=True, blank=True)

    account_holder = models.ForeignKey(User, verbose_name=_("account_holder"), null=True, blank=True,
                                       on_delete=models.PROTECT)
    transaction_commission = models.OneToOneField("TransactionCommission", verbose_name=_("transaction_commission"), blank=True,
                                           null=True,
                                           on_delete=models.PROTECT)

    @property
    def customer_commission(self):
        if self.commission_paid > decimal.Decimal(0):
            return self.commission_paid
        else:
            return self.pub_share_pre_fee * decimal.Decimal(0.80)

    @property
    def status(self):
        if self.tk_status == 12:
            return 'Đã thanh toán'
        elif self.tk_status == 13:
            return 'Đã hủy'
        elif self.tk_status == 3:
            return 'Hoàn thành'
        else:
            return 'Chờ xử lý'

    @property
    def tk_create_time_tag(self):
        if self.tk_create_time:
            return self.tk_create_time.strftime("%d-%m-%Y %H:%M")
        else:
            return self.tk_create_time

    @property
    def tk_earning_time_tag(self):
        if self.tk_earning_time:
            return self.tk_earning_time.strftime("%d-%m-%Y %H:%M")
        else:
            return self.tk_earning_time
    def __str__(self):
        return self.pk

class Transaction1688(models.Model):
    class Meta:
        verbose_name = _("Transaction1688")
        verbose_name_plural = _("Transaction1688")
        #unique_together = ("transaction_holder", "type", 'payment_type', 'created_by', 'amount', 'reference')



    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    platformRatio = models.DecimalField(verbose_name=_("platformRatio"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    commission = models.DecimalField(verbose_name=_("platformRatio"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    commission_paid = models.DecimalField(verbose_name=_("commission_paid"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    tradeAmount = models.DecimalField(verbose_name=_("tradeAmount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    ratio = models.DecimalField(verbose_name=_("ratio"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    tradeNumber = models.DecimalField(verbose_name=_("tradeNumber"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    settleState = models.PositiveIntegerField(verbose_name=_("settleState"), null=True, blank=True, default=0)
    platform = models.PositiveIntegerField(verbose_name=_("platform"), null=True, blank=True, default=0)
    orderState = models.PositiveIntegerField(verbose_name=_("orderState"), null=True, blank=True, default=0)
    rightsState = models.PositiveIntegerField(verbose_name=_("rightsState"), null=True, blank=True, default=0)
    tkId = models.CharField(verbose_name=_("tkId"), null=True, blank=True, max_length=512)
    mediaId = models.CharField(verbose_name=_("mediaId"), null=True, blank=True, max_length=512)
    feedId = models.CharField(verbose_name=_("feedId"), null=True, blank=True, max_length=512)
    bizId = models.CharField(verbose_name=_("bizId"), null=True, blank=True, max_length=512)
    bizSubId = models.CharField(verbose_name=_("bizSubId"), null=True, blank=True, max_length=512)
    ext = models.CharField(verbose_name=_("ext"), null=True, blank=True, max_length=512)
    buyerType = models.CharField(verbose_name=_("buyerType"), null=True, blank=True, max_length=512)
    mediaZoneId = models.CharField(verbose_name=_("mediaZoneId"), null=True, blank=True, max_length=512)

    name = models.CharField(verbose_name=_("name"), max_length=2048, blank=True)

    transaction_commission = models.OneToOneField("TransactionCommission", verbose_name=_("transaction_commission"), blank=True,
                                           null=True,
                                           on_delete=models.PROTECT)

    account_holder = models.ForeignKey(User, verbose_name=_("account_holder"), null=True, blank=True,
                                       on_delete=models.PROTECT)

    createTime = models.DateTimeField(verbose_name=_("createTime"), null=True, blank=True)
    settleTime = models.DateTimeField(verbose_name=_("settleTime"), null=True, blank=True)
    confirmTime = models.DateTimeField(verbose_name=_("confirmTime"), null=True, blank=True)

    @property
    def quantity(self):
        return int(self.tradeNumber)

    @property
    def customer_commission(self):
        if self.commission_paid > decimal.Decimal(0):
            return self.commission_paid
        else:
            return self.commission * decimal.Decimal(0.55)
    @property
    def status(self):
        if self.orderState == 10:
            return 'Chờ thanh toán'
        elif self.orderState == 20:
            return 'Đã thanh toán'
        elif self.orderState == 80:
            return 'Đã hủy'
        elif self.orderState == 50:
            return 'Hoàn thành'
        else:
            return 'Chờ xử lý'

    @property
    def create_tag(self):
        if self.createTime:
            return self.createTime.strftime("%d-%m-%Y %H:%M")
        else:
            return self.createTime
    @property
    def confirm_tag(self):
        if self.confirmTime:
            return self.confirmTime.strftime("%d-%m-%Y %H:%M")
        else:
            return self.confirmTime
    @property
    def settle_tag(self):
        if self.settleTime:
            return self.settleTime.strftime("%d-%m-%Y %H:%M")
        else:
            return self.settleTime


    def __str__(self):
        return self.pk

class TransactionCommission(models.Model):
    class Meta:
        verbose_name = _("TransactionCommission")
        verbose_name_plural = _("TransactionCommission")
        #unique_together = ("transaction_holder", "type", 'payment_type', 'created_by', 'amount', 'reference')
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    
    
    commission_type = models.ForeignKey(CommissionType, verbose_name=_("commission_type"), blank=True,
                                           null=True,
                                           on_delete=models.PROTECT)   
    
    transaction_holder = models.ForeignKey("BalanceAccount", verbose_name=_("transaction_holder"), blank=True,
                                           null=True,
                                           on_delete=models.PROTECT)
    commission_amount = models.DecimalField(verbose_name=_("commission_amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    
    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    customer_ratio = models.DecimalField(verbose_name=_("customer_ratio"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    
    share_fee = models.DecimalField(verbose_name=_("share_fee"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    
    detail = models.CharField(verbose_name=_("detail"), blank=True,max_length=512)  # store detail automatically get from bank system

    reference = models.CharField(verbose_name=_("reference"), blank=True, max_length=255)  # store detail automatically get from bank system

    note = models.TextField(verbose_name=_("note"), blank=True)  # ghi chu cho purpore

    approved_by = models.ForeignKey(User, verbose_name=_("approved_by"),related_name='transactionvommission_approved_by', limit_choices_to={'is_staff': True}, null=True,
                                blank=True, on_delete=models.PROTECT)

    approved = models.DateTimeField(verbose_name=_("approved"), null=True, blank=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), on_delete=models.PROTECT,null=True)

    def __str__(self):
        return self.pk

class Transaction(models.Model):
    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transaction")
        unique_together = ("transaction_holder", "type", 'payment_type', 'created_by', 'amount', 'reference')

    transaction_holder = models.ForeignKey("BalanceAccount", verbose_name=_("transaction_holder"), blank=True,
                                           null=True,
                                           on_delete=models.PROTECT)
    #deposit or paid
    type = models.ForeignKey("TransactionType", verbose_name=_("TransactionType"), on_delete=models.PROTECT, null=True)

    #bank or cash
    payment_type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"), on_delete=models.PROTECT, null=True)

    purpose_payment = models.ForeignKey("PurposePayment", verbose_name=_("PurposePayment"), on_delete=models.PROTECT, null=True, blank=True)

    partner_company = models.ForeignKey("Partnercompany", verbose_name=_("Partnercompany"), on_delete=models.PROTECT, null=True, blank=True)

    website = models.ForeignKey("WebsiteType", verbose_name=_("WebsiteType"), on_delete=models.PROTECT, null=True, blank=True)

    bank_account = models.ForeignKey("BankAccount", verbose_name=_("BankAccount"), on_delete=models.PROTECT, null=True, blank=True)

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    from_balance = models.ForeignKey("BalanceAccount", verbose_name=_("from_balance"), related_name='from_transactions',
                                     null=True, blank=True,
                                     on_delete=models.PROTECT)

    to_balance = models.ForeignKey("BalanceAccount", verbose_name=_("to_balance"), related_name='to_transactions',
                                   null=True, blank=True,
                                   on_delete=models.PROTECT)

    from_balance_history = models.CharField(verbose_name=_("from_balance_history"), default="", max_length=512,
                                            editable=False)
    to_balance_history = models.CharField(verbose_name=_("to_balance_history"), default="", max_length=512,
                                          editable=False)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS,
                                        decimal_places=XRATE_DECIMAL_PLACES, validators=[MinValueValidator(0)])

    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    amount_foreign = models.DecimalField(verbose_name=_("amount_foreign"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True,blank=True,null=True)

    extra_amount = models.DecimalField(verbose_name=_("extra_amount"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    detail = models.CharField(verbose_name=_("detail"), blank=True,max_length=512)  # store detail automatically get from bank system

    reference = models.CharField(verbose_name=_("reference"), blank=True, max_length=255)  # store detail automatically get from bank system

    note = models.TextField(verbose_name=_("note"), blank=True)  # ghi chu cho purpore

    cashier = models.ForeignKey(User, verbose_name=_("cashier"),related_name='to_cashier', limit_choices_to={'is_staff': True}, null=True,
                                blank=True, on_delete=models.PROTECT)

    approved_by = models.ForeignKey(User, verbose_name=_("approved_by"),related_name='to_approved_by', limit_choices_to={'is_staff': True}, null=True,
                                blank=True, on_delete=models.PROTECT)

    send_to = models.ForeignKey(User, verbose_name=_("send_to"), related_name='to_send_to',
                                limit_choices_to={'is_staff': True}, null=True,
                                blank=True, on_delete=models.PROTECT)

    approved = models.DateTimeField(verbose_name=_("approved"), null=True, blank=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), on_delete=models.PROTECT,null=True)

    alipay = models.ForeignKey(AlipayAccounts, verbose_name=_("alipay"), related_name="transaction_alipay_set", null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return str(_("Giao dịch:") + " %s : %s%s" % (self.pk,
                                                          "-" if self.from_balance_history and
                                                          not self.to_balance_history else "",
                                                          self.currency.display(self.amount)))

class BankAccount(models.Model):
    class Meta:
        verbose_name = _("BankAccount")
        verbose_name_plural = _("BankAccount")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    name = models.CharField(verbose_name=_("name"), max_length=512)
    bank_branch = models.CharField(verbose_name=_("bank_branch"), max_length=512,default='')
    bank_account = models.CharField(verbose_name=_("bank_account"), max_length=512)
    type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"), limit_choices_to={'is_vendorpayment': True},
                             on_delete=models.PROTECT)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS,
                                        decimal_places=XRATE_DECIMAL_PLACES, validators=[MinValueValidator(0)])

    account_holder = models.ForeignKey(User, verbose_name=_("account_holder"), null=True, blank=True,
                                       on_delete=models.PROTECT)


    # is_staff = models.BooleanField(verbose_name=_("is_staff"), default=False)

    def __str__(self):
        return str("%s" % (self.name))

class BalanceAccount(models.Model):
    class Meta:
        verbose_name = _("BalanceAccount")
        verbose_name_plural = _("BalanceAccount")
        unique_together = ("account_holder", "currency")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    name = models.CharField(verbose_name=_("name"), max_length=512)
    type = models.PositiveSmallIntegerField(verbose_name=_("type"), choices=BalanceType.ChoiceList(),
                                            default=BalanceType.bank, db_index=True)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT)
    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    account_holder = models.ForeignKey(User, verbose_name=_("account_holder"), null=True, blank=True,
                                       on_delete=models.PROTECT)
    metadata = models.TextField(verbose_name=_("metadata"), blank=True)
    info = models.TextField(verbose_name=_("info"), blank=True)
    # payment_uid = models.UUIDField(verbose_name=_("payment_uid"), unique=True, default=uuid.uuid4, editable=False)

    # is_staff = models.BooleanField(verbose_name=_("is_staff"), default=False)

    def __str__(self):
        return str("%s" % (self.account_holder.username))

class ReportBanks(models.Model):
    class Meta:
        verbose_name = _("ReportBanks")
        verbose_name_plural = _("ReportBanks")
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    note = models.TextField(verbose_name=_("note"), blank=True, default='')  # payment note
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)

    updated = models.DateTimeField(verbose_name=_("updated"), null=True, blank=True)

    def __str__(self):
        return str("%s" % (self.value))

class ReportBalance(models.Model):
    class Meta:
        verbose_name = _("ReportBalance")
        verbose_name_plural = _("ReportBalance")
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    note = models.TextField(verbose_name=_("note"), blank=True, default='')  # payment note

    type = models.ForeignKey("PaymentType", verbose_name=_("PaymentType"), limit_choices_to={'is_vendorpayment': True},
                             on_delete=models.PROTECT)
    group = models.CharField(verbose_name=_("group"), max_length=512)

    account = models.CharField(verbose_name=_("account"), max_length=512, blank=True, default='')

    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    deposit_amount = models.DecimalField(verbose_name=_("deposit_amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    paid_amount = models.DecimalField(verbose_name=_("paid_amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    refund_amount = models.DecimalField(verbose_name=_("refund_amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    def __str__(self):
        return str("%s" % (self.account))