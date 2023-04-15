#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  shop_models.py
#  
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#


import decimal
from audit_log.models.fields import CreatingUserField, LastUserField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..constants.DefaultSettings import *
from ..enums import *


class Currency(models.Model):
    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currency")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    code = models.CharField(verbose_name=_("code"), max_length=255, primary_key=True, unique=True,
                            help_text=_('Required. 3 uppercase characters.'),
                            validators=[RegexValidator(r'^[A-Z]{3}$', _('Enter a valid currency code.'), 'invalid'), ]
                            )
    exchange_rate = models.DecimalField(verbose_name=_("exchange_rate"), default=1.0, max_digits=XRATE_MAX_DIGITS,
                                        decimal_places=XRATE_DECIMAL_PLACES, validators=[MinValueValidator(0.0001)])
    label = models.CharField(verbose_name=_("label"), max_length=16)

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __str__(self):
        return str(self.code)

    @staticmethod
    def Convert(amount, exchange_rate):
        if not amount:
            return 0
        return amount * exchange_rate

    def convert(self, amount, exchange_rate=None):
        if not exchange_rate:
            exchange_rate = self.exchange_rate;
        return Currency.Convert(amount, exchange_rate)

    @staticmethod
    def Invert(common_amount, exchange_rate):
        if not common_amount or not exchange_rate: return 0
        value = common_amount / exchange_rate
        return decimal.Decimal(value).quantize(decimal.Decimal(str(10 ** -MONEY_DECIMAL_PLACES)),
                                               rounding=decimal.ROUND_UP)

    def invert(self, common_amount, exchange_rate=None):
        if not exchange_rate:
            exchange_rate = self.exchange_rate
        value = common_amount / exchange_rate
        return Currency.Invert(common_amount, exchange_rate)

    def display(self, amount, separator=','):
        d = format(amount, '%s.2f' % separator)
        return str(d + ' ' + self.__str__())


class Status(models.Model):
    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)
    logic_step = models.PositiveSmallIntegerField(verbose_name=_("logic_step"), choices=LogicStep.ChoiceList(),
                                                  default=LogicStep.pending, db_index=True)

    is_orderstatus = models.BooleanField(verbose_name=_("is_orderstatus"), default=True, db_index=True)
    is_shipmentstatus = models.BooleanField(verbose_name=_("is_shipmentstatus"), default=False, db_index=True)


    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __str__(self):
        return str(self.label) or ''


class Vendor(models.Model):
    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendor")
        unique_together = ('shopping_domain', 'name')

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    shopping_domain = models.CharField(verbose_name=_("shopping_domain"), blank=True, max_length=255, db_index=True)
    name = models.CharField(verbose_name=_("name"), max_length=255, db_index=True)
    label = models.CharField(verbose_name=_("label"), blank=True, max_length=255)
    shop_url = models.CharField(verbose_name=_("shop_url"), blank=True, max_length=2048)
    note = models.TextField(verbose_name=_("note"), blank=True)

    def __str__(self): return str(self.label if self.label else self.name)
