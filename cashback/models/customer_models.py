#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  customer_models.py
#
#
#  Created by TVA on 3/28/16.
#  Copyright (c) 2016 ordercn. All rights reserved.
#


from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..enums import *


class CustomerProfile(models.Model):

    class Meta:
        verbose_name = _("CustomerProfile")
        verbose_name_plural = _("CustomerProfile")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    user = models.OneToOneField(User, verbose_name=_("user"), related_name='customerProfile', editable=False)
    city = models.CharField(verbose_name=_("city"), blank=True, max_length=512, db_index=True)
    district = models.CharField(verbose_name=_("district"), blank=True, max_length=512, db_index=True)
    street = models.CharField(verbose_name=_("street"), blank=True, max_length=512, db_index=True)
    receive_sms_notify = models.BooleanField(verbose_name=_("receive_sms_notify"), default=True)
    receive_email_notify = models.BooleanField(verbose_name=_("receive_email_notify"), default=True)
    gender = models.PositiveSmallIntegerField(verbose_name=_("gender"), choices=CustomerGender.ChoiceList(),
                                              default=CustomerGender.unknown, db_index=True)
    about = models.TextField(verbose_name=_("about"), blank=True,max_length=255)

    service_quantity = models.TextField(verbose_name=_("service_quantity"), blank=True,max_length=255)

    service_percent = models.TextField(verbose_name=_("service_percent"), blank=True,max_length=255)

    weight_rate = models.TextField(verbose_name=_("weight_rate"), blank=True,max_length=255)

    currency_discount = models.TextField(verbose_name=_("currency_discount"), blank=True,max_length=255)

    prepaid_rate = models.TextField(verbose_name=_("prepaid_rate"), blank=True, max_length=255)

    service_type = models.PositiveSmallIntegerField(choices=ServiceType.ChoiceList(),
                                                  default=ServiceType.default,
                                                  db_index=True)

    supporter_employee = models.ForeignKey(User, verbose_name=_("supporter_employee"),
                                           limit_choices_to={'is_staff': True}, null=True, blank=True,
                                           on_delete=models.SET_NULL)

    referrer = models.ForeignKey("self", verbose_name=_("referrer"), null=True, blank=True, on_delete=models.SET_NULL)

    is_referrer = models.BooleanField(verbose_name=_("is_referrer"), default=False)


    vip_status = models.PositiveSmallIntegerField(choices=VipStatus.ChoiceList(),
                                                  default=VipStatus.Normal,
                                                  db_index=True)
    referrer_text = models.CharField(verbose_name=_("referrer_text"), blank=True, null=True, max_length=512, db_index=True)


    order_by_black_list = models.ManyToManyField(User,verbose_name=_("order_by_black_list"),related_name="customerprofile_order_by_black_listset", blank=True)

    ordered_by = models.ForeignKey(User, verbose_name=_("ordered_by"), related_name="customerprofile_ordered_by_set", on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    takecare_by = models.ForeignKey(User, verbose_name=_("takecare_by"), related_name="customerprofile_takecare_by_set", on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)


    @property
    def full_name(self):
        return self.user.profile.full_name if self.user.profile.full_name \
            else (self.user.first_name + ' ' + self.user.last_name)

    @property
    def phone_number(self):
        return self.user.profile.phone_number

    @property
    def address(self):
        return self.user.profile.address

    @property
    def facebook(self):
        return self.user.profile.user_facebook

    def __str__(self):
        return str(self.user)
