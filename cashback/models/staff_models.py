#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  staff_models.py
#  
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#

import decimal
from audit_log.models.fields import CreatingUserField, LastUserField
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..constants.DefaultSettings import *


class EmployeeProfile(models.Model):
    class Meta:
        verbose_name = _("EmployeeProfile")
        verbose_name_plural = _("EmployeeProfile")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    user = models.OneToOneField(User, verbose_name=_("user"), related_name='employeeProfile', editable=False)
    emergency_number = models.CharField(verbose_name=_("emergency_number"), blank=True, max_length=255, db_index=True)
    superior_employee = models.ForeignKey("self", verbose_name=_("superior_employee"), null=True, blank=True,
                                          on_delete=models.SET_NULL)
    position = models.ForeignKey("EmployeePosition", verbose_name=_("position"), null=True, blank=True,
                                 on_delete=models.SET_NULL)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.SET_NULL)
    extra_salary = models.DecimalField(verbose_name=_("extra_salary"), default=decimal.Decimal(0),
                                       max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                       validators=[MinValueValidator(0)], db_index=True)
    is_active = models.BooleanField(verbose_name=_("is_active"), default=True)

    # do_job_cashier = models.BooleanField(verbose_name = _("do_job_cashier"),default=True)
    # do_job_inventory = models.BooleanField(verbose_name = _("do_job_inventory"),default=True)
    # do_job_order = models.BooleanField(verbose_name = _("do_job_order"),default=True)

    @property
    def full_name(self):
        return self.user.profile.full_name

    @property
    def phone_number(self):
        return self.user.profile.phone_number

    @property
    def address(self):
        return self.user.profile.address

    def __str__(self):
        return str("%s - %s" % (self.user, str(self.position)))


class EmployeePosition(models.Model):
    class Meta:
        verbose_name = _("EmployeePosition")
        verbose_name_plural = _("EmployeePosition")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    title = models.CharField(verbose_name=_("title"), blank=True, max_length=512)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), null=True, blank=True,
                                 on_delete=models.SET_NULL)
    base_salary = models.DecimalField(verbose_name=_("base_salary"), default=decimal.Decimal(0),
                                      max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                      validators=[MinValueValidator(0)], db_index=True)

    permission_groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True,
                                               help_text=_(
                                                   'The groups that all of these employee belongs to. A user will get all permissions granted to each of their groups.')
                                               )

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __str__(self):
        return str(self.title)
