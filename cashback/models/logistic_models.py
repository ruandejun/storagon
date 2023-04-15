#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  logistic_models.py
#
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#


import decimal
from audit_log.models.fields import CreatingUserField, LastUserField
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..constants.DefaultSettings import *
from django.utils.html import format_html
from django.db.models import Sum, F, Count, Q
from django.db.models.fields import DecimalField, FloatField, IntegerField
import math
from .order_models import *
from shop_module.models.product_models import ImagesDocument, Document
import random
# Logistic Shipment


class BaseModel(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")


class WebsiteService(models.Model):
    class Meta:
        verbose_name = _("WebsiteService")
        verbose_name_plural = _("WebsiteService")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    name = models.CharField(verbose_name=_("name"), max_length=512)
    url = models.CharField(verbose_name=_("url"), max_length=512)
    token = models.CharField(verbose_name=_("token"), max_length=512)


    def __str__(self):
        return str(self.name)

class ShipmentService(models.Model):
    class Meta:
        verbose_name = _("ShipmentService")
        verbose_name_plural = _("ShipmentService")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    name = models.CharField(verbose_name=_("name"), max_length=512)
    label = models.CharField(verbose_name=_("label"), max_length=512)
    contact = models.TextField(verbose_name=_("contact"), blank=True)
    metadata = models.TextField(verbose_name=_("metadata"), blank=True)
    is_local = models.BooleanField(verbose_name=_("is_local"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class ShipmentLocation(models.Model):
    class Meta:
        verbose_name = _("ShipmentLocation")
        verbose_name_plural = _("ShipmentLocation")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    name = models.CharField(verbose_name=_("name"), max_length=512)
    note = models.TextField(verbose_name=_("note"), blank=True,max_length=255)
    address = models.CharField(verbose_name=_("address"), blank=True, max_length=512)
    country = models.CharField(verbose_name=_("country"), blank=True, max_length=512)
    state = models.CharField(verbose_name=_("state"), blank=True, max_length=512)
    city = models.CharField(verbose_name=_("city"), blank=True, max_length=512)
    zipcode = models.CharField(verbose_name=_("zipcode"), blank=True, max_length=512)
    phone = models.CharField(verbose_name=_("phone"), blank=True, max_length=512)
    district = models.CharField(verbose_name=_("district"), blank=True, max_length=512)
    flag = models.BooleanField(verbose_name=_("flag"), default=False)

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __str__(self):
        return str(self.name)

class ArrivedItem(models.Model):
    class Meta:
        verbose_name = _("ArrivedItem")
        verbose_name_plural = _("ArrivedItem")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True}, editable=True,
                                   blank=True, related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
                                related_name="modified_%(app_label)s_%(class)s_set")

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    order_item = models.ForeignKey('OrderItem', verbose_name=_("order_item"))

    shipment_package = models.ForeignKey('ShipmentPackage', verbose_name=_("shipment_package"))

    arrived_quantity = models.PositiveIntegerField(verbose_name=_("arrived_quantity"), null=True, blank=True,
                                                   default=0, db_index=True)

    shipping_cost = models.DecimalField(verbose_name=_("shipping_cost"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)


    def __str__(self):
        return "%s x %s" % (self.arrived_quantity, str(self.order_item)[:100])

class ShipmentItem(models.Model):
    class Meta:
        verbose_name = _("ShipmentItem")
        verbose_name_plural = _("ShipmentItem")

    shipment_package = models.ForeignKey('ShipmentPackage', verbose_name=_("shipment_package"))
    order_item = models.ForeignKey('OrderItem', verbose_name=_("order_item"))

    quantity = models.PositiveIntegerField(verbose_name=_("quantity"), default=0, db_index=True, null=True, blank=True)

    arrived_quantity = models.PositiveIntegerField(verbose_name=_("arrived_quantity"), null=True, blank=True,
                                                   default=0, db_index=True)



    def __str__(self):
        return "%s x %s" % (self.quantity, str(self.order_item)[:100])

class PackingType(models.Model):
    class Meta:
        verbose_name = _("PackingType")
        verbose_name_plural = _("PackingType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class PackingLabel(models.Model):
    class Meta:
        verbose_name = _("PackingLabel")
        verbose_name_plural = _("PackingLabel")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    name = models.CharField(verbose_name=_("name"), max_length=255)
    address = models.CharField(verbose_name=_("address"), max_length=2048)
    phone = models.CharField(verbose_name=_("phone"), max_length=255)
    logo_url = models.CharField(verbose_name=_("logo_url"), max_length=2048, blank=True)
    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_packinglabel_set", on_delete=models.PROTECT)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.name)


class ShippingAddress(models.Model):
    class Meta:
        verbose_name = _("ShippingAddress")
        verbose_name_plural = _("ShippingAddress")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_shipping_address_set", on_delete=models.PROTECT)

    full_name = models.CharField(verbose_name=_("full_name"), max_length=255)
    address = models.CharField(verbose_name=_("address"), max_length=255)
    city = models.CharField(verbose_name=_("city"), max_length=255)
    country = models.CharField(verbose_name=_("country"), max_length=255)
    zipcode = models.CharField(verbose_name=_("zipcode"), max_length=255)
    phone = models.CharField(verbose_name=_("phone"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.full_name)


class ShippingType(models.Model):
    class Meta:
        verbose_name = _("ShippingType")
        verbose_name_plural = _("ShippingType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class ShippingMethod(models.Model):
    class Meta:
        verbose_name = _("ShippingMethod")
        verbose_name_plural = _("ShippingMethod")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)

    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class Importshipment(models.Model):
    class Meta:
        verbose_name = _("Exportshipment")
        verbose_name_plural = _("Exportshipment")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")


    exported = models.DateTimeField(verbose_name=_("exported"), blank=True, null=True)

    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)

    arrived_by = models.ForeignKey(User, verbose_name=_("arrived_by"), null=True, blank=True)
    exported_by = models.ForeignKey(User, verbose_name=_("exported_by"),related_name="exported_by_packing_set", null=True, blank=True)
    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)
    delivered_by = models.ForeignKey(User, verbose_name=_("delivered_by"),related_name="delivered_packing_by_set", null=True, blank=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT)

    website_service = models.ForeignKey("WebsiteService", verbose_name=_("website_service"), related_name='website_service_importshipment', null=True,
                                          blank=True,
                                          on_delete=models.PROTECT)

    website_id = models.CharField(max_length=255, verbose_name=_('website_id'), null=True, blank=True)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_imported_shipmentpackages_set",
                                 on_delete=models.PROTECT)


    note = models.TextField(verbose_name=_("note"), blank=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    weight_cost = models.DecimalField(verbose_name=_("weight_cost"), default=decimal.Decimal(0), max_digits=9,
                                      decimal_places=2)

    price = models.DecimalField(verbose_name=_("exportshipment_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    extra_charge = models.DecimalField(verbose_name=_("extra_charge"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    def calculate_imported_shipment_service(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.imported_shipment_service.all().aggregate(
            _count_shipment_package_import=Count(F('id')),
            _sum_weight_real_shipment_package_import=Sum(F('weight_real')),
            _sum_weight_shipment_package_import=Sum(F('weight')),
            _sum_shipping_cost_shipment_package_import=Sum(F('shipping_cost')),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created
    @property
    def arrived_tag(self):
        if self.arrived:
            return self.arrived.strftime("%d-%m-%Y %H:%M")
        else:
            return self.arrived
    @property
    def delivered_tag(self):
        if self.delivered:
            return self.delivered.strftime("%d-%m-%Y %H:%M")
        else:
            return self.delivered

    @property
    def count_shipment_package_import(self):
        if not hasattr(self, '_count_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._count_shipment_package_import:
            return self._count_shipment_package_import
        else:
            return 0

    @property
    def sum_weight_shipment_package_import(self):
        if not hasattr(self, '_sum_weight_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._sum_weight_shipment_package_import:
            return self._sum_weight_shipment_package_import
        else:
            return 0
    @property
    def sum_weight_real_shipment_package_import(self):
        if not hasattr(self, '_sum_weight_real_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._sum_weight_real_shipment_package_import:
            return self._sum_weight_real_shipment_package_import
        else:
            return 0
    @property
    def sum_shipping_cost_shipment_package_import(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._sum_shipping_cost_shipment_package_import:
            return self._sum_shipping_cost_shipment_package_import
        else:
            return 0

class Importedforeignshipment(models.Model):
    class Meta:
        verbose_name = _("Exportshipment")
        verbose_name_plural = _("Exportshipment")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")


    exported = models.DateTimeField(verbose_name=_("exported"), blank=True, null=True)
    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)

    arrived_by = models.ForeignKey(User, verbose_name=_("arrived_by"), null=True, blank=True)
    exported_by = models.ForeignKey(User, verbose_name=_("exported_by"),related_name="exported_by_imported_foreignshipment_set", null=True, blank=True)
    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)
    delivered_by = models.ForeignKey(User, verbose_name=_("delivered_by"),related_name="delivered_by_imported_foreignshipment_set", null=True, blank=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_imported_foreignshipment_set",
                                 on_delete=models.PROTECT,null=True,blank=True)

    note = models.TextField(verbose_name=_("note"), blank=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    price = models.DecimalField(verbose_name=_("exportshipment_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    extra_charge = models.DecimalField(verbose_name=_("extra_charge"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    def calculate_imported_foreign_shipment_service(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.imported_foreign_shipment_service.all().aggregate(
            _count_shipment_package_import=Count(F('id')),
            _sum_weight_shipment_package_import=Sum(F('weight')),
            _sum_shipping_cost_shipment_package_import=Sum(F('shipping_cost')),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def count_shipment_package_import(self):
        if not hasattr(self, '_count_shipment_package_import'):
            self.calculate_imported_foreign_shipment_service()
        if self._count_shipment_package_import:
            return self._count_shipment_package_import
        else:
            return 0

    @property
    def sum_weight_shipment_package_import(self):
        if not hasattr(self, '_sum_weight_shipment_package_import'):
            self.calculate_imported_foreign_shipment_service()
        if self._sum_weight_shipment_package_import:
            return self._sum_weight_shipment_package_import
        else:
            return 0

    @property
    def sum_shipping_cost_shipment_package_import(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package_import'):
            self.calculate_imported_foreign_shipment_service()
        if self._sum_shipping_cost_shipment_package_import:
            return self._sum_shipping_cost_shipment_package_import
        else:
            return 0

class Exportedshipment(models.Model):
    class Meta:
        verbose_name = _("Exportshipment")
        verbose_name_plural = _("Exportshipment")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")


    exported = models.DateTimeField(verbose_name=_("exported"), blank=True, null=True)

    list_order = models.ManyToManyField(Order,verbose_name=_("list_order"),related_name="exported_shipment_list_order", blank=True)

    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)

    shipping_type = models.ForeignKey(ShippingType, verbose_name=_("shipping_type"),related_name="shipping_type_exported_packing", null=True, blank=True)
    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_("shipping_method"),related_name="shipping_method_exported_packing", null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, verbose_name=_("shipping_address"),related_name="shipping_address_exported_packing", null=True, blank=True)

    exported_by = models.ForeignKey(User, verbose_name=_("exported_by"),related_name="exportedshipment_exported_by", null=True, blank=True)

    delivered_by = models.ForeignKey(User, verbose_name=_("delivered_by"),related_name="exportedshipment_delivered_by", null=True, blank=True)

    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)

    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True},
                               on_delete=models.PROTECT)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_exported_shipmentpackages_set",
                                 on_delete=models.PROTECT)

    shipping_number = models.CharField(verbose_name=_("shipping_number"), blank=True, max_length=512, db_index=True, null=True)

    note = models.TextField(verbose_name=_("note"), blank=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    price = models.DecimalField(verbose_name=_("exportshipment_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    paid_price = models.DecimalField(verbose_name=_("exportshipment_paid_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    item_price = models.DecimalField(verbose_name=_("exportshipment_item_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)


    extra_charge = models.DecimalField(verbose_name=_("extra_charge"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    amount_need_to_pay = models.DecimalField(verbose_name=_("amount_need_to_pay"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    def calculate_payments(self):
        result = self.customerpayment_set.all()
        total_amount_transaction = 0
        for r in result:
            if r.transaction.status.value != 'unapproved':
                amount_t = r.transaction.amount * r.transaction.exchange_rate
                total_amount_transaction += amount_t
        setattr(self, '_sum_payment_transaction', total_amount_transaction)
        setattr(self, '_count_payment', result.count())


    @property
    def need_to_pay(self):
        if self.price:
            return self.price + self.extra_charge+self.sum_shipping_cost_shipment_package_exported_vnd - self.sum_payment_transaction
        else:
            return None

    @property
    def sum_payment_transaction(self):
        if not hasattr(self, '_sum_payment_transaction'):
            self.calculate_payments()
        if self._sum_payment_transaction:
            return self._sum_payment_transaction
        else:
            return 0

    def calculate_exported_shipment_service(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.exported_shipment_service.all().aggregate(
            _count_shipment_package_exported=Count(F('id')),
            _sum_weight_shipment_package_exported=Sum(F('weight')),
            _sum_weight_real_shipment_package_exported=Sum(F('weight_real')),
            _sum_shipping_cost_shipment_package_exported=Sum(F('shipping_cost')),
            _sum_shipping_cost_shipment_package_exported_vnd=Sum(F('shipping_cost')*F('exchange_rate')),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def count_shipment_package_exported(self):
        if not hasattr(self, '_count_shipment_package_exported'):
            self.calculate_exported_shipment_service()
        if self._count_shipment_package_exported:
            return self._count_shipment_package_exported
        else:
            return 0

    @property
    def sum_weight_shipment_package_exported(self):
        if not hasattr(self, '_sum_weight_shipment_package_import'):
            self.calculate_exported_shipment_service()
        if self._sum_weight_shipment_package_exported:
            return self._sum_weight_shipment_package_exported
        else:
            return 0

    @property
    def sum_shipping_cost_shipment_package_exported(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package_exported'):
            self.calculate_exported_shipment_service()
        if self._sum_shipping_cost_shipment_package_exported:
            return self._sum_shipping_cost_shipment_package_exported
        else:
            return 0

    @property
    def sum_shipping_cost_shipment_package_exported_vnd(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package_exported_vnd'):
            self.calculate_exported_shipment_service()
        if self._sum_shipping_cost_shipment_package_exported_vnd:
            return self._sum_shipping_cost_shipment_package_exported_vnd
        else:
            return 0


    @property
    def sum_weight_real_shipment_package_exported(self):
        if not hasattr(self, '_sum_weight_real_shipment_package_exported'):
            self.calculate_exported_shipment_service()
        if self._sum_weight_real_shipment_package_exported:
            return self._sum_weight_real_shipment_package_exported
        else:
            return 0


class Exportshipment(models.Model):
    class Meta:
        verbose_name = _("Exportshipment")
        verbose_name_plural = _("Exportshipment")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    packing_type = models.ForeignKey("PackingType", verbose_name=_("PackingType"), on_delete=models.PROTECT, null=True)


    exported = models.DateTimeField(verbose_name=_("exported"), blank=True, null=True)
    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)
    exported_by = models.ForeignKey(User, verbose_name=_("exported_by"), null=True, blank=True)
    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_orderstatus': True}, on_delete=models.PROTECT, null=True)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="customer_exportshipment_set",
                                 on_delete=models.PROTECT)

    note = models.TextField(verbose_name=_("note"), blank=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    price = models.DecimalField(verbose_name=_("exportshipment_price"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    extra_charge = models.DecimalField(verbose_name=_("extra_charge"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)

    def calculate_imported_shipment_service(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.export_shipment_service.all().aggregate(
            _count_shipment_package_import=Count(F('id')),
            _sum_weight_shipment_package_import=Sum(F('weight')),
            _sum_shipping_cost_shipment_package_import=Sum(F('shipping_cost')),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def count_shipment_package_import(self):
        if not hasattr(self, '_count_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._count_shipment_package_import:
            return self._count_shipment_package_import
        else:
            return 0

    @property
    def sum_weight_shipment_package_import(self):
        if not hasattr(self, '_sum_weight_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._sum_weight_shipment_package_import:
            return self._sum_weight_shipment_package_import
        else:
            return 0

    @property
    def sum_shipping_cost_shipment_package_import(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package_import'):
            self.calculate_imported_shipment_service()
        if self._sum_shipping_cost_shipment_package_import:
            return self._sum_shipping_cost_shipment_package_import
        else:
            return 0

    ####
    def calculate_Shipment_package(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.export_shipment_service.all().aggregate(
            _count_shipment_package=Count(F('id')),
            _sum_weight_shipment_package=Sum(F('weight')),
            _sum_shipping_cost_shipment_package=Sum(F('shipping_cost')),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def count_shipment_package(self):
        if not hasattr(self, '_count_shipment_package'):
            self.calculate_Shipment_package()
        if self._count_shipment_package:
            return self._count_shipment_package
        else:
            return 0
    @property
    def sum_weight_shipment_package(self):
        if not hasattr(self, '_sum_weight_shipment_package'):
            self.calculate_Shipment_package()
        if self._sum_weight_shipment_package:
            return self._sum_weight_shipment_package
        else:
            return 0
    @property
    def sum_shipping_cost_shipment_package(self):
        if not hasattr(self, '_sum_shipping_cost_shipment_package'):
            self.calculate_Shipment_package()
        if self._sum_shipping_cost_shipment_package:
            return self._sum_shipping_cost_shipment_package
        else:
            return 0



class ShipmentPackage(models.Model):
    class Meta:
        verbose_name = _("ShipmentPackage")
        verbose_name_plural = _("ShipmentPackage")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    departed = models.DateTimeField(verbose_name=_("departed"), blank=True, null=True)

    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)

    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)

    imported = models.DateTimeField(verbose_name=_("imported"), blank=True, null=True)

    exported = models.DateTimeField(verbose_name=_("exported"), blank=True, null=True)

    arrived_by = models.ForeignKey(User, verbose_name=_("arrived_by"), related_name="arrived_by_set",
                                     on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                     blank=True)

    delivered_by = models.ForeignKey(User, verbose_name=_("delivered_by"), related_name="delivered_by_set", on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    exported_by = models.ForeignKey(User, verbose_name=_("exported_by"), related_name="exported_by_set",
                                     on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                     blank=True)

    imported_by = models.ForeignKey(User, verbose_name=_("imported_by"), related_name="imported_by_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)

    order = models.ForeignKey("Order", verbose_name=_("order"), null=True,blank=True)


    delivery_cost = models.DecimalField(verbose_name=_("orderpackage_delivery_cost"), default=decimal.Decimal(0),
                                max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                validators=[MinValueValidator(0)], db_index=True)

    shipping_cost = models.DecimalField(verbose_name=_("shipping_cost"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    payment_late_cost = models.DecimalField(verbose_name=_("payment_late_cost"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)

    weight_cost = models.DecimalField(verbose_name=_("weight_cost"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    weight_cost_org = models.DecimalField(verbose_name=_("weight_cost_org"), default=decimal.Decimal(0), max_digits=9,
                                      decimal_places=2)

    quantity = models.PositiveIntegerField(verbose_name=_("quantity"), default=0, db_index=True,null=True,blank=True)

    arrived_quantity = models.PositiveIntegerField(verbose_name=_("arrived_quantity"), null=True, blank=True,
                                                   default=None, db_index=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_shipmentstatus': True},
                               on_delete=models.PROTECT, null=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    weight_real = models.DecimalField(verbose_name=_("weight_real"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    length = models.DecimalField(verbose_name=_("length"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    height = models.DecimalField(verbose_name=_("height"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    width = models.DecimalField(verbose_name=_("width"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)

    tracking_number = models.CharField(verbose_name=_("tracking_number"), blank=True, max_length=512, db_index=True, null=True)


    shipment_service = models.ForeignKey("ShipmentService", verbose_name=_("shipment_service"), null=True, blank=True,on_delete=models.PROTECT)

    shipment_method = models.CharField(verbose_name=_("shipment_method"), blank=True, max_length=512, db_index=True)

    export_shipment = models.ForeignKey("Exportshipment", verbose_name=_("export_shipment"), related_name='export_shipment_service', null=True, blank=True,
                                        on_delete=models.PROTECT)

    exported_shipment = models.ForeignKey("Exportedshipment", verbose_name=_("exported_shipment"), related_name='exported_shipment_service', null=True, blank=True,
                                        on_delete=models.PROTECT)

    imported_shipment = models.ForeignKey("Importshipment", verbose_name=_("imported_shipment"), related_name='imported_shipment_service', null=True,
                                          blank=True,
                                          on_delete=models.PROTECT)

    packing_label = models.ForeignKey("PackingLabel", verbose_name=_("packing_label"), related_name='packing_label_set', null=True,
                                          blank=True,
                                          on_delete=models.PROTECT)

    website_id = models.CharField(max_length=255, verbose_name=_('website_id'), null=True, blank=True)

    website_service = models.ForeignKey("WebsiteService", verbose_name=_("website_service"), related_name='website_service_set', null=True,
                                          blank=True,
                                          on_delete=models.PROTECT)



    imported_foreign_shipment = models.ForeignKey("Importedforeignshipment", verbose_name=_("imported_foreign_shipment"), related_name='imported_foreign_shipment_service', null=True,
                                          blank=True,
                                          on_delete=models.PROTECT)

    location = models.ForeignKey("ShipmentLocation", verbose_name=_("location"), related_name='departed_packages',
                                 blank=True, null=True, on_delete=models.PROTECT)
    destination = models.ForeignKey("ShipmentLocation", verbose_name=_("destination"), related_name='arrived_packages',
                                    blank=True, null=True, on_delete=models.PROTECT)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])

    inventory_employee = models.ForeignKey(User, verbose_name=_("inventory_employee"),
                                           limit_choices_to={'is_staff': True}, null=True, blank=True,
                                           on_delete=models.SET_NULL)

    note = models.TextField(verbose_name=_("note"), blank=True)

    details = models.TextField(verbose_name=_("details"), blank=True)

    item_names = models.TextField(verbose_name=_("item_names"), blank=True)

    origin_details = models.TextField(verbose_name=_("origin_details"), blank=True)

    vendor_payment = models.ForeignKey("VendorPayment", verbose_name=_("vendor_payment"), null=True, blank=True,
                                       on_delete=models.SET_NULL)
    shipment_logistics = models.ForeignKey("ShipmentLogistics", verbose_name=_("shipment_logistics"), null=True,
                                           blank=True, on_delete=models.SET_NULL)

    order_item = models.ManyToManyField('OrderItem', verbose_name=_("order_item"),related_name='ShipmentPackage_order_item_set', through='OrderPackageItem')

    orderpackage = models.ManyToManyField('OrderPackage', verbose_name=_("ShipmentPackage_orderpackage"),
                                          related_name='ShipmentPackage_orderpackage_set', through='OrderPackageItem')

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name='customer_packages', null=True,
                                 blank=True, on_delete=models.SET_NULL)
    customer_payment = models.ForeignKey("CustomerPayment", verbose_name=_("customer_payment"), null=True, blank=True,
                                         on_delete=models.SET_NULL)
    fragile = models.BooleanField(verbose_name=_("fragile"), default=False)
    packing = models.BooleanField(verbose_name=_("packing"), default=False)
    ecommerce = models.BooleanField(verbose_name=_("ecommerce"), default=False)

    flag = models.BooleanField(verbose_name=_("flag"), default=False)

    updated = models.BooleanField(verbose_name=_("updated"), default=False)

    @property
    def first_image_url(self):
        order_items = self.order_item.exclude(Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved'))
        if order_items.exists():

            return order_items.first().image_url
        else:
            return ''


    @property
    def status_tag(self):
        if self.status:
            return self.status.label
        else:
            return self.status
    @property
    def customer_full_name(self):
        if self.customer:
            return self.customer.profile.full_name
        else:
            return self.customer

    @property
    def customer_tag(self):
        if self.customer:
            return self.customer.username
        else:
            return self.customer
    @property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created

    @property
    def created_by_username(self):
        if self.created_by:
            return self.created_by.username
        else:
            return self.created_by

    @property
    def arrived_by_username(self):
        if self.arrived_by:
            return self.arrived_by.username
        else:
            return self.arrived_by

    @property
    def arrived_tag(self):
        if self.arrived:
            return self.arrived.strftime("%d-%m-%Y %H:%M")
        else:
            return self.arrived
    @property
    def exported_tag(self):
        if self.exported:
            return self.exported.strftime("%d-%m-%Y %H:%M")
        else:
            return self.exported
    @property
    def exported_by_username(self):
        if self.exported_by:
            return self.exported_by.username
        else:
            return self.exported_by
    @property
    def delivered_by_username(self):
        if self.delivered_by:
            return self.delivered_by.username
        else:
            return self.delivered_by

    @property
    def delivered_tag(self):
        if self.delivered:
            return self.delivered.strftime("%d-%m-%Y %H:%M")
        else:
            return self.delivered
    @property
    def calculate_mass(self):
        if self.height and self.length and self.width:

            return '{:,.2f}'.format((self.height/100*self.length/100*self.width/100))
        else:
            return decimal.Decimal(0)

    def calculate_Shipment_item(self):
        # ::type: dict
        decimal.getcontext().rounding = decimal.ROUND_UP
        result = self.order_item.distinct().all().exclude(
            Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved')).aggregate(
            _count_id=Count(F('id')),
            _count_order_item=Sum(F('quantity')),
            _sum_paid_order_item=Sum(F('paid_quantity')),
            _sum_order_order_item=Sum(F('order_quantity')),
            _sum_price_item=Sum(F('price')*F('quantity'),output_field=DecimalField()),
            _sum_shipping_item=Sum(F('shipping')),
            _sum_paid_shipping=Sum(F('paid_shipping')),
            _sum_paid_shipping_vnd=Sum(F('paid_shipping')*F('exchange_rate'),output_field=DecimalField()),
            _total_item_price=Sum(((F('price') * F('quantity')) + F('shipping') + F('service_charge') + F(
                'insurance_charge') + F('fragile_charge') + F('rocket_charge') + F('packing_charge') + F(
                'rocket_ship_charge') + F('bargain_charge')) * F('exchange_rate'), output_field=DecimalField()),
        )
        for key, value in list(result.items()):
            setattr(self, key, value)

    @property
    def sum_paid_shipping(self):
        if not hasattr(self, '_sum_paid_shipping'):
            self.calculate_Shipment_item()
        if self._sum_paid_shipping:
            return self._sum_paid_shipping
        else:
            return 0

    @property
    def shipping_cost_vnd(self):
        return self.shipping_cost * self.exchange_rate

    @property
    def cost_to_pay(self):
        return self.weight*self.weight_cost

    @property
    def sum_price_item(self):
        if not hasattr(self, '_sum_price_item'):
            self.calculate_Shipment_item()
        if self._sum_price_item:
            return self._sum_price_item
        else:
            return 0

    @property
    def total_item_price(self):
        if not hasattr(self, '_total_item_price'):
            self.calculate_Shipment_item()
        if self._total_item_price:
            return self._total_item_price
        else:
            return 0

    @property
    def need_to_pay(self):
        #tiền kg phải trả cho kiện này


        #toàn bộ sản phẩm trong kiện được tính
        list_item_in_shipment = OrderItem.objects.filter(
            pk__in=self.order_item.all()).exclude(
            Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved')).distinct()

        #toàn bộ order trong kiện đó
        list_order = Order.objects.filter(orderitem__in=self.order_item.all()).distinct()
        if list_order.exists():
            #khách đã thanh toán trong toàn bộ order
            sum_order_payment_transaction = sum([i.sum_payment_transaction for i in list_order])
            #toàn bộ phụ thu của order đó
            sum_total_extra_price = sum([i.total_extra_price for i in list_order])

            #toàn bộ sản phẩm trong đơn hàng, loại trừ sản phẩn của vận đơn được tính
            list_item = OrderItem.objects.filter(order__in=list_order).exclude(Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved')).exclude(pk__in=self.order_item.all()).distinct()



            #toàn bộ sản phẩm đang được chốt tiền và sản phẩm đã giao, loại trừ kiện hàng đang được tính
            list_item_completed = list_item.filter(Q(status__value='delivered_ship') | Q(status__value='pending_paid') | Q(status__value='pending_order')).distinct()



            #toàn bộ sản phẩm cần phải cọc loại trừ kiện hàng đang được tính
            list_item_prepaid = list_item.exclude(Q(status__value='delivered_ship') | Q(status__value='pending_paid') | Q(status__value='pending_order')).distinct()




            # list_item_in_exported = list_item.filter(Q(status__value='delivered_ship') | Q(status__value='pending_paid') | Q(status__value='pending_order'), shipmentpackage__in=self.exported_shipment.exported_shipment_service.all()).distinct()
            #
            #
            # calculate_list_item_in_exported = list_item_in_exported.aggregate(
            #     _count_id=Count(F('id')),
            #     _total_item_price=Sum(((F('price')*F('quantity'))+F('shipping')+F('service_charge')+F('insurance_charge')+F('fragile_charge')+F('rocket_charge')+F('packing_charge')+F('rocket_ship_charge')+F('bargain_charge'))*F('exchange_rate'),output_field=DecimalField(), distinct=True))

            # if calculate_list_item_in_exported['_total_item_price']:
            #     total_list_item_in_exported = calculate_list_item_in_exported['_total_item_price']
            # else:
            #     total_list_item_in_exported = 0



            #tính sản phẩm trong kiện hàng đang được tính
            calculate_list_item_in_shipment = list_item_in_shipment.aggregate(
                _count_id=Count(F('id')),
                _total_item_price=Sum(((F('price')*F('quantity'))+F('shipping')+F('service_charge')+F('insurance_charge')+F('fragile_charge')+F('rocket_charge')+F('packing_charge')+F('rocket_ship_charge')+F('bargain_charge'))*F('exchange_rate'),output_field=DecimalField(), distinct=True),
            )
            #tính sản phẩm đã giao và đang được chốt
            calculate_list_item_completed = list_item_completed.aggregate(
                _count_id=Count(F('id')),
                _total_item_price=Sum(((F('price')*F('quantity'))+F('shipping')+F('service_charge')+F('insurance_charge')+F('fragile_charge')+F('rocket_charge')+F('packing_charge')+F('rocket_ship_charge')+F('bargain_charge'))*F('exchange_rate'),output_field=DecimalField(), distinct=True),
            )
            #tính sản phẩm cần cọc
            calculate_list_item_prepaid = list_item_prepaid.aggregate(
                _count_id=Count(F('id')),
                _total_item_price=Sum(((F('price')*F('quantity'))+F('shipping')+F('service_charge')+F('insurance_charge')+F('fragile_charge')+F('rocket_charge')+F('packing_charge')+F('rocket_ship_charge')+F('bargain_charge'))*F('exchange_rate'),output_field=DecimalField(), distinct=True),
            )


            if calculate_list_item_completed['_total_item_price']:
                total_item_price_completed = calculate_list_item_completed['_total_item_price']
            else:
                total_item_price_completed = 0

            if calculate_list_item_prepaid['_total_item_price']:
                total_item_price_prepaid = calculate_list_item_prepaid['_total_item_price']
            else:
                total_item_price_prepaid = 0

            if calculate_list_item_in_shipment['_total_item_price']:
                total_item_in_shipment = calculate_list_item_in_shipment['_total_item_price']
            else:
                total_item_in_shipment = 0

            # tinh kien ship
            # list_item_order = OrderItem.objects.filter(order__in=list_order).exclude(
            #     Q(status__value='canceled') | Q(status__value='Failed') | Q(status__value='unapproved')).distinct()


            list_shipment = ShipmentPackage.objects.filter(Q(status__value='delivered_ship') | Q(status__value='pending_paid') | Q(status__value='pending_order'),order_item__in=list_item).exclude(pk=self.pk).distinct()

            calculate_list_shipment = list_shipment.aggregate(
                _count_id=Count(F('id')),
                _total_weight_to_pay=Sum(F('weight')*F('weight_cost'),output_field=DecimalField(), distinct=True),
            )

            if calculate_list_shipment['_total_weight_to_pay']:
                total_weight_to_pay = calculate_list_shipment['_total_weight_to_pay']
            else:
                total_weight_to_pay = decimal.Decimal(0)


            prepaid_rate = (sum_order_payment_transaction-total_weight_to_pay)/(total_item_in_shipment+total_item_price_completed+total_item_price_prepaid+sum_total_extra_price)


            #total_item_price_completed + ((total_item_price_prepaid+total_list_item_in_exported)* decimal.Decimal(0.7)) + total_item_in_shipment + self.cost_to_pay + total_weight_to_pay + sum_total_extra_price - sum_order_payment_transaction

            total_item_need_to_pay = total_item_in_shipment+self.cost_to_pay+total_item_price_completed+(total_item_price_prepaid*decimal.Decimal(prepaid_rate))+total_weight_to_pay+sum_total_extra_price-sum_order_payment_transaction
        else:
            total_item_need_to_pay = self.cost_to_pay

        return round(total_item_need_to_pay,0)

    @property
    def prepaid_percent(self):
        if self.order and self.order.sum_payment_transaction:
            return (decimal.Decimal(self.order.sum_payment_transaction)-decimal.Decimal(self.order.sum_shipment_cost)-decimal.Decimal(self.order.total_extra_price))/decimal.Decimal(self.order.total_item_cost_not_shipment)
        else:
            return 0

    @property
    def fake_sum_price(self):
        return decimal.Decimal(random.randint(150, 270) * 3300)


    @property
    def sum_shipping_item(self):
        if not hasattr(self, '_sum_shipping_item'):
            self.calculate_Shipment_item()
        if self._sum_shipping_item:
            return self._sum_shipping_item
        else:
            return 0

    @property
    def sum_paid_shipping(self):
        if not hasattr(self, '_sum_paid_shipping'):
            self.calculate_Shipment_item()
        if self._sum_paid_shipping:
            return self._sum_paid_shipping
        else:
            return 0

    @property
    def sum_paid_shipping_vnd(self):
        if not hasattr(self, '_sum_paid_shipping_vnd'):
            self.calculate_Shipment_item()
        if self._sum_paid_shipping_vnd:
            return self._sum_paid_shipping_vnd
        else:
            return 0

    @property
    def sum_order_order_item(self):
        if not hasattr(self, '_sum_order_order_item'):
            self.calculate_Shipment_item()
        if self._sum_order_order_item:
            return self._sum_order_order_item
        else:
            return 0

    @property
    def sum_paid_order_item(self):
        if not hasattr(self, '_sum_paid_order_item'):
            self.calculate_Shipment_item()
        if self._sum_paid_order_item:

            return self._sum_paid_order_item
        else:
            return 0

    @property
    def count_order_item(self):
        if not hasattr(self, '_count_order_item'):
            self.calculate_Shipment_item()
        if self._count_order_item:

            return self._count_order_item
        else:
            return 0

    def __str__(self):
        return str("%s" % (str(self.tracking_number)))



class ShipmentDocuments(models.Model):
    class Meta:
        verbose_name = _("ShipmentDocuments")
        verbose_name_plural = _("ShipmentDocuments")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    url = models.CharField(verbose_name=_("url"), max_length=2048, blank=True)

    document = models.ForeignKey(Document, verbose_name=_("document"), related_name="file_document",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)



    def __str__(self):
        return str(self.url)

class ShipmentPackageImages(models.Model):
    class Meta:
        verbose_name = _("ShipmentPackageImages")
        verbose_name_plural = _("ShipmentPackageImages")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    image_url = models.CharField(verbose_name=_("image_url"), max_length=2048, blank=True)

    images_document = models.ForeignKey(ImagesDocument, verbose_name=_("images_document"), related_name="images_document_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)

    shipment_package = models.ForeignKey(ShipmentPackage, verbose_name=_("shipment_package"), related_name="shipment_images_set",
                                    on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True,
                                    blank=True)

    def __str__(self):
        return str(self.image_url)

class ShipmentPackageTracking(models.Model):
    class Meta:
        verbose_name = _("ShipmentPackageTracking")
        verbose_name_plural = _("ShipmentPackageTracking")


    shipment_package_item = models.ForeignKey('ShipmentPackage', verbose_name=_("shipment_package_item"))

    logistics_package = models.ForeignKey('ShipmentLogistics', verbose_name=_("logistics_package"))



    def __str__(self):
        return "%s" % (str(self.shipment_package_item)[:100])

class ShipmentLogistics(models.Model):
    class Meta:
        verbose_name = _("ShipmentLogistics")
        verbose_name_plural = _("ShipmentLogistics")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    departed = models.DateTimeField(verbose_name=_("departed"), blank=True, null=True)
    arrived = models.DateTimeField(verbose_name=_("arrived"), blank=True, null=True)
    delivered = models.DateTimeField(verbose_name=_("delivered"), blank=True, null=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), limit_choices_to={'is_shipmentstatus': True},
                               on_delete=models.PROTECT, null=True)

    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=XRATE_MAX_DIGITS,
                                 decimal_places=XRATE_DECIMAL_PLACES,validators=[MinValueValidator(0)],db_index=True)

    orderitem_set = models.ManyToManyField('ShipmentPackage', verbose_name=_("orderitem_set"),
                                                 through='ShipmentPackageTracking')

    tracking_number = models.CharField(verbose_name=_("tracking_number"), blank=True, max_length=512, db_index=True, null=True)

    shipment_service = models.ForeignKey("ShipmentService", verbose_name=_("shipment_service"), null=True, blank=True,
                                         on_delete=models.PROTECT)
    shipment_method = models.CharField(verbose_name=_("shipment_method"), blank=True, max_length=512, db_index=True)

    location = models.ForeignKey("ShipmentLocation", verbose_name=_("location"), related_name='departed_container',
                                 blank=True, null=True, on_delete=models.PROTECT)
    destination = models.ForeignKey("ShipmentLocation", verbose_name=_("destination"), related_name='arrived_container',
                                    blank=True, null=True, on_delete=models.PROTECT)

    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(verbose_name=_("shipping_cost"), default=decimal.Decimal(0),
                                        max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)], db_index=True)
    tax_cost = models.DecimalField(verbose_name=_("tax_cost"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)

    inventory_employee = models.ForeignKey(User, verbose_name=_("inventory_employee"),
                                           limit_choices_to={'is_staff': True}, null=True, blank=True,
                                           on_delete=models.SET_NULL)

    note = models.TextField(verbose_name=_("note"), blank=True)

    logistics_payment = models.ForeignKey("LogisticsPayment", verbose_name=_("logistics_payment"), null=True,
                                          blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str("{%s} (%s)" % (self.pk, str(self.status)))

class ShipmentStatus(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    time = models.DateTimeField(verbose_name=_("time"))
    ftime = models.DateTimeField(verbose_name=_("ftime"))
    context = models.CharField(verbose_name=_("context"), blank=True, max_length=512)
    location = models.CharField(verbose_name=_("context"), blank=True, max_length=512)
    shipment_packs = models.ForeignKey('ShipmentPacks', verbose_name=_('shipment_packs'))

class ShipmentPacks(BaseModel):
    version = IntegerVersionField()
    tracking_number = models.CharField(max_length=255, verbose_name=_('tracking_number'), null=True)
    order = models.ForeignKey("Order", verbose_name=_("order"), null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(verbose_name=_("note"), blank=True)
    company = models.CharField(verbose_name=_("company"), blank=True, max_length=255)
    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2)
    status = models.ForeignKey('ShipmentStatus', verbose_name=_('status'))
