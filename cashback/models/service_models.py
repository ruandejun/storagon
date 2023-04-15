#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  product_models.py
#
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#

from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import Sum, F, Count
import uuid, decimal, logging, json, re
from ..constants.DefaultSettings import *

from audit_log.models.fields import CreatingUserField, LastUserField

from mptt.models import MPTTModel, TreeForeignKey



class ServiceType(models.Model):
    class Meta:
        verbose_name = _("ServiceType")
        verbose_name_plural = _("ServiceType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)

    def __str__(self):
        return str(self.label)



class ServiceOrder(models.Model):
    class Meta:
        verbose_name = _("ServiceOrder")
        verbose_name_plural = _("ServiceOrder")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    customer = models.CharField(verbose_name=_("customer"), blank=True, null=True, max_length=255, db_index=True)

    shopping_domain = models.CharField(verbose_name=_("shopping_domain"), blank=True, max_length=255, db_index=True)

    vendor = models.CharField(verbose_name=_("vendor"), blank=True, max_length=255, db_index=True)
    vendor_id = models.CharField(verbose_name=_("vendor_id"), blank=True, max_length=255, db_index=True)
    vendor_address = models.CharField(verbose_name=_("vendor_address"), blank=True, max_length=255, db_index=True)
    vendor_url = models.CharField(verbose_name=_("vendor_url"), blank=True, max_length=255, db_index=True)

    detail_url = models.CharField(verbose_name=_("detail_url"), blank=True, max_length=2048)
    name = models.CharField(verbose_name=_("name"), blank=True, max_length=512, db_index=True)
    sku = models.CharField(verbose_name=_("sku"), blank=True, max_length=512, db_index=True)
    image_url = models.CharField(verbose_name=_("image_url"), blank=True, max_length=2048)
    short_description = models.TextField(verbose_name=_("short_description"), blank=True)
    currency = models.CharField(verbose_name=_("currency"), max_length=255, db_index=True)
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=decimal.Decimal(0),
                                        max_digits=XRATE_MAX_DIGITS, decimal_places=XRATE_DECIMAL_PLACES,
                                        validators=[MinValueValidator(0)])
    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    shipping = models.DecimalField(verbose_name=_("shipping"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)
    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=8);
    quantity = models.PositiveIntegerField(verbose_name=_("quantity"), default=1)

    min_quantity = models.PositiveIntegerField(verbose_name=_("min_quantity"),null=True, blank=True, default=1)

    price_ranges = models.CharField(verbose_name=_("price_ranges"), blank=True, max_length=2048)

    options_selected = models.TextField(verbose_name=_("options_selected"), blank=True)
    options_metadata = models.TextField(verbose_name=_("options_metadata"), blank=True)
    category_list = models.CharField(verbose_name=_("category_list"), max_length=512, blank=True)
    fragile = models.BooleanField(verbose_name=_("fragile"), default=False)
    insurance = models.BooleanField(verbose_name=_("insurance"), default=False)
    rocket = models.BooleanField(verbose_name=_("rocket"), default=False)
    packing = models.BooleanField(verbose_name=_("packing"), default=False)
    service = models.BooleanField(verbose_name=_("service"), default=True)
    bargain = models.BooleanField(verbose_name=_("bargain"), default=False)
    rocket_ship = models.BooleanField(verbose_name=_("rocket_ship"), default=False)
    note = models.CharField(verbose_name=_("note"), max_length=1024, blank=True)
    html = models.TextField(verbose_name=_("html"), blank=True)


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


    product_id = models.PositiveIntegerField(verbose_name=_("product_id"), default=0)
    http_referer = models.CharField(verbose_name=_("http_referer"), max_length=2048, blank=True)

    def __str__(self):
        return str("%s: %s" % (self.shopping_domain, self.name))

    @property
    def option_selected_tag(self):
        try:
            option_selected = json.loads(self.options_selected)
        except ValueError:
            return re.sub(r"u'", "'", re.sub(r'\s*,\s*u?', '\n', self.options_selected)).lstrip('{').rstrip('}')
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
            return string
            # return '\n'.join([key + ':' + value for key, value in list(option_selected.items())])

    @property
    def total_vendor_quantity(self):
        calculator_orderitem=CartItem.objects.filter(vendor=self.vendor).aggregate(total_quantity=Sum(F('quantity')))
        return calculator_orderitem['total_quantity']

    @property
    def total_service_cost(self):
        return decimal.Decimal(self.service_charge) + decimal.Decimal(self.insurance_charge) + decimal.Decimal(self.packing_charge) + decimal.Decimal(self.rocket_charge) + decimal.Decimal(self.packing_charge) + decimal.Decimal(self.bargain_charge)