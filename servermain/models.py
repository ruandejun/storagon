#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  models.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings  # site setting
from storagon.PrivateAPI_SDK import SignalSDK
from storagon.enum import *
from storagon.tool import *
from .mongo_models import UserStorage, ServerFileStorage, Session
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
import base64
import hashlib
import random, re
from Crypto.Cipher import AES
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.DO_NOTHING)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    full_name = models.CharField(max_length=255, db_index=True)
    email = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    address = models.TextField(blank=True) #, verbose_name=u"Địa chỉ nhà"
    account_type = models.PositiveSmallIntegerField(choices=AccountType.ChoiceList(), default=AccountType.user, db_index=True)
    account_status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal, db_index=True)

    storage_space = models.BigIntegerField(default=0, db_index=True)

    plan_id = models.PositiveIntegerField(default=0, db_index=True)
    plan_expired = models.DateTimeField(default=timezone.now,blank=True, db_index=True)

    referer = models.ForeignKey(User, related_name='refererList', blank=True, null=True, on_delete=models.SET_NULL)  # referer level 1
    referer2 = models.ForeignKey(User, related_name='referer2List', blank=True, null=True, on_delete=models.SET_NULL)  # referer level 2

    eumk = models.CharField(blank=True, null=True, max_length=1024)

    signup_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    def getPlanID(self):
        if self.plan_expired and self.plan_expired > timezone.now():
            return self.plan_id
        else:
            return 0;

    def isAffiliate(self):
        return self.account_type == AccountType.affiliate or self.account_type == AccountType.affiliatePPD

    def __unicode__(self): return self.user


def generateID():
    return base64.urlsafe_b64encode(os.urandom(16))[:-2]


