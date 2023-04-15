#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  order_models.py
#
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#


import decimal
import json
import logging
import re
import uuid
from audit_log.models.fields import CreatingUserField, LastUserField
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, F, Count, Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .shop_models import Currency
from ..models import logistic_models
from user_module.models import UserProfile
from .customer_models import CustomerProfile
from ..constants.DefaultSettings import *
from ..enums import *
import datetime
from django.core.serializers import serialize
from system_configure.controllers import SystemConfigureController
from django.utils.functional import cached_property



CALCULATE_DATE = datetime.datetime.now().replace(month=8, day=1, hour=00, minute=00)


class HistoryOrder(models.Model):
    class Meta:
        verbose_name = _("HistoryOrder")
        verbose_name_plural = _("HistoryOrder")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")
    order = models.ForeignKey("Order", verbose_name=_("order"))

    details = models.TextField(verbose_name=_("details"), blank=True, null=True)

    def __str__(self):
        return self.details

class PromotionOrder(models.Model):
    class Meta:
        verbose_name = _("PromotionOrder")
        verbose_name_plural = _("PromotionOrder")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    from_date = models.DateTimeField(verbose_name=_("from_date"), null=True)

    to_date = models.DateTimeField(verbose_name=_("to_date"), null=True)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    percent = models.DecimalField(verbose_name=_("promotion_percent"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    weight_cost = models.DecimalField(verbose_name=_("weight_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    prepaid_rate = models.DecimalField(verbose_name=_("prepaid_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    def __str__(self):
        return self.from_date.strftime("%d-%m-%Y %H:%M")+'/'+self.to_date.strftime("%d-%m-%Y %H:%M")

class ExtraWeightCost(models.Model):
    class Meta:
        verbose_name = _("ExtraWeightCost")
        verbose_name_plural = _("ExtraWeightCost")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    from_date = models.DateTimeField(verbose_name=_("from_date"), null=True)

    to_date = models.DateTimeField(verbose_name=_("to_date"), null=True)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    percent = models.DecimalField(verbose_name=_("weight_percent"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    weight_cost = models.DecimalField(verbose_name=_("weight_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    prepaid_rate = models.DecimalField(verbose_name=_("prepaid_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    reduced = models.BooleanField(verbose_name=_("reduced"), default=False)

    def __str__(self):
        return str(self.from_date.strftime("%d-%m-%Y %H:%M")+'/'+self.to_date.strftime("%d-%m-%Y %H:%M"))

class ShipmentLeastCost(models.Model):
    class Meta:
        verbose_name = _("ShipmentLeastCost")
        verbose_name_plural = _("ShipmentLeastCost")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    from_date = models.DateTimeField(verbose_name=_("from_date"), null=True)

    to_date = models.DateTimeField(verbose_name=_("to_date"), null=True)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    # percent = models.DecimalField(verbose_name=_("promotion_percent"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
    #                     decimal_places=MONEY_DECIMAL_PLACES,
    #                     validators=[MinValueValidator(0)], db_index=True)

    weight_cost = models.DecimalField(verbose_name=_("weight_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                        decimal_places=MONEY_DECIMAL_PLACES,
                        validators=[MinValueValidator(0)], db_index=True)

    # prepaid_rate = models.DecimalField(verbose_name=_("prepaid_rate"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
    #                     decimal_places=MONEY_DECIMAL_PLACES,
    #                     validators=[MinValueValidator(0)], db_index=True)

    def __str__(self):
        return str(self.from_date.strftime("%d-%m-%Y %H:%M")+'/'+self.to_date.strftime("%d-%m-%Y %H:%M"))

class OrderPackageItem(models.Model):
    class Meta:
        verbose_name = _("OrderPackageItem")
        verbose_name_plural = _("OrderPackageItem")

    order_item = models.ForeignKey('OrderItem', verbose_name=_("order_item"), null=True, blank=True)

    order_package = models.ForeignKey('OrderPackage', verbose_name=_("order_package"), null=True, blank=True)

    shipment_package = models.ForeignKey('ShipmentPackage', verbose_name=_("shipment_package"), null=True, blank=True)

    order = models.ForeignKey('Order', verbose_name=_("order"), related_name='OrderPackageItem_order_set', null=True,
                              blank=True)

    def __str__(self):
        return str(self.order_item)[:100]


class AlipayAccounts(models.Model):
    class Meta:
        verbose_name = _("AlipayAccounts")
        verbose_name_plural = _("AlipayAccounts")
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    note = models.TextField(verbose_name=_("note"), blank=True, default='')  # payment note
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    amount = models.DecimalField(verbose_name=_("amount"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                 decimal_places=MONEY_DECIMAL_PLACES,
                                 validators=[MinValueValidator(0)], db_index=True)
    def __str__(self):
        return str("%s" % (self.value))

class OrderPackage(models.Model):
    class Meta:
        verbose_name = _("OrderPackage")
        verbose_name_plural = _("OrderPackage")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    order = models.ForeignKey("Order", verbose_name=_("order"), null=True, blank=True)

    order_item = models.ManyToManyField('OrderItem', verbose_name=_("order_item"),
                                        related_name='OrderPackage_order_item_set', through='OrderPackageItem')

    shipmentpackage = models.ManyToManyField('ShipmentPackage', verbose_name=_("OrderPackage_shipmentpackage"),
                                             related_name='OrderPackage_shipmentpackage_set',
                                             through='OrderPackageItem')

    price = models.DecimalField(verbose_name=_("orderpackage_price"), default=decimal.Decimal(0),max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    shipping = models.DecimalField(verbose_name=_("orderpackage_shipping"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    price_real = models.DecimalField(verbose_name=_("orderpackage_price_real"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)
    earn_price = models.DecimalField(verbose_name=_("orderpackage_earn_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    price_refund = models.DecimalField(verbose_name=_("orderpackage_price_refund"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)


    status = models.ForeignKey("Status", verbose_name=_("status"), on_delete=models.PROTECT, null=True, blank=True)

    tracking_number = models.CharField(verbose_name=_("tracking_number"), blank=True, max_length=512, db_index=True,
                                       null=True)

    order_number = models.CharField(verbose_name=_("order_number"), blank=True, max_length=512, db_index=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    exchange_rate_org = models.DecimalField(verbose_name=_("exchange_rate_org"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    inventory_employee = models.ForeignKey(User, verbose_name=_("inventory_employee"),
                                           limit_choices_to={'is_staff': True}, null=True, blank=True,
                                           on_delete=models.SET_NULL)

    alipay = models.ForeignKey(AlipayAccounts, verbose_name=_("alipay"), null=True, blank=True, on_delete=models.SET_NULL)

    note = models.TextField(verbose_name=_("note"), blank=True)

    refunded = models.BooleanField(verbose_name=_("refunded"), default=False)

    paid = models.BooleanField(verbose_name=_("paid"), default=False)

    payment_late = models.BooleanField(verbose_name=_("payment_late"), default=False)

    flag = models.BooleanField(verbose_name=_("flag"), default=False)

    rocket = models.BooleanField(verbose_name=_("rocket"), default=False)

    paid_date = models.DateTimeField(verbose_name=_("paid Date"), null=True, blank=True)

    pending_date = models.DateTimeField(verbose_name=_("pending Date"), null=True, blank=True)


    def __str__(self):
        return str("[%s] (%s)" % (self.pk, str(self.tracking_number)))

    @property
    def first_image_url(self):
        item_objs = self.order_item.exclude(Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved'))
        if item_objs.exists():
            return item_objs.first().image_url
        else:
            return ''

    @property
    def total_refund_price(self):
        _sum_refund_price = self.refundcharge_set.exclude(status__value='unapproved').all().aggregate(
            _sum_price=Sum(F('price')),
            _count=Sum(F('id')),
        )
        if not _sum_refund_price['_sum_price']:
            sum_refund = 0
        else:
            sum_refund = _sum_refund_price['_sum_price']
        return sum_refund

    @property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created

    @property
    def paid_date_tag(self):
        if self.paid_date:
            return self.paid_date.strftime("%d-%m-%Y %H:%M")
        else:
            return self.paid_date

    @property
    def item_count(self):
        return self.order_item.count()

    @property
    def total_item_price(self):
        _sum_item_price = self.order_item.exclude(
            Q(status__value='unapproved')|Q(status__value='canceled')|Q(status__value='Failed')).all().distinct().aggregate(
            _sum_price=Sum((F('price') * F('quantity'))+F('shipping'),distinct=True ,output_field=models.DecimalField(),),
            _count=Count(F('id')),
        )
        if not _sum_item_price['_sum_price']:
            item_price = 0
        else:
            item_price = _sum_item_price['_sum_price']
        return item_price

    @property
    def total_order_number_price(self):
        list_item = self.order_item.exclude(
            Q(status__value='unapproved')|Q(status__value='canceled')|Q(status__value='Failed')).all().distinct()
        _sum_orderpackage_price = OrderPackage.objects.exclude(
            Q(status__value='unapproved')|Q(status__value='canceled')|Q(status__value='Failed')).filter(order_item__in=list_item).distinct().aggregate(
            _sum_price=Sum(F('price'), output_field=models.DecimalField(),distinct=True),
            _count=Sum(F('id'),distinct=True),
        )
        if not _sum_orderpackage_price['_sum_price']:
            item_price = 0
        else:
            item_price = _sum_orderpackage_price['_sum_price']
        return item_price

    @property
    def date_waiting(self):
        date_waiting = (datetime.datetime.today() - self.created).days
        return date_waiting
    @property
    def tracking_count(self):
        return self.shipmentpackage.distinct().count()

class Order(models.Model):

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Order")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT)
    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="order_customer_set",
                                 on_delete=models.PROTECT)

    customer_note = models.TextField(verbose_name=_("customer_note"), blank=True)

    note = models.TextField(verbose_name=_("note"), blank=True)
    # TODO:note that if set editable=False it will not show up in admin and api so use it wisely
    # payment_uid = models.UUIDField(verbose_name=_("payment_uid"), unique=True, default=uuid.uuid4, editable=False, max_length=255)

    delivery_method = models.PositiveSmallIntegerField(verbose_name=_("delivery_method"),
                                                       choices=DeliveryMethod.ChoiceList(),
                                                       default=DeliveryMethod.store_pickup, db_index=True)
    delivery_address = models.CharField(verbose_name=_("delivery_address"), blank=True, max_length=512, db_index=True)
    city = models.CharField(verbose_name=_("city"), blank=True, max_length=512, db_index=True)
    district = models.CharField(verbose_name=_("district"), blank=True, max_length=512, db_index=True)
    street = models.CharField(verbose_name=_("street"), blank=True, max_length=512, db_index=True)
    receiver_name = models.CharField(verbose_name=_("receiver_name"), blank=True, max_length=512, db_index=True)
    receiver_phone = models.CharField(verbose_name=_("receiver_phone"), blank=True, max_length=512, db_index=True)

    prepaid_percent = models.PositiveSmallIntegerField(verbose_name=_("prepaid_percent"), default=0, db_index=True,
                                                       validators=[MinValueValidator(0), MaxValueValidator(100)])

    discount = models.BooleanField(verbose_name=_("discount"), default=False)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])
    extra_charge = models.DecimalField(verbose_name=_("extra_charge"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)
    tax_cost = models.DecimalField(verbose_name=_("tax_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)

    amount_payment_left = models.DecimalField(verbose_name=_("amount_payment_left"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)

    amount_need_to_pay = models.DecimalField(verbose_name=_("amount_need_to_pay"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)
    amount_order_profit = models.DecimalField(verbose_name=_("amount_order_profit"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)

    order_weight = models.DecimalField(verbose_name=_("order_weight"), default=decimal.Decimal(0), max_digits=9,
                                       decimal_places=2)

    cost_by_weight = models.DecimalField(verbose_name=_("cost_by_weight"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    cost_per_weight = models.DecimalField(verbose_name=_("cost_per_weight"), default=decimal.Decimal(0),
                                          max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                          validators=[MinValueValidator(0)], db_index=True)

    prepaid_date = models.DateTimeField(verbose_name=_("Prepaid Date"), null=True, blank=True)

    ordered_date = models.DateTimeField(verbose_name=_("Ordered Date"), null=True, blank=True)

    completed_date = models.DateTimeField(verbose_name=_("Completed Date"), null=True, blank=True)

    arrived_date = models.DateTimeField(verbose_name=_("Arrived Date"), null=True, blank=True)

    shiptovn_date = models.DateTimeField(verbose_name=_("ShipToVN Date"), null=True, blank=True)

    ordered_by = models.ForeignKey(User, verbose_name=_("ordered_by"), related_name="ordered_by_set",
                                   on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    checked_by = models.ForeignKey(User, verbose_name=_("checked_by"), related_name="checked_by_set",
                                   on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    referer_by = models.ForeignKey(User, verbose_name=_("referer_by"), related_name="referer_by_set",
                                   on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    takecare_by = models.ForeignKey(User, verbose_name=_("takecare_by"), related_name="takecare_by_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)
    flag = models.BooleanField(verbose_name=_("flag"), default=False)

    stop_refund = models.BooleanField(verbose_name=_("stop_refund"), default=False)

    check_commission = models.BooleanField(verbose_name=_("check_commission"), default=False)

    commission = models.BooleanField(verbose_name=_("commission"), default=False)


    def __str__(self):
        try:
            return str("#%s (%s)" % (self.id, str(self.status)))
        except Exception as e:
            print(e)
            return str("#%s" % self.id)

    def reload(self):
        new_self = self.__class__.objects.get(pk=self.pk)
        # You may want to clear out the old dict first or perform a selective merge
        self.__dict__.update(new_self.__dict__)

    @property
    def total_extra_price(self):
        sum_extra_price = self.extracharge_set.filter().aggregate(
            _sum_price=Sum(F('price')),
            _count=Sum(F('id')),
        )
        if not sum_extra_price['_sum_price']:
            sum_extra = 0
        else:
            sum_extra = sum_extra_price['_sum_price']
        return sum_extra + self.extra_charge

    @cached_property
    def first_image_url(self):
        return self.orderitem_set.first().image_url

    @property
    def rocket(self):
        return self.orderitem_set.filter(rocket=True).count()

    @property
    def service(self):
        return self.orderitem_set.filter(service=True).count()

    @property
    def prepaid_date_tag(self):
        if self.prepaid_date:
            return self.prepaid_date.strftime("%d-%m-%Y %H:%M")
        else:
            return self.prepaid_date

    @property
    def ordered_date_tag(self):
        if self.ordered_date:
            return self.ordered_date.strftime("%d-%m-%Y %H:%M")
        else:
            return self.ordered_date

    @cached_property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created

    @cached_property
    def full_name(self):
        user_profile = UserProfile.objects.filter(user=self.customer)
        if user_profile:
            return user_profile[0].full_name
        return None

    @property
    def status_processing(self):
        status_value = self.status.value
        order_items = self.orderitem_set.all().aggregate(
            _count_items=Count(F('id')),
            _sum_items_quantity=Sum(F('quantity')),
        )
        if status_value == 'checked' or status_value == 'delivered_ship':
            arrived_item = logistic_models.ArrivedItem.objects.filter(
                order_item__in=self.orderitem_set.all()).aggregate(
                _count_items=Count(F('id')),
                _sum_arrived_quantity=Sum(F('arrived_quantity')),
            )
            item_status_quantity = arrived_item['_sum_arrived_quantity']
        else:
            order_item_status = self.orderitem_set.filter(status__value=status_value).aggregate(
                _count_items=Count(F('id')),
                _sum_items_quantity=Sum(F('quantity')),
            )
            item_status_quantity = order_item_status['_sum_items_quantity']
        if not item_status_quantity:
            item_status_quantity = 0
        order_items_quantity = order_items['_sum_items_quantity']
        if not order_items_quantity:
            order_items_quantity = 0
        return self.status.label+'[' + str(item_status_quantity) + '/' + str(order_items_quantity) + ']'

    @cached_property
    def facebook_name(self):
        user_profile = UserProfile.objects.filter(user=self.customer)
        if user_profile:
            return user_profile[0].user_facebook
        return None

    @cached_property
    def address_tag(self):
        return str("%s %s, %s" % (self.delivery_address, self.district, self.city))

    @property
    def extra_charge_tag(self):
        return self.currency.display(self.extra_charge)

    @cached_property
    def tax_cost_tag(self):
        return self.currency.display(self.tax_cost)


    def calculate_order_number(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.orderpackage_set.filter(paid=True).distinct().aggregate(
            _count_orderpackage=Count(F('id'), distinct=True),
            _sum_orderpackage_price=Sum(F('price')),
            _sum_orderpackage_price_vnd=Sum(F('price') * F('exchange_rate')),
            _sum_orderpackage_price_vnd_org=Sum(F('price') * F('exchange_rate_org')),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)

    def calculate_refund_charge(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = Refundcharge.objects.exclude(status__value='unapproved').filter(orderpackage__in=self.orderpackage_set.all()).distinct().aggregate(
            _count_refundcharge=Count(F('id'), distinct=True),
            _sum_refundcharge_price=Sum(F('price')),
            _sum_refundcharge_price_vnd=Sum(F('price') * F('exchange_rate')),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)


    def calculate_shipment_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP

        result = self.shipmentpackage_set.filter(orderpackageitem__order_item__isnull=False).exclude(Q(status__logic_step=LogicStep.failed)|Q(status__value='unapproved')).distinct().aggregate(
            _count_shipment=Count(F('id')),
            _sum_shipment_weight=Sum(F('weight')),
            _sum_shipment_cost=Sum(F('weight') * F('weight_cost')),
            _sum_shipment_cost_org=Sum(F('weight') * F('weight_cost_org') * F('exchange_rate')),
            _sum_shipment_payment_late_cost=Sum(F('payment_late_cost') * F('exchange_rate')),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)

    def calculate_order_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.orderitem_set.all().exclude(status__logic_step=LogicStep.failed).aggregate(
            _count_item=Count(F('id')),
            _count_quantity=Sum(F('quantity'), output_field=models.DecimalField()),
            _sum_item_price=Sum(F('price') * F('quantity'),output_field=models.DecimalField()),
            _sum_item_order_price=Sum(F('order_price') * F('order_quantity'),output_field=models.DecimalField()),
            _sum_item_order_price_vnd=Sum(F('order_price') * F('order_quantity') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_cost=Sum(F('price') * F('quantity') * F('exchange_rate')),
            _sum_item_shipping=Sum(F('shipping') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_shipping_orig=Sum(F('shipping'),output_field=models.DecimalField()),
            _sum_item_insurance_charge=Sum(F('insurance_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_insurance_charge_orig=Sum('insurance_charge',output_field=models.DecimalField()),
            _sum_item_bargain_charge=Sum(F('bargain_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_bargain_charge_orig=Sum('bargain_charge',output_field=models.DecimalField()),
            _sum_item_rocket_charge=Sum(F('rocket_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_rocket_charge_orig=Sum('rocket_charge',output_field=models.DecimalField()),
            _sum_item_rocket_ship_charge=Sum(F('rocket_ship_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_rocket_ship_charge_orig=Sum('rocket_ship_charge',output_field=models.DecimalField()),

            _sum_item_packing_charge=Sum(F('packing_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_packing_charge_orig=Sum('packing_charge'),
            _sum_item_service_charge=Sum(F('service_charge') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_service_charge_orig=Sum('service_charge',output_field=models.DecimalField()),
            _sum_item_total_service_cost=Sum(
                (F('insurance_charge') + F('service_charge') + F('rocket_charge') + F('packing_charge') + F('bargain_charge') + F('rocket_ship_charge')) * F(
                    'exchange_rate'),output_field=models.DecimalField()),
            _sum_item_total_service_cost_orig=Sum(
                F('service_charge') + F('rocket_charge') + F('packing_charge') + F('insurance_charge') + F('bargain_charge') + F('rocket_ship_charge'),output_field=models.DecimalField()),
            _sum_item_tax_cost=Sum(F('tax_cost') * F('exchange_rate'),output_field=models.DecimalField()),
            _sum_item_weight=Sum(F('weight'),output_field=models.DecimalField()),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)

    def calculate_sum_by_currency(self):
        sum_by_currency = self.orderitem_set.all().exclude(status__logic_step=LogicStep.failed).values(
            'currency').annotate(
            sum_item_cost=Sum(F('price') * F('quantity'), output_field=models.DecimalField()),
            sum_shipping=Sum(F('shipping'), output_field=models.DecimalField()),
            sum_order_item_cost=Sum(F('order_price') * F('order_quantity'), output_field=models.DecimalField()),
            sum_order_shipping_cost=Sum(F('order_shipping'), output_field=models.DecimalField()),
            sum_order_quantity=Sum(F('order_quantity'), output_field=models.PositiveIntegerField()),
            sum_quantity=Sum(F('quantity'), output_field=models.PositiveIntegerField()),
            sum_item=Count(F('id')),
            exchange_rate=F('exchange_rate'),
            sum_service_charge=Sum(F('service_charge'), output_field=models.DecimalField()),
            sum_insurance_charge=Sum(F('insurance_charge'), output_field=models.DecimalField()),
            sum_rocket_charge=Sum(F('rocket_charge'), output_field=models.DecimalField()),
            sum_packing_charge=Sum(F('packing_charge'), output_field=models.DecimalField()),
            sum_bargain_charge=Sum(F('bargain_charge'), output_field=models.DecimalField()),
            total_service_cost=Sum(
                F('service_charge') + F('insurance_charge') + F('rocket_charge') + F('packing_charge') + F('bargain_charge'),
                output_field=models.DecimalField()),
            sum_tax_cost=Sum(F('tax_cost'), output_field=models.DecimalField()),
        )
        try:
            for sum_cur in sum_by_currency:
                sum_cur['sum_total'] = sum_cur['sum_item_cost'] + sum_cur['sum_shipping'] + \
                                       sum_cur['sum_service_charge'] + sum_cur['sum_tax_cost'] + sum_cur['sum_insurance_charge']+sum_cur['sum_rocket_charge']+sum_cur['sum_packing_charge']+sum_cur['sum_bargain_charge']

                sum_cur['sum_order_cost'] = sum_cur['sum_order_item_cost'] + sum_cur['sum_order_shipping_cost']
        except Exception as e:
            logging.debug('SQL annotate error: %s' % e)
            self._sum_by_currency = []
        else:
            self._sum_by_currency = sum_by_currency

    @property
    def sum_refundcharge_price(self):
        if not hasattr(self, '_sum_refundcharge_price'):
            self.calculate_refund_charge()
        if self._sum_refundcharge_price:

            return self._sum_refundcharge_price
        else:
            return decimal.Decimal(0)

    @property
    def sum_refundcharge_price_vnd(self):
        if not hasattr(self, '_sum_refundcharge_price_vnd'):
            self.calculate_refund_charge()
        if self._sum_refundcharge_price_vnd:

            return self._sum_refundcharge_price_vnd
        else:
            return decimal.Decimal(0)

    @property
    def sum_orderpackage_price(self):
        if not hasattr(self, '_sum_orderpackage_price'):
            self.calculate_order_number()
        if self._sum_orderpackage_price:

            return self._sum_orderpackage_price
        else:
            return decimal.Decimal(0)

    @property
    def sum_shipment_cost_org(self):
        if not hasattr(self, '_sum_shipment_cost_org'):
            self.calculate_shipment_item()
        if self._sum_shipment_cost_org:
            # if self._sum_shipment_cost_org == 0:
            #     return self.sum_shipment_cost
            return self._sum_shipment_cost_org
        else:
            return self.sum_shipment_cost

    @property
    def sum_orderpackage_price_vnd(self):
        if not hasattr(self, '_sum_orderpackage_price_vnd'):
            self.calculate_order_number()
        if self._sum_orderpackage_price_vnd:

            return self._sum_orderpackage_price_vnd
        else:
            return decimal.Decimal(0)

    @property
    def sum_orderpackage_price_vnd_org(self):
        if not hasattr(self, '_sum_orderpackage_price_vnd_org'):
            self.calculate_order_number()
        if self._sum_orderpackage_price_vnd_org:

            return self._sum_orderpackage_price_vnd_org
        else:
            return decimal.Decimal(0)


    # @property
    # def sum_orderpackage_price_vnd(self):
    #     if not hasattr(self, '_sum_orderpackage_price_vnd'):
    #         self.calculate_order_number()
    #     if self._sum_orderpackage_price_vnd:
    #
    #         return self._sum_orderpackage_price_vnd
    #     else:
    #         return 0



    @property
    def sum_shipment_cost(self):
        if not hasattr(self, '_sum_shipment_cost'):
            self.calculate_shipment_item()
        if self._sum_shipment_cost:

            # if self.prepaid_date:
            #     list_shipment_least_cost = ShipmentLeastCost.objects.filter(from_date__gte=self.prepaid_date)
            # else:
            #     list_shipment_least_cost = None
            # if list_shipment_least_cost:
            #     if list_shipment_least_cost[0].weight_cost > self._sum_shipment_cost:
            #         return list_shipment_least_cost[0].weight_cost
            #     else:
            #         return self._sum_shipment_cost
            # else:
                # company_information = SystemConfigureController.getConfigure('company_information')
                #
                # list_site_minimum_cost = ['sieutoc365.com', 'tmallviet.com']
                # if company_information['Website'] in list_site_minimum_cost and self._sum_shipment_weight < 5:
                #     return decimal.Decimal(90000)
            return self._sum_shipment_cost
        else:
            return decimal.Decimal(0)

    @property
    def sum_shipment_weight(self):
        if not hasattr(self, '_sum_shipment_weight'):
            self.calculate_shipment_item()
        if self._sum_shipment_weight:
            return self._sum_shipment_weight
        else:
            return decimal.Decimal(0)

    @property
    def order_profit(self):
        return self.total_item_cost - self.sum_orderpackage_price_vnd_org - self.sum_shipment_cost_org - self.total_extra_price - self.sum_shipment_payment_late_cost + self.sum_refundcharge_price_vnd

    @property
    def sum_shipment_payment_late_cost(self):
        if not hasattr(self, '_sum_shipment_payment_late_cost'):
            self.calculate_shipment_item()
        if self._sum_shipment_payment_late_cost:
            return self._sum_shipment_payment_late_cost
        else:
            return decimal.Decimal(0)

    @property
    def sum_item_order_price(self):
        if not hasattr(self, '_sum_item_order_price'):
            self.calculate_order_item()
        if self._sum_item_order_price:
            return self._sum_item_order_price
        else:
            return 0
    @property
    def sum_item_price(self):
        if not hasattr(self, '_sum_item_price'):
            self.calculate_order_item()
        if self._sum_item_price:
            return self._sum_item_price
        else:
            return 0
    @property
    def count_items(self):
        # if not hasattr(self, '_count_shipment'):
        #     self.calculate_shipment_item()
        # if self._count_shipment:
        #     return self._count_shipment
        # else:
        #     return 0
        count_items = self.orderitem_set.count()
        if count_items:
            return count_items
        else:
            return 0
    @property
    def count_shipment(self):
        # if not hasattr(self, '_count_shipment'):
        #     self.calculate_shipment_item()
        # if self._count_shipment:
        #     return self._count_shipment
        # else:
        #     return 0
        shipment_count = self.orderitem_set.aggregate(count=Count(F('shipmentpackage'), distinct=True))
        if shipment_count:
            return shipment_count['count']
        else:
            return 0

    @property
    def count_item(self):
        if not hasattr(self, '_count_item'):
            self.calculate_order_item()
        try:
            return int(self._count_item)
        except Exception as e:
            # print(e)
            return 0

    @property
    def count_quantity(self):
        if not hasattr(self, '_count_quantity'):
            self.calculate_order_item()
        try:
            return int(self._count_quantity)
        except Exception as e:
            # print(e)
            return 0


    @property
    def sum_item_cost(self):
        if not hasattr(self, '_sum_item_cost'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_cost, self.exchange_rate)

    @property
    def sum_item_shipping_orig(self):
        if not hasattr(self, '_sum_item_shipping_orig'):
            self.calculate_order_item()
        try:
            return self._sum_item_shipping_orig
        except Exception as e:
            # print(e)
            return 0

    @property
    def sum_item_shipping(self):
        if not hasattr(self, '_sum_item_shipping'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_shipping, self.exchange_rate)

    @property
    def sum_item_service_charge(self):
        if not hasattr(self, '_sum_item_service_charge'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_service_charge, self.exchange_rate)

    @property
    def sum_item_service_charge_orig(self):
        if not hasattr(self, '_sum_item_service_charge_orig'):
            self.calculate_order_item()
        try:
            return self._sum_item_service_charge_orig
        except Exception as e:
            # print(e)
            return 0


    @property
    def sum_item_rocket_charge_orig(self):
        if not hasattr(self, '_sum_item_rocket_charge_orig'):
            self.calculate_order_item()
        try:
            return int(self._sum_item_rocket_charge_orig)
        except Exception as e:
            # print(e)
            return 0

    @property
    def sum_item_rocket_charge(self):
        if not hasattr(self, '_sum_item_rocket_charge'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_rocket_charge, self.exchange_rate)


    @property
    def sum_item_bargain_charge_orig(self):
        if not hasattr(self, '_sum_item_bargain_charge_orig'):
            self.calculate_order_item()
        try:
            return self._sum_item_bargain_charge_orig
        except Exception as e:
            # print(e)
            return 0

    @property
    def sum_item_bargain_charge(self):
        if not hasattr(self, '_sum_item_bargain_charge'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_bargain_charge, self.exchange_rate)

    @property
    def sum_item_packing_charge(self):
        if not hasattr(self, '_sum_item_packing_charge'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_packing_charge, self.exchange_rate)

    @property
    def sum_item_insurance_charge_orig(self):
        if not hasattr(self, '_sum_item_insurance_charge_orig'):
            self.calculate_order_item()
        try:
            return self._sum_item_insurance_charge_orig
        except Exception as e:
            # print(e)
            return decimal.Decimal(0)
    @property
    def sum_item_insurance_charge(self):
        if not hasattr(self, '_sum_item_insurance_charge'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_insurance_charge, self.exchange_rate)

    @property
    def sum_item_total_service_cost_orig(self):
        if not hasattr(self, '_sum_item_total_service_cost_orig'):
            self.calculate_order_item()
        try:
            return self._sum_item_total_service_cost_orig
        except Exception as e:
            # print(e)
            return decimal.Decimal(0)

    @property
    def order_discount(self):
        company_information = SystemConfigureController.getConfigure('company_information')
        discount = 0
        if company_information['Website'] == 'taobao365.vn' or company_information['Website'] == 'chuyenhang365.com':
            if self.sum_item_cost <= 2000000:
                discount = 0
            elif decimal.Decimal(2000000) < self.sum_item_cost <= decimal.Decimal(5000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.1)
            elif decimal.Decimal(5000000) < self.sum_item_cost <= decimal.Decimal(10000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.2)
            elif decimal.Decimal(10000000) < self.sum_item_cost <= decimal.Decimal(15000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.3)
            elif decimal.Decimal(15000000) < self.sum_item_cost <= decimal.Decimal(20000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.4)
            elif decimal.Decimal(20000000) < self.sum_item_cost <= decimal.Decimal(30000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.5)
            elif decimal.Decimal(30000000) < self.sum_item_cost <= decimal.Decimal(55000000):
                discount = self.sum_item_service_charge * decimal.Decimal(0.7)
            elif decimal.Decimal(55000000) < self.sum_item_cost:
                discount = self.sum_item_service_charge * 1
        return round(decimal.Decimal(discount),2)

    @property
    def sum_item_total_service_cost(self):
        if not hasattr(self, '_sum_item_total_service_cost'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_total_service_cost, self.exchange_rate)

    @property
    def sum_item_tax_cost(self):
        if not hasattr(self, '_sum_item_tax_cost'):
            self.calculate_order_item()
        return Currency.Invert(self._sum_item_tax_cost, self.exchange_rate)

    @property
    def sum_by_currency(self):
        if not hasattr(self, '_sum_by_currency'):
            self.calculate_sum_by_currency()
        return self._sum_by_currency

    def count_item_tag(self):
        return str(self.count_item)

    count_item_tag.short_description = _("Count Item")

    @property
    def sum_cost_by_weight(self):
        return self.order_weight * (self.cost_per_weight * 1000)

    def sum_cost_by_weight_tag(self):
        return self.currency.display(self.order_weight * (self.cost_per_weight * 1000))

    sum_cost_by_weight_tag.short_description = _('Sum Cost By Weight')

    def sum_item_cost_tag(self):
        return self.currency.display(self.sum_item_cost)

    sum_item_cost_tag.short_description = _('Sum item cost')

    def sum_item_shipping_tag(self):
        return self.currency.display(self.sum_item_shipping)

    sum_item_shipping_tag.short_description = _('Sum item shipping')

    def sum_item_insurance_charge_tag(self):
        return self.currency.display(self.sum_item_insurance_charge)

    sum_item_insurance_charge_tag.short_description = _('Sum item insurance')

    def sum_item_service_charge_tag(self):
        return self.currency.display(self.sum_item_service_charge)

    sum_item_service_charge_tag.short_description = _('Sum item service')

    def sum_item_service_charge_orig_tag(self):
        return str(self._sum_item_service_charge_orig) + ' CNY'

    sum_item_service_charge_orig_tag.short_description = _('Sum item service origin')

    @property
    def total_item_cost(self):
        return self.sum_item_cost + self.sum_item_shipping + self.sum_item_total_service_cost+ self.sum_item_tax_cost + self.sum_shipment_cost + self.sum_shipment_payment_late_cost + self.total_extra_price - self.order_discount


    @property
    def total_item_cost_not_shipment(self):
        return self.sum_item_cost + self.sum_item_shipping + self.sum_item_total_service_cost+ self.sum_item_tax_cost - self.order_discount


    def total_item_cost_tag(self):
        return self.currency.display(self.total_item_cost)

    total_item_cost_tag.short_description = _('Total item cost')

    @property
    def total_cost(self):
        return self.total_item_cost


    def total_cost_tag(self):
        return self.currency.display(self.total_cost)

    total_cost_tag.short_description = _('Total cost')

    @property
    def order_vip_status(self):
        customer = CustomerProfile.objects.get(user_id=self.customer.id)
        return customer.vip_status

    @property
    def reduce_cost(self):
        if self.created < CALCULATE_DATE.replace(tzinfo=self.created.tzinfo):
            return 0
        extras = self.tax_cost + self.sum_cost_by_weight
        if self.order_vip_status == 0:
            return 0
        elif self.order_vip_status == 1:
            return extras * 5 / 100
        elif self.order_vip_status == 2:
            return extras * 10 / 100
        return extras * 20 / 100

    @property
    def extras(self):
        extras = self.tax_cost + self.sum_cost_by_weight
        return extras - self.reduce_cost

    @property
    def grant_total(self):
        # todo: calculate ShipmentPackage shipping_cost
        return self.total_cost + self.extras

    @property
    def prepaid(self):
        return self.total_cost * self.prepaid_percent / 100

    def prepaid_tag(self):
        return self.currency.display(self.prepaid)

    prepaid_tag.short_description = _('Prepaid')

    def redude_cost_tag(self):
        return ' -' + self.currency.display(self.reduce_cost)

    redude_cost_tag.short_description = _('VIP')

    def grant_total_tag(self):
        return self.currency.display(self.grant_total)

    grant_total_tag.short_description = _('Grant total')

    @property
    def order_cost(self):
        result = 0
        for sum_cur in self.sum_by_currency:
            result += sum_cur['sum_order_cost']
        return result

    def latest_transaction_date(self):
        result = self.customerpayment_set.last()
        return result.created if result else None

    latest_transaction_date.short_description = _('Transaction Date')

    def order_cost_tag(self):
        result = ''
        for sum_cur in self.sum_by_currency:
            result += '%s%s ' % (sum_cur['sum_order_cost'], sum_cur['currency'])
        return result

    order_cost_tag.short_description = _('Order Cost')

    def sum_total(self):
        sum_total = 0
        for sum_cur in self.sum_by_currency:
            sum_total += sum_cur['sum_total']
        return sum_total

    def calculate_payments(self):
        result = self.customerpayment_set.all()
        total_amount_transaction = 0
        for r in result:
            if r.transaction.status.value != 'unapproved':
                amount_t = r.transaction.amount * r.transaction.exchange_rate
                total_amount_transaction += amount_t
        setattr(self, '_sum_payment_transaction', total_amount_transaction)
        setattr(self, '_count_payment', result.count())

    def ship_to_vn(self):
        return str(self.orderitem_set.filter(status__value='ShipToVN').count()) \
               + '/' + \
               str(self.orderitem_set.all().exclude(status__value='Failed').count())

    ship_to_vn.short_description = _("ShipToVN")

    @property
    def PrePaid_count(self):
        return self.orderitem_set.filter(status__value='PrePaid').count()
    @property
    def checked_vn(self):
        return self.orderitem_set.filter(status__value='checked').count()


    def calculate_sum_checked_vn(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.orderitem_set.filter(status__logic_step= LogicStep.completed).exclude(status__logic_step=LogicStep.failed).aggregate(
            _count_item_checked_vn=Count(F('id')),
            _count_quantity_checked_vn=Count(F('quantity')),
            _sum_item_cost_checked_vn=Sum(F('price') * F('quantity') * F('exchange_rate')),
            _sum_item_shipping_checked_vn=Sum(F('shipping') * F('exchange_rate')),
            _sum_item_insurance_charge_checked_vn=Sum(F('insurance_charge') * F('exchange_rate')),
            _sum_item_insurance_charge_orig_checked_vn=Sum('insurance_charge'),
            _sum_item_rocket_charge_checked_vn=Sum(F('rocket_charge') * F('exchange_rate')),
            _sum_item_rocket_charge_orig_checked_vn=Sum('rocket_charge'),
            _sum_item_rocket_ship_charge_checked_vn=Sum(F('rocket_ship_charge') * F('exchange_rate')),
            _sum_item_rocket_ship_charge_orig_checked_vn=Sum('rocket_ship_charge'),
            _sum_item_packing_charge_checked_vn=Sum(F('packing_charge') * F('exchange_rate')),
            _sum_item_packing_charge_orig_checked_vn=Sum('packing_charge'),
            _sum_item_service_charge_checked_vn=Sum(F('service_charge') * F('exchange_rate')),
            _sum_item_service_charge_orig_checked_vn=Sum('service_charge'),

            _sum_item_total_service_cost_checked_vn=Sum(
                (F('insurance_charge') + F('service_charge') + F('rocket_charge') + F('packing_charge') + F('bargain_charge') + F('rocket_ship_charge')) * F(
                    'exchange_rate')),
            _sum_item_total_service_cost_orig_checked_vn=Sum(
                F('service_charge') + F('rocket_charge') + F('packing_charge') + F('insurance_charge') + F('bargain_charge')),
            _sum_item_tax_cost_checked_vn=Sum(F('tax_cost') * F('exchange_rate')),
            _sum_item_total_item_cost_checked_vn=Sum((F('price') * F('quantity') + F('shipping') + F('insurance_charge') + F('service_charge') + F('rocket_charge') + F('packing_charge') + F('tax_cost')+ F('bargain_charge') + F('rocket_ship_charge')) * F('exchange_rate')),
            _sum_item_weight_checked_vn=Sum(F('weight')),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)


    @property
    def sum_quantity_item_checked_vn(self):
        result_checked_item = self.orderitem_set.filter().exclude(
            status__value='WaitingForPrePaid').exclude(
            status__value='canceled').exclude(
            status__value='Failed').exclude(
            status__value='unapproved')
        total_quantity_item_checked = sum([i.quantity for i in result_checked_item if i.sum_arrived_quantity > 0])
        return total_quantity_item_checked

    @property
    def sum_quantity_item_arrived(self):
        result_checked_item = self.orderitem_set.filter().exclude(
            status__value='WaitingForPrePaid').exclude(
            status__value='canceled').exclude(
            status__value='Failed').exclude(
            status__value='unapproved')
        total_quantity_item_arrived = sum([i.sum_arrived_quantity for i in result_checked_item if i.sum_arrived_quantity > 0])
        return total_quantity_item_arrived

    @property
    def sum_item_total_item_cost_checked_vn(self):
        result_checked_item = self.orderitem_set.filter().exclude(
            status__value='WaitingForPrePaid').exclude(
            status__value='canceled').exclude(
            status__value='Failed').exclude(
            status__value='unapproved')
        total_vnd_item_checked = sum([i.total_vnd for i in result_checked_item if i.sum_arrived_quantity > 0])
        return total_vnd_item_checked


    @property
    def count_payment(self):
        if not hasattr(self, '_count_payment'):
            self.calculate_payments()
        return self._count_payment

    @property
    def sum_payment_transaction(self):
        if not hasattr(self, '_sum_payment_transaction'):
            self.calculate_payments()
        return Currency.Invert(self._sum_payment_transaction, self.exchange_rate)

    def sum_payment_transaction_tag(self):
        return self.currency.display(self.sum_payment_transaction)

    sum_payment_transaction_tag.short_description = _('Payment total')


    @property
    def payment_left(self):
        return round(self.grant_total,0) - round(self.sum_payment_transaction,0)

    @property
    def need_to_pay(self):
        if decimal.Decimal(self.prepaid_percent) > decimal.Decimal(0):
            prepaid_rate = decimal.Decimal(self.prepaid_percent)/100
        else:
            try:
                prepaid_rate = decimal.Decimal(self.customer.customerProfile.prepaid_rate)
            except:
                prepaid_rate = decimal.Decimal(0.7)
            else:
                if prepaid_rate > decimal.Decimal(0):
                    prepaid_rate = decimal.Decimal(self.customer.customerProfile.prepaid_rate) / decimal.Decimal(
                            100)
                else:
                    prepaid_rate = decimal.Decimal(0.7)
        result_checked_item = self.orderitem_set.filter().exclude(
            status__value='WaitingForPrePaid').exclude(
            status__value='canceled').exclude(
            status__value='Failed').exclude(
            status__value='unapproved')
        if result_checked_item.exists():
            total_vnd_item_checked = sum([i.total_vnd for i in result_checked_item if i.sum_arrived_quantity > 0])
        else:
            total_vnd_item_checked = 0

        total_pay = total_vnd_item_checked + self.sum_shipment_cost + self.total_extra_price + self.sum_shipment_payment_late_cost - self.order_discount



        total_need_to_prepaid = decimal.Decimal((self.total_item_cost - total_pay)*decimal.Decimal(prepaid_rate))

        if total_need_to_prepaid <= decimal.Decimal(0):
            total_need_to_prepaid = decimal.Decimal(0)
        total_need_to_pay= total_need_to_prepaid + decimal.Decimal(total_pay) - decimal.Decimal(self.sum_payment_transaction)


        return round(total_need_to_pay,0)


    def payment_left_tag(self):
        return self.currency.display(self.payment_left)

    payment_left_tag.short_description = _('Payment left')

    def user_facebook_tag(self):
        user_profile = self.customer.profile
        if user_profile.user_facebook:
            return user_profile.user_facebook
        return None

    user_facebook_tag.short_description = _('Facebook Address')

    def phone_tag(self):
        return self.customer.profile.phone_number

    phone_tag.short_description = _('Phone Number')

class OrderItem(models.Model):
    class Meta:
        verbose_name = _("OrderItem")
        verbose_name_plural = _("OrderItem")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    sku = models.CharField(verbose_name=_("sku"), blank=True, max_length=512, db_index=True)
    min_quantity = models.PositiveIntegerField(verbose_name=_("min_quantity"),null=True, blank=True, default=1)
    price_ranges = models.CharField(verbose_name=_("price_ranges"), blank=True, max_length=2048)

    order = models.ForeignKey("Order", verbose_name=_("order"),null=True,blank=True)

    customer = models.CharField(verbose_name=_("customer"), blank=True, null=True, max_length=255, db_index=True)


    product = models.ForeignKey("Product", verbose_name=_("product"), null=True, blank=True, on_delete=models.PROTECT)

    shopping_domain = models.CharField(verbose_name=_("shopping_domain"), blank=True, max_length=255, db_index=True)

    vendor = models.CharField(verbose_name=_("vendor"), blank=True, max_length=255, db_index=True)
    vendor_id = models.CharField(verbose_name=_("vendor_id"), blank=True, max_length=255, db_index=True)
    vendor_address = models.CharField(verbose_name=_("vendor_address"), blank=True, max_length=255, db_index=True)
    vendor_url = models.CharField(verbose_name=_("vendor_url"), blank=True, max_length=255, db_index=True)

    name = models.CharField(verbose_name=_("name"), blank=True, max_length=512, db_index=True)
    image_url = models.CharField(verbose_name=_("image_url"), max_length=2048, blank=True)
    item_url = models.CharField(verbose_name=_("item_url"), blank=True, max_length=2048)
    item_url_commi = models.CharField(verbose_name=_("item_url_commi"), blank=True, max_length=2048)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), blank=True, null=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])
    options_selected = models.CharField(verbose_name=_("options_selected"), max_length=512, blank=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT, null=True, blank=True)

    quantity = models.PositiveIntegerField(verbose_name=_("customer_quantity"), default=1, db_index=True)
    price = models.DecimalField(verbose_name=_("customer_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)
    shipping = models.DecimalField(verbose_name=_("customer_shipping"), default=decimal.Decimal(0),
                                   max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                   validators=[MinValueValidator(0)], db_index=True)

    order_item_url = models.CharField(verbose_name=_("order_item_url"), blank=True, max_length=2048)

    order_quantity = models.PositiveIntegerField(verbose_name=_("order_quantity"), default=0, db_index=True)
    paid_quantity = models.PositiveIntegerField(verbose_name=_("paid_quantity"), null=True, blank=True, default=0, db_index=True)
    canceled_quantity = models.PositiveIntegerField(verbose_name=_("canceled_quantity"), null=True, blank=True, default=0, db_index=True)
    order_price = models.DecimalField(verbose_name=_("order_price"), default=decimal.Decimal(0),
                                      max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                      validators=[MinValueValidator(0)], db_index=True)
    order_shipping = models.DecimalField(verbose_name=_("order_shipping"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    paid_price = models.DecimalField(verbose_name=_("paid_price"), null=True, blank=True, default=decimal.Decimal(0),
                                     max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                     validators=[MinValueValidator(0)], db_index=True)

    paid_shipping = models.DecimalField(verbose_name=_("paid_shipping"), null=True, blank=True,
                                        default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    service_by_percent = models.DecimalField(verbose_name=_("service_by_percent"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    service_by_quantity = models.DecimalField(verbose_name=_("service_by_quantity"), default=decimal.Decimal(0),
                                             max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                             validators=[MinValueValidator(0)], db_index=True)

    service_charge = models.DecimalField(verbose_name=_("service_charge"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    insurance_charge = models.DecimalField(verbose_name=_("insurance_charge"), default=decimal.Decimal(0),
                                           max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                           validators=[MinValueValidator(0)], db_index=True)

    fragile_charge = models.DecimalField(verbose_name=_("fragile_charge"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    rocket_charge = models.DecimalField(verbose_name=_("rocket_charge"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    packing_charge = models.DecimalField(verbose_name=_("packing_charge"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    rocket_ship_charge = models.DecimalField(verbose_name=_("rocket_ship_charge"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    bargain_charge = models.DecimalField(verbose_name=_("bargain_charge"), default=decimal.Decimal(0),
                                             max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                             validators=[MinValueValidator(0)], db_index=True)

    tax_cost = models.DecimalField(verbose_name=_("tax_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)
    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    fragile = models.BooleanField(verbose_name=_("fragile"), default=False)
    insurance = models.BooleanField(verbose_name=_("insurance"), default=False)
    rocket = models.BooleanField(verbose_name=_("rocket"), default=False)
    packing = models.BooleanField(verbose_name=_("packing"), default=False)
    service = models.BooleanField(verbose_name=_("service"), default=True)
    bargain = models.BooleanField(verbose_name=_("bargain"), default=False)
    rocket_ship = models.BooleanField(verbose_name=_("rocket_ship"), default=False)
    checkitem = models.BooleanField(verbose_name=_("checkitem"), default=False)
    ##status
    delivery = models.BooleanField(verbose_name=_("delivery"), default=False)
    waitchecking = models.BooleanField(verbose_name=_("waitchecking"), default=False)
    deposit = models.BooleanField(verbose_name=_("deposit"), default=False)
    ##
    interal_note = models.TextField(verbose_name=_("interal_note"), blank=True)

    customer_note = models.TextField(verbose_name=_("customer_note"), blank=True)

    note = models.TextField(verbose_name=_("note"), blank=True)

    order_employee = models.ForeignKey(User, verbose_name=_("order_employee"), limit_choices_to={'is_staff': True},
                                       null=True, blank=True, on_delete=models.SET_NULL)

    check_employee = models.ForeignKey(User, verbose_name=_("check_employee"), related_name='check_employee_set', limit_choices_to={'is_staff': True},
                                       null=True, blank=True, on_delete=models.SET_NULL)

    ordered_date = models.DateTimeField(verbose_name=_("Item Ordered Date"), null=True, blank=True)

    checked_date = models.DateTimeField(verbose_name=_("Item Checked Date"), null=True, blank=True)

    completed_date = models.DateTimeField(verbose_name=_("Item Completed Date"), null=True, blank=True)


    http_referer = models.CharField(verbose_name=_("http_referer"), max_length=2048, blank=True)
    ## tracking
    tracking_number = models.CharField(verbose_name=_("tracking_number"), max_length=255, null=True, blank=True)

    shipmentpackage = models.ManyToManyField('ShipmentPackage', verbose_name=_("shipmentpackage"),
                                             related_name='shipmentpackage_set', through='OrderPackageItem')
    ##
    # order number
    order_number = models.CharField(verbose_name=_("order_number"), max_length=255, null=True, blank=True)

    orderpackage = models.ManyToManyField('OrderPackage', verbose_name=_("orderpackage"),
                                          related_name='orderpackage_set', through='OrderPackageItem')
    flag = models.BooleanField(verbose_name=_("flag"), default=False)


    def __str__(self):
        try:
            return str("<%s> (%s) %s" % (self.pk, str(self.status), self.name))
        except Exception as ex:
            print(ex)
            return str("<%s> %s" % (self.pk, self.name))

    def calculate_arrived_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.arriveditem_set.filter().aggregate(
            _sum_arrived_quantity=Sum(F('arrived_quantity')),
            _sum_arrived_shipping_cost=Sum(F('shipping_cost')),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)
    @property
    def sum_arrived_quantity(self):
        if not hasattr(self, '_sum_arrived_quantity'):
            self.calculate_arrived_item()
        if self._sum_arrived_quantity:
            return self._sum_arrived_quantity
        else:
            return 0

    @property
    def sum_arrived_shipping_cost(self):
        if not hasattr(self, '_sum_arrived_shipping_cost'):
            self.calculate_arrived_item()
        if self._sum_arrived_shipping_cost:
            return self._sum_arrived_shipping_cost
        else:
            return 0

    @property
    def sum_arrived_shipping_cost_vnd(self):
        if self.sum_arrived_shipping_cost:
            return self.sum_arrived_shipping_cost * self.exchange_rate
        else:
            return 0

    def calculate_tracking_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.shipmentpackage.all().distinct().aggregate(
            _count_shipmentpackage=Count(F('id'), distinct=True),
            _sum_delivery_cost=Sum(F('delivery_cost'), distinct=True, output_field=models.DecimalField()),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)

    def calculate_order_number_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.orderpackage.all().distinct().aggregate(
            _count_orderpackage=Count(F('id'), distinct=True),
        )

        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def ordered_by_username(self):
        return self.order_employee.username
    @property
    def checked_by_username(self):
        return self.check_employee.username

    @property
    def item_status(self):
        return self.status.label

    @property
    def vendor_tag(self):
        return re.sub(r'</fo.+?>', '', re.sub(r'<fo.+?>', '', self.vendor))
    @property
    def name_tag(self):
        return re.sub(r'</fo.+?>', '', re.sub(r'<fo.+?>', '', self.name))

    @property
    def item_total(self):
        return self.price * self.quantity

    @property
    def image_url_big(self):
        if self.image_url:
            return self.image_url.replace('_150x150.jpg', '').replace(
        '_150x150q90.jpg', '').replace('.150x150', '')
        else:
            return self.created
    @property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created


    @property
    def ordered_tag(self):
        if self.ordered_date:
            return self.ordered_date.strftime("%d-%m-%Y %H:%M")
        else:
            return self.ordered_date
    @property
    def checked_tag(self):
        if self.checked_date:
            return self.checked_date.strftime("%d-%m-%Y %H:%M")
        else:
            return self.checked_date
    @property
    def count_shipmentpackage(self):
        if not hasattr(self, '_count_shipmentpackage'):
            self.calculate_tracking_item()
        if self._count_shipmentpackage:
            return self._count_shipmentpackage
        else:
            return 0
    @property
    def sum_delivery_cost(self):
        if not hasattr(self, '_sum_delivery_cost'):
            self.calculate_tracking_item()
        return self._sum_delivery_cost


    @property
    def count_orderpackage(self):
        if not hasattr(self, '_count_orderpackage'):
            self.calculate_order_number_item()
        return self._count_orderpackage

    @property
    def count_tracking(self):
        if not hasattr(self, '_count_quantity'):
            self.calculate_tracking_item()
        try:
            return int(self._count_quantity)
        except Exception as e:
            # print(e)
            return 0

    @property
    def option_selected_tag(self):
        try:
            option_selected = json.loads(self.options_selected)
        except ValueError:
            string = re.sub(r"u'", "'", re.sub(r'\s*,\s*u?', '\n', self.options_selected)).lstrip('{').rstrip('}')
        else:
            string=''
            for key, value in list(option_selected.items()):
                if key.find('1688_0') != -1:
                    string = string + 'Màu sắc:' + value + '\n'
                elif key.find('1688_1') != -1:
                    string = string + 'Kích thước:' + value + '\n'
                elif key.find('_0') != -1:
                    string = string + 'Kích thước:' + value + '\n'
                elif key.find('_1') != -1:
                    string = string + 'Màu sắc:' + value + '\n'
                else:
                    string = string + key+':'+value + '\n'
        return re.sub(r'</fo.+?>', '',re.sub(r'<fo.+?>', '',string))

    @property
    def shipmentpackage_tag(self):
        text = {}
        for line_shipment in self.shipmentpackage.all():
            text[str(line_shipment.id)] = str(line_shipment.tracking_number)
        return '\n'.join([key + ':' + value for key, value in list(text.items())])

    def name_image_tag(self):
        text = "%s <br>" % self.name
        if len(text) > 100:
            text = text[:100] + '...'
        text = text + '<b><p style="color:Tomato;">%s</p></b>' % self.option_selected_tag
        return format_html(
            text + '<br><a href="{}" target="blank" data-toggle="tooltip" title="{}"><img src="{}" '
                   'style="width:100px;height:100px;" class="toggle-enlarge"/> </a>',
            self.order_item_url if self.order_item_url else self.item_url,
            self.option_selected_tag, self.image_url, self.image_url)

    name_image_tag.allow_tags = True
    name_image_tag.short_description = _("Image")

    def image_tag(self):
        return format_html(
            '<a href="{}" target="blank" data-toggle="tooltip" title="{}"><img src="{}" '
            'style="width:64px;height:64px;" class="toggle-enlarge"/> </a>',
            self.order_item_url if self.order_item_url else self.item_url,
            self.option_selected_tag, self.image_url, self.image_url)

    image_tag.allow_tags = True
    image_tag.short_description = _("Image")

    def image_inline_tag(self):
        return format_html(
            '<a href="{}" target="blank" data-toggle="tooltip" title="{}"><img src="{}" '
            'style="width:500px;height:500px;" class="toggle-enlarge"/> </a>',
            self.order_item_url if self.order_item_url else self.item_url,
            self.option_selected_tag, self.image_url, self.image_url)

    image_inline_tag.allow_tags = True
    image_inline_tag.short_description = _("Image")

    def item_url_tag(self):
        return format_html('<a href="{}" target="blank">{}</a>',
                           self.order_item_url if self.order_item_url else self.item_url, self.name)

    item_url_tag.allow_tags = True
    item_url_tag.short_description = _("Item url")

    def price_tag(self):
        return self.currency.display(self.price)

    price_tag.allow_tags = True
    price_tag.short_description = _("Price")

    def order_price_tag(self):
        return self.currency.display(self.order_price)

    order_price_tag.allow_tags = True
    order_price_tag.short_description = _("Order Price")

    @property
    def total_vendor_quantity(self):
        if len(self.vendor) > 1:
            if self.order:
                calculator_orderitem = self.order.orderitem_set.exclude(
                status__value='WaitingForPrePaid').exclude(
                status__value='canceled').exclude(
                status__value='Failed').exclude(
                status__value='unapproved').filter(vendor=self.vendor).aggregate(total_quantity=Sum(F('quantity')))
                return calculator_orderitem['total_quantity']
            else:
                calculator_orderitem= OrderItem.objects.filter(customer=self.customer, order__isnull=True).exclude(
                status__value='WaitingForPrePaid').exclude(
                status__value='canceled').exclude(
                status__value='Failed').exclude(
                status__value='unapproved').filter(vendor=self.vendor).aggregate(total_quantity=Sum(F('quantity')))
                return calculator_orderitem['total_quantity']
        else:
            return self.quantity
    @property
    def value(self):
        return self.price * self.quantity

    @property
    def order_value(self):
        return self.order_price * self.order_quantity

    @property
    def paid_value(self):

        return self.paid_price * self.paid_quantity

    def value_tag(self):
        return self.currency.display(self.value)
    value_tag.short_description = _("Value")

    @property
    def total_service_cost(self):
        return decimal.Decimal(self.service_charge) + decimal.Decimal(self.insurance_charge) + decimal.Decimal(self.packing_charge) + decimal.Decimal(self.rocket_charge)  + decimal.Decimal(self.bargain_charge)

    @property
    def total_service_cost_vnd(self):
        return self.total_service_cost * self.exchange_rate

    @property
    def total(self):
        return self.value + self.shipping + decimal.Decimal(self.tax_cost) + self.total_service_cost

    @property
    def total_vnd(self):
        return self.total * self.exchange_rate

    @property
    def price_vnd(self):
        return self.price * self.exchange_rate

    @property
    def shipping_vnd(self):
        return self.shipping * self.exchange_rate

    @property
    def service_charge_vnd(self):
        return self.service_charge * self.exchange_rate

    @property
    def bargain_charge_vnd(self):
        return self.bargain_charge * self.exchange_rate

    @property
    def insurance_charge_vnd(self):
        return self.insurance_charge * self.exchange_rate
    @property
    def rocket_charge_vnd(self):
        return self.rocket_charge * self.exchange_rate
    @property
    def packing_charge_vnd(self):
        return self.packing_charge * self.exchange_rate
    @property
    def order_total_vnd(self):

        return self.order_total * self.exchange_rate

    @property
    def order_price_vnd(self):
        return self.order_price * self.exchange_rate

    @property
    def order_shipping_vnd(self):
        return self.order_shipping * self.exchange_rate

    @property
    def paid_total_vnd(self):
        return self.paid_total * self.exchange_rate

    @property
    def paid_price_vnd(self):
        return self.paid_price * self.exchange_rate

    @property
    def paid_shipping_vnd(self):
        return self.paid_shipping * self.exchange_rate

    @property
    def order_total(self):
        if self.order_value > 0:
            return self.order_value + self.order_shipping
        else:
            return 0

    @property
    def paid_total(self):

        return self.paid_value + self.paid_shipping

    def total_tag(self):
        return self.currency.display(self.total)

    total_tag.short_description = _("Total")

    def total_order_currency_tag(self):
        value = decimal.Decimal(self.total)
        return self.order.currency.display(
            self.order.currency.invert(value * decimal.Decimal(self.exchange_rate), self.order.exchange_rate))

    total_order_currency_tag.short_description = _("Total")

    # def save(self, *args, **kwargs):
    #     try:
    #         order = self.order
    #         order_item_set = order.orderitem_set.all()
    #         print(order.status)
    #         if len(order_item_set.values('status').distinct()) < 2 \
    #                 and order_item_set.first().status.value == "ShipToVN":
    #             order.status = order_item_set.first().status
    #             print(order.status)
    #             order.save()
    #     except Exception as e:
    #         print(e)
    #     super(OrderItem, self).save()

class OrderedItem(models.Model):
    class Meta:
        verbose_name = _("OrderedItem")
        verbose_name_plural = _("OrderedItem")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    order_item = models.ForeignKey('OrderItem', verbose_name=_("order_item"),
                               on_delete=models.PROTECT)

    order_package = models.ForeignKey('OrderPackage', verbose_name=_("order_package"),
                               on_delete=models.PROTECT)

    ordered_quantity = models.PositiveIntegerField(verbose_name=_("ordered_quantity"), null=True, blank=True,
                                                   default=0, db_index=True)

    shipping_cost = models.DecimalField(verbose_name=_("shipping_cost"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)


    def __str__(self):
        return "%s x %s" % (self.ordered_quantity, str(self.order_item)[:100])

class TotalOrderBilling(models.Model):
    class Meta:
        verbose_name = _("TotalOrderBilling")
        verbose_name_plural = _("TotalOrderBilling")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)


    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return str(self.status.value)

class ThanhToanHo(models.Model):
    class Meta:
        verbose_name = _("ThanhToanHo")
        verbose_name_plural = _("ThanhToanHo")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="thanhtoanho_customer_set",
                                 on_delete=models.PROTECT, null=True)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)


    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT, null=True, blank=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT, null=True, blank=True)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    exchange_rate_org = models.DecimalField(verbose_name=_("exchange_rate_org"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])


    alipay = models.ForeignKey(AlipayAccounts, verbose_name=_("alipay"), related_name="thanhtoanho_alipay_set", null=True, blank=True, on_delete=models.SET_NULL)

    main_currency = models.CharField(verbose_name=_("main_currency"), max_length=255, default='CNY')


    extra_price = models.DecimalField(verbose_name=_("extra_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    service_charge = models.DecimalField(verbose_name=_("service_charge"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    paid_date = models.DateTimeField(verbose_name=_("paid Date"), null=True, blank=True)

    pending_date = models.DateTimeField(verbose_name=_("pending Date"), null=True, blank=True)

    paid_by = models.ForeignKey(User, verbose_name=_("paid_by"), related_name="thanhtoanho_paid_by_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,

                                    blank=True)
    pending_by = models.ForeignKey(User, verbose_name=_("pending_by"), related_name="thanhtoanho_pending_by_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)


    @cached_property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created


    @property
    def total_price(self):
        return self.price + self.service_charge + self.extra_price

    def __str__(self):
        return str(self.pk)

class OrderBilling(models.Model):
    class Meta:
        verbose_name = _("OrderBilling")
        verbose_name_plural = _("OrderBilling")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    order = models.ForeignKey("Order", verbose_name=_("order"))

    total_billing = models.ForeignKey("TotalOrderBilling", verbose_name=_("total_billing"), null=True)

    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)
    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT, null=True, blank=True)

    item_price = models.DecimalField(verbose_name=_("item_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    extra_price = models.DecimalField(verbose_name=_("extra_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    total_weight = models.DecimalField(verbose_name=_("total_weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    shipment_price = models.DecimalField(verbose_name=_("extra_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    quantity_shipment = models.PositiveIntegerField(verbose_name=_("quantity_shipment"), default=0, db_index=True)

    item_quantity = models.PositiveIntegerField(verbose_name=_("item_quantity"), default=0, db_index=True)

    arrived_quantity = models.PositiveIntegerField(verbose_name=_("arrived_quantity"), default=0, db_index=True)

    need_to_pay = models.DecimalField(verbose_name=_("need_to_pay"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    total_paid = models.DecimalField(verbose_name=_("total_paid"), default=decimal.Decimal(0),
                                      max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                      validators=[MinValueValidator(0)], db_index=True)

    def __str__(self):
        return str(self.order.id)

class Extracharge(models.Model):
    class Meta:
        verbose_name = _("Extracharge")
        verbose_name_plural = _("Extracharge")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    order = models.ForeignKey("Order", verbose_name=_("order"))

    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    def __str__(self):
        return str(self.price)

class RefundType(models.Model):
    class Meta:
        verbose_name = _("RefundType")
        verbose_name_plural = _("RefundType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class RefundBankType(models.Model):
    class Meta:
        verbose_name = _("RefundBankType")
        verbose_name_plural = _("RefundBankType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class Refundcharge(models.Model):
    class Meta:
        verbose_name = _("Refundcharge")
        verbose_name_plural = _("Refundcharge")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    refund_type = models.ForeignKey("RefundType", verbose_name=_("refund_type"), on_delete=models.PROTECT, null=True)

    refund_bank_type = models.ForeignKey("RefundBankType", verbose_name=_("refund_bank_type"), on_delete=models.PROTECT, null=True)

    orderpackage = models.ForeignKey("OrderPackage", verbose_name=_("orderpackage"), on_delete=models.PROTECT, blank=True, null=True)

    thanhtoanho = models.ForeignKey("ThanhToanHo", verbose_name=_("thanhtoanho"), on_delete=models.PROTECT, blank=True, null=True)

    reference = models.TextField(verbose_name=_("reference"),
                                 blank=True)  # store detail automatically get from bank system
    status = models.ForeignKey("Status", verbose_name=_("status"), on_delete=models.PROTECT, null=True, blank=True)

    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])
    flag = models.BooleanField(verbose_name=_("flag"), default=False)

    approved_by = models.ForeignKey(User, verbose_name=_("approved_by"), related_name='refundcharge_to_approved_by', limit_choices_to={'is_staff': True}, null=True,
                                blank=True, on_delete=models.PROTECT)

    approved = models.DateTimeField(verbose_name=_("approved"), null=True, blank=True)

    def __str__(self):
        return str(self.price)