class UserFile(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    file_name = models.CharField(max_length=255, db_index=True)
    realFile = models.ForeignKey('RealFile',on_delete=models.DO_NOTHING)
    folder = models.ForeignKey('Folder', related_name='fileList', on_delete=models.DO_NOTHING, blank=True, null=True)

    erfk = models.CharField(blank=True, null=True, max_length=1024)

    last_download_date = models.DateTimeField(auto_now_add=True, db_index=True)
    download_count = models.PositiveIntegerField(default=0, db_index=True)

    file_mode = models.PositiveSmallIntegerField(choices=FileMode.ChoiceList(), default=FileMode.normal, db_index=True)
    string_id = models.CharField(max_length=255, db_index=True, default=generateID)

    @property
    def file_size(self): return self.realFile.file_size

    @property
    def file_hash(self): return self.realFile.file_hash

    def download_tag(self):
        dlink = self.get_absolute_url(withFileKey=False, usingDownloadViewNumber=2)
        return format_html('<a href="{}">{}</a>', dlink, dlink[:20])
    download_tag.allow_tags = True

    def get_absolute_url(self, withFileKey=True, usingDownloadViewNumber=1):
        if usingDownloadViewNumber==1: url = reverse('download', args=(self.id, self.file_name))
        else: url = reverse('download2', args=(self.id, self.string_id))
        if withFileKey and self.erfk:
            try:
                eumk = base64.b64decode(self.user.profile.eumk)
                cipher = AES.new(eumk, AES.MODE_ECB)
                erfk = str(cipher.decrypt(base64.b64decode(self.erfk)))
            except:
                return url;

            if not re.search(r'[0-9a-f]{32}', erfk):
                return url;

            return url + '#' + erfk
        else:
            return url

    def __unicode__(self):
        if len(self.file_name) > 20:
            return self.file_name[:20] + '...'
        return self.file_name

    def clean(self):
        if self.folder and self.folder.user != self.user:
            raise ValidationError(u'folder must belong to same user with file in that folder')


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    parent_folder = models.ForeignKey('Folder', related_name='subFolderList', on_delete=models.DO_NOTHING, blank=True, null=True)
    folder_type = models.PositiveSmallIntegerField(choices=FolderType.ChoiceList(), default=FolderType.normal, db_index=True)

    def __unicode__(self):
        return self.name;
        # if self.parent_folder:
        # 	temp = unicode(self.parent_folder)
        # else:
        # 	temp = ''
        # return "%s/%s" % (temp, self.name)

    def clean(self):
        if self.parent_folder and self.parent_folder.user != self.user:
            raise ValidationError(u'parent_folder must belong to same user with child folder')
        if self.parent_folder == self:
            raise ValidationError(u'parent_folder must not reference to self')


class RealFile(models.Model):
    serverFile = models.ForeignKey('ServerFile', blank=False, null=True, on_delete=models.PROTECT)  # prevent a deletion of a ServerFile if there are still RealFile belong to it
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    file_size = models.BigIntegerField(default=0, db_index=True)
    file_hash = models.CharField(max_length=255, db_index=True)
    file_location = models.CharField(max_length=255, db_index=True)

    # last_download_date = models.DateTimeField(auto_now_add=True, db_index=True)
    # download_count = models.PositiveIntegerField(default=0, db_index=True)

    def __unicode__(self): return self.file_location


class ServerFile(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    server_status = models.PositiveSmallIntegerField(choices=ServerStatus.ChoiceList(), default=ServerStatus.normal, db_index=True)
    ip_address = models.CharField(max_length=255, db_index=True)
    server_address = models.CharField(max_length=255, db_index=True)
    priority = models.PositiveSmallIntegerField(default=0, db_index=True)  # 0 = highest priority, the lower the better
    total_storage = models.BigIntegerField(default=0, db_index=True)
    reserved_storage = models.BigIntegerField(default=0, db_index=True)


    def __unicode__(self): return "%s: %s" % (self.name, self.server_address)


# Payment

class Bill(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    userFile = models.ForeignKey(UserFile, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    bill_status = models.PositiveSmallIntegerField(choices=BillStatus.ChoiceList(), default=BillStatus.ok, db_index=True)
    paygate_id = models.PositiveIntegerField(default=0, db_index=True)
    plan_id = models.PositiveIntegerField(default=0, db_index=True)
    money_charged = models.BigIntegerField(default=0, db_index=True)

    detail = models.TextField(blank=True)


    def __unicode__(self): return "BillNo.%s(plan_%s)" % (self.id, self.plan_id)


class AccountCurrency(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    code = models.CharField(verbose_name=_("code"), max_length=255, primary_key=True, unique=True,
                            help_text=_('Required. 3 uppercase characters.'),
                            validators=[RegexValidator(r'^[A-Z]{3}$', _('Enter a valid currency code.'), 'invalid'), ]
                            )

    label = models.CharField(verbose_name=_("label"), max_length=16)

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, db_index=True)

    def __unicode__(self):
        return "%s" % (self.code)


class AccountBalance(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    balance_type = models.PositiveSmallIntegerField(choices=BalanceType.ChoiceList(), default=BalanceType.credit, db_index=True)
    currency = models.ForeignKey(AccountCurrency,blank=True, null=True, on_delete=models.SET_NULL)
    amount = models.BigIntegerField(default=0, db_index=True)
    account_id = models.CharField(default='', max_length=255, db_index=True)
    address = models.CharField(default='', verbose_name=_("address"), max_length=255)

    def __unicode__(self):
        return "%s %s" % (self.user, BalanceType.AllLabelList()[self.balance_type])


class TransactionLog(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    transaction_type = models.PositiveSmallIntegerField(choices=TransactionType.ChoiceList(), default=TransactionType.agency, db_index=True)
    transaction_status = models.PositiveSmallIntegerField(choices=TransactionStatus.ChoiceList(), default=TransactionStatus.auto, db_index=True)
    balance = models.ForeignKey('AccountBalance', null=True, on_delete=models.SET_NULL)
    amount = models.BigIntegerField(default=0, db_index=True)

    invoice_bill = models.ForeignKey(Bill, blank=True, null=True, on_delete=models.SET_NULL)

    transaction_id = models.CharField(default='', max_length=255, db_index=True)

    data = models.TextField(blank=True)


    def __unicode__(self): return "%s <= %s" % (self.balance, self.invoice_bill)



# Extra


class Banlist(models.Model):
    key = models.CharField(max_length=255, primary_key=True, unique=True)
    expires_date = models.DateTimeField(blank=True, null=True, default=None, db_index=True)
    enable = models.BooleanField(default=True, db_index=True)


    def __unicode__(self): return self.pk


class PremiumKey(models.Model):
    reseller = models.ForeignKey(User, related_name='resellPremiumKey', null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=255, unique=True)
    plan_id = models.PositiveSmallIntegerField(default=0, db_index=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    activated_date = models.DateTimeField(blank=True, null=True, default=None, db_index=True)
    activated_user = models.ForeignKey(User, related_name='activatedPremiumKey', null=True, on_delete=models.SET_NULL)

    bill = models.OneToOneField(Bill, null=True, on_delete=models.SET_NULL)

    def __unicode__(self): return self.code


class UserApply(models.Model):
    user = models.ForeignKey(User, related_name='application', on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    apply_type = models.PositiveSmallIntegerField(choices=ApplyType.ChoiceList(), default=ApplyType.becomeAffiliate, db_index=True)
    apply_status = models.PositiveSmallIntegerField(choices=ApplyStatus.ChoiceList(), default=ApplyStatus.processing, db_index=True)

    # amount = models.BigIntegerField(default=0, db_index=True);
    # website_address = models.CharField(max_length=255, blank=True, db_index=True)  # domain of website agency, host

    data = models.TextField(blank=True,null=True, default='');

    def __unicode__(self): return '%s - %s'%(self.user, ApplyType.AllLabelList()[self.apply_type]);


class WebsiteAgency(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    website_domain = models.CharField(max_length=255, blank=True, unique=True, db_index=True)  # domain of website agency, host
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
