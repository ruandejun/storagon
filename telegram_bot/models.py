#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from storagon.enum import *
from storagon.utils import get_current_user
import decimal
MONEY_MAX_DIGITS = getattr(settings, 'MONEY_MAX_DIGITS', 24)
MONEY_DECIMAL_PLACES = getattr(settings, 'MONEY_DECIMAL_PLACES', 2)
XRATE_MAX_DIGITS = getattr(settings, 'XRATE_MAX_DIGITS', 15)
XRATE_DECIMAL_PLACES = getattr(settings, 'XRATE_DECIMAL_PLACES', 0)
# Create your models here.

class CheckerType(models.Model):
    class Meta:
        verbose_name = _("CheckerType")
        verbose_name_plural = _("CheckerType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)

    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)   
    def __str__(self):
        return str(self.label)    
    
class CreatorType(models.Model):
    class Meta:
        verbose_name = _("CreatorType")
        verbose_name_plural = _("CreatorType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)

    
    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)   
    def __str__(self):
        return str(self.label)  

class CheckerTask(models.Model):
    class Meta:
        verbose_name = _("CheckerTask")
        verbose_name_plural = _("CheckerTask")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)  
    owner = models.ForeignKey(User, related_name='UserCheckerTask', blank=True, null=True, on_delete=models.DO_NOTHING)
    file_name = models.CharField(verbose_name=_("file_name"), blank=True, null=True, max_length=255)
    file_id = models.CharField(verbose_name=_("file_id"), blank=True, null=True, max_length=255)
    file_unique_id = models.CharField(verbose_name=_("file_unique_id"), blank=True, null=True, max_length=255)
    file_size = models.BigIntegerField(default=0, db_index=True)
    details = models.TextField(verbose_name=_("details"), blank=True, null=True, default='')
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    status = models.PositiveSmallIntegerField(choices=LinkStatus.ChoiceList(), default=LinkStatus.working,
                                                   db_index=True)  
      
    status_message_id = models.CharField(verbose_name=_("status_message_id"), blank=True, null=True, max_length=255)
    
    checker_type = models.ForeignKey(CheckerType, related_name='CheckerTask_checker_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    document = models.FileField(upload_to='checker_documents/%Y/%m/%d/')
    
    document_valid = models.FileField(upload_to='checker_documents_valid/%Y/%m/%d/', blank=True, null=True)
    document_invalid = models.FileField(upload_to='checker_documents_invalid/%Y/%m/%d/', blank=True, null=True)
    document_unknown = models.FileField(upload_to='checker_documents_unknown/%Y/%m/%d/', blank=True, null=True)
    
    display_page_valid = models.PositiveSmallIntegerField(default=1, db_index=True)

    display_page_invalid = models.PositiveSmallIntegerField(default=1, db_index=True)
    
    display_page_unknown = models.PositiveSmallIntegerField(default=1, db_index=True)
    
    total_value = models.PositiveSmallIntegerField(default=0, db_index=True)
    
    display_value = models.PositiveSmallIntegerField(choices=PageValue.ChoiceList(), default=PageValue.valid,
                                                   db_index=True) 

    @property
    def download_url(self): 
        if self.document:
            return self.document.url


    def __str__(self):
        return str(self.pk)

class CheckerValid(models.Model):
    class Meta:
        verbose_name = _("CheckerValid")
        verbose_name_plural = _("CheckerValid")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)  
    
    owner = models.ForeignKey(User, related_name='UserCheckerValid', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    details = models.TextField(verbose_name=_("details"), blank=True, null=True, default='')
    
    status = models.PositiveSmallIntegerField(choices=LinkStatus.ChoiceList(), default=LinkStatus.working,
                                                   db_index=True)    
    
    checker_task = models.ForeignKey(CheckerTask, related_name='CheckerTaskCheckerValid', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    checker_type = models.ForeignKey(CheckerType, related_name='CheckerValid_checker_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return str(self.details)

class CheckerInvalid(models.Model):
    class Meta:
        verbose_name = _("CheckerInvalid")
        verbose_name_plural = _("CheckerInvalid")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)  
    
    owner = models.ForeignKey(User, related_name='UserCheckerInvalid', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    details = models.TextField(verbose_name=_("details"), blank=True, null=True, default='')
    
    status = models.PositiveSmallIntegerField(choices=LinkStatus.ChoiceList(), default=LinkStatus.working,
                                                   db_index=True)    
    
    checker_task = models.ForeignKey(CheckerTask, related_name='CheckerTaskCheckerInvalid', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    checker_type = models.ForeignKey(CheckerType, related_name='CheckerInvalid_checker_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return str(self.details)

class CheckerUnknown(models.Model):
    class Meta:
        verbose_name = _("CheckerUnknown")
        verbose_name_plural = _("CheckerUnknown")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)  
    
    owner = models.ForeignKey(User, related_name='UserCheckerUnknown', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    details = models.TextField(verbose_name=_("details"), blank=True, null=True, default='')
    
    status = models.PositiveSmallIntegerField(choices=LinkStatus.ChoiceList(), default=LinkStatus.working,
                                                   db_index=True)    
    
    checker_task = models.ForeignKey(CheckerTask, related_name='CheckerTaskCheckerUnknown', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    checker_type = models.ForeignKey(CheckerType, related_name='CheckerUnknown_checker_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return str(self.details)    
    
class UserTelegram(models.Model):
    class Meta:
        verbose_name = _("User_Telegram")
        verbose_name_plural = _("User_Telegram")
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    user = models.ForeignKey(User, verbose_name=_("User"), related_name='user_telegram', on_delete=models.PROTECT)

    telegram_id = models.CharField(verbose_name=_("telegram_id"), blank=True, max_length=255, unique=True)

    first_name = models.CharField(verbose_name=_("first_name"), blank=True, max_length=255)

    last_name = models.CharField(verbose_name=_("last_name"), blank=True, max_length=255)

    username = models.CharField(verbose_name=_("username"), blank=True, max_length=255)
    
    checker_type = models.ForeignKey(CheckerType, related_name='checker_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    creator_type = models.ForeignKey(CreatorType, related_name='creator_type', blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.telegram_id)
    
class TelegramBot(models.Model):
    class Meta:
        verbose_name = _("TelegramBot")
        verbose_name_plural = _("TelegramBot")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    
    telegram_id = models.CharField(verbose_name=_("telegram_id"), blank=True, max_length=255)

    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)   
    def __str__(self):
        return str(self.telegram_id)     
     
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

    def __str__(self):
        return str(self.label) or ''

class AccountsType(models.Model):
    class Meta:
        verbose_name = _("AccountsType")
        verbose_name_plural = _("AccountsType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class KeysSearch(models.Model):
    class Meta:
        verbose_name = _("KeysSearch")
        verbose_name_plural = _("KeysSearch")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    value = models.CharField(verbose_name=_("value"), max_length=25, unique=True)
    # label = models.CharField(verbose_name=_("label"), max_length=255)
    # default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.value)

class MunProxies(models.Model):
    class Meta:
        verbose_name = _("MunProxies")
        verbose_name_plural = _("MunProxies")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT) 
    
    socks_port = models.CharField(verbose_name=_("socks_port"),blank=True, null=True, max_length=255, db_index=True, default='')
    control_port = models.CharField(verbose_name=_("control_port"),blank=True, null=True, max_length=255, db_index=True, default='')
    bridges_string = models.CharField(verbose_name=_("bridges_string"),blank=True, null=True, max_length=255, db_index=True, default='')
    rotating_time = models.CharField(verbose_name=_("rotating_time"),blank=True, null=True, max_length=255, db_index=True, default='')
    country_code = models.CharField(verbose_name=_("country_code"),blank=True, null=True, max_length=255, db_index=True, default='')
    country_name = models.CharField(verbose_name=_("country_name"),blank=True, null=True, max_length=255, db_index=True, default='')
    owner = models.ForeignKey(User, verbose_name=_("owner"), related_name="munproxies_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    def __str__(self):
        return str(self.socks_port)

class LinkCheckout(models.Model):
    class Meta:
        verbose_name = _("LinkCheckout")
        verbose_name_plural = _("LinkCheckout")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)  
    url = models.TextField(verbose_name=_("url"), blank=True, null=True, default='')
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    status = models.PositiveSmallIntegerField(choices=LinkStatus.ChoiceList(), default=LinkStatus.working,
                                                   db_index=True)    
    type = models.ForeignKey(AccountsType, verbose_name=_("type"),
                             related_name="link_type_set", null=True,
                             blank=True, on_delete=models.PROTECT)
    def __str__(self):
        return str(self.url)
    
class UserCheckFunction(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True) 
    user = models.ForeignKey(User, related_name='check_function', on_delete=models.DO_NOTHING)
    value = models.CharField(verbose_name=_("value"), max_length=255)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)      
    def __unicode__(self): return self.value
    
class UserCreateFunction(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    user = models.ForeignKey(User, related_name='create_function', on_delete=models.DO_NOTHING)
    value = models.CharField(verbose_name=_("value"), max_length=255)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)      
    def __unicode__(self): return self.value    

class UserHwid(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    user = models.ForeignKey(User, related_name='hwid', on_delete=models.DO_NOTHING)
    value = models.CharField(verbose_name=_("value"), max_length=255, db_index=True)
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)      
    last_poll = models.DateTimeField(verbose_name=_("last_poll"), null=True, blank=True, db_index=True)
    def __unicode__(self): return self.value    
    
class MunAnti(models.Model):
    class Meta:
        verbose_name = _("MunAnti")
        verbose_name_plural = _("MunAnti")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    version = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    update_url = models.CharField(max_length=9999, db_index=True)   
    def __str__(self):
        return str(self.version)
    
class AccountsSelling(models.Model):
    class Meta:
        verbose_name = _("AccountsSelling")
        verbose_name_plural = _("AccountsSelling")
        # abstract = True
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    warranty_date = models.DateTimeField(verbose_name=_("warranty_date"), null=True, blank=True)

    warranty = models.BooleanField(verbose_name=_("warranty"), default=False)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="accounts_customer_set", null=True,
                                 blank=True, on_delete=models.PROTECT)

    type = models.ForeignKey(AccountsType, verbose_name=_("type"),
                             related_name="type_set", null=True,
                             blank=True, on_delete=models.PROTECT)

    ordered = models.BooleanField(verbose_name=_("ordered"), default=False)

    ordered_date = models.DateTimeField(verbose_name=_("ordered_date"), null=True, blank=True)

    owner = models.ForeignKey(User, verbose_name=_("owner"), related_name="accounts_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)

    details = models.CharField(max_length=9999, db_index=True)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)

    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    signup_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    selling_status = models.PositiveSmallIntegerField(choices=SellingStatus.ChoiceList(), default=SellingStatus.listed,
                                                   db_index=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            self.modified_by = user
            if self._state.adding:
                self.created_by = user

        super(AccountsSelling, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.details

    def __str__(self):
        return self.type

class BrowserProfiles(models.Model):
    class Meta:
        verbose_name = _("BrowserProfiles")
        verbose_name_plural = _("BrowserProfiles")
        # abstract = True
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)
    
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    
    profile_owner = models.ForeignKey(User, verbose_name=_("profile_owner"), related_name="accounts_profile_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)

    profile_name = models.CharField(verbose_name=_("profile_name"),blank=True, null=True, max_length=255, db_index=True, default='')
    
    profile_os = models.CharField(verbose_name=_("profile_os"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_browser = models.CharField(verbose_name=_("profile_browser"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_version = models.CharField(verbose_name=_("profile_version"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_proxy_type = models.PositiveSmallIntegerField(choices=ProxyType.ChoiceList(), default=ProxyType.sock5,
                                            db_index=True)
    profile_proxy_details = models.CharField(verbose_name=_("profile_proxy_details"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_socks5_details = models.CharField(verbose_name=_("profile_socks5_details"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_proxy_username = models.CharField(verbose_name=_("profile_proxy_username"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_proxy_password = models.CharField(verbose_name=_("profile_proxy_password"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_path_cookies = models.CharField(verbose_name=_("profile_path_cookies"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_user_agent = models.CharField(verbose_name=_("profile_user_agent"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_original_name = models.CharField(verbose_name=_("profile_original_name"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_resolution = models.CharField(verbose_name=_("profile_resolution"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_cpu = models.CharField(verbose_name=_("profile_cpu"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_canvas = models.CharField(verbose_name=_("profile_canvas"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_rects = models.CharField(verbose_name=_("profile_rects"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_font = models.TextField(verbose_name=_("profile_font"), blank=True, null=True, default='')
    profile_start_url = models.CharField(verbose_name=_("profile_start_url"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_audio = models.TextField(verbose_name=_("profile_audio"), blank=True, null=True, default='')
    profile_webgl = models.TextField(verbose_name=_("profile_webgl"), blank=True, null=True, default='')
    profile_time_zone = models.PositiveSmallIntegerField(choices=FingerStatus.ChoiceList(), default=FingerStatus.follow,
                                            db_index=True)
    profile_webrtc = models.PositiveSmallIntegerField(choices=FingerStatus.ChoiceList(), default=FingerStatus.follow,
                                            db_index=True)
    profile_geo = models.PositiveSmallIntegerField(choices=FingerStatus.ChoiceList(), default=FingerStatus.follow,
                                            db_index=True)
    profile_vendor = models.CharField(verbose_name=_("vendor"),blank=True, null=True, max_length=255, db_index=True, default='')
    profile_renderer = models.CharField(verbose_name=_("renderer"), blank=True, null=True, max_length=255, db_index=True, default='')
    profile_note = models.TextField(verbose_name=_("note"), blank=True, null=True, default='')
    
    profile_status = models.PositiveSmallIntegerField(choices=ProfilesStatus.ChoiceList(), default=ProfilesStatus.normal,
                                                db_index=True)
    
    profile_used = models.PositiveSmallIntegerField(default=0, db_index=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            self.modified_by = user
            if self._state.adding:
                self.created_by = user

        # Sync profile_vendor and profile_renderer into profile_webgl JSON string if present
        if self.profile_vendor or self.profile_renderer:
            import json
            webgl_data = {}
            if self.profile_webgl and self.profile_webgl.strip() and self.profile_webgl != 'Noise':
                try:
                    webgl_data = json.loads(self.profile_webgl)
                except Exception:
                    pass
            if not isinstance(webgl_data, dict):
                webgl_data = {}
            
            modified = False
            if self.profile_vendor and webgl_data.get("37445") != self.profile_vendor:
                webgl_data["37445"] = self.profile_vendor
                modified = True
            if self.profile_renderer and webgl_data.get("37446") != self.profile_renderer:
                webgl_data["37446"] = self.profile_renderer
                modified = True
            
            if modified and webgl_data:
                self.profile_webgl = json.dumps(webgl_data, ensure_ascii=False)

        super(BrowserProfiles, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.profile_name

    def __str__(self):
        return self.profile_name    
   
class AccountsData(models.Model):
    class Meta:
        verbose_name = _("AccountsData")
        verbose_name_plural = _("AccountsData")
        # abstract = True
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="accounts_data_customer_set", null=True,
                                 blank=True, on_delete=models.PROTECT)

    type = models.ForeignKey(AccountsType, verbose_name=_("type"),
                             related_name="accounts_data_type_set", null=True,
                             blank=True, on_delete=models.PROTECT)

    owner = models.ForeignKey(User, verbose_name=_("owner"), related_name="accounts_data_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    
    note = models.TextField(verbose_name=_("note"), blank=True, null=True)
    
    first_name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    last_name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    address1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    address2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    city = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    state = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    zipcode = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    dob = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    ssn = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    signup_ip = models.TextField(verbose_name=_("signup_ip"), blank=True, null=True)

    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)
    used = models.PositiveSmallIntegerField(default=0, db_index=True)
    
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            self.modified_by = user
            if self._state.adding:
                self.created_by = user

        super(AccountsData, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.fisrt_name

    def __str__(self):
        return self.fisrt_name  
    
class AccountsEmails(models.Model):
    class Meta:
        verbose_name = _("AccountsEmails")
        verbose_name_plural = _("AccountsEmails")
        # abstract = True
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="accounts_emails_customer_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    accounts_data = models.ForeignKey(AccountsData, verbose_name=_("account_data"), related_name="account_data_emails_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    
    type = models.ForeignKey(AccountsType, verbose_name=_("type"),
                             related_name="accounts_emails_type_set", null=True,
                             blank=True, on_delete=models.PROTECT)
    
    owner = models.ForeignKey(User, verbose_name=_("owner"), related_name="accounts_emails_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)
    
    email = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    password = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    proxy = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    socks5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    state_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    state = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    phone_number = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    phone_service = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    signup_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)
    
    used = models.PositiveSmallIntegerField(default=0, db_index=True)
    
    refresh_token = models.TextField(blank=True, null=True)
    client_id = models.CharField(blank=True, null=True, max_length=255)
    
    latest_from = models.CharField(blank=True, null=True, max_length=255)
    latest_time = models.CharField(blank=True, null=True, max_length=255)
    latest_content = models.TextField(blank=True, null=True)
    latest_code = models.CharField(blank=True, null=True, max_length=255)
    
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            self.modified_by = user
            if self._state.adding:
                self.created_by = user

        # Auto-link to existing AccountsCreated if this email already exists there
        has_matching_acc = False
        matching_acc = None
        if self.email:
            email_clean = self.email.strip()
            from django.db.models import Q
            from telegram_bot.models import AccountsCreated
            acc_qs = AccountsCreated.objects.filter(Q(email__iexact=email_clean) | Q(username__iexact=email_clean))
            matching_acc = acc_qs.first()
            if matching_acc:
                self.used = 1
                has_matching_acc = True

        super(AccountsEmails, self).save(*args, **kwargs)

        if has_matching_acc and matching_acc and matching_acc.accounts_emails_id != self.pk:
            update_kwargs = {'accounts_emails': self}
            if not matching_acc.email:
                update_kwargs['email'] = self.email
            AccountsCreated.objects.filter(pk=matching_acc.pk).update(**update_kwargs)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email  
     
class AccountsCreated(models.Model):
    class Meta:
        verbose_name = _("AccountsCreated")
        verbose_name_plural = _("AccountsCreated")
        # abstract = True
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="accounts_created_customer_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    
    accounts_data = models.ForeignKey(AccountsData, verbose_name=_("account_data"), related_name="account_data_created_set", null=True,
                                 blank=True, on_delete=models.PROTECT)    

    type = models.ForeignKey(AccountsType, verbose_name=_("type"),
                             related_name="accounts_created_type_set", null=True,
                             blank=True, on_delete=models.PROTECT)

    browser_profiles = models.ForeignKey(BrowserProfiles, verbose_name=_("browser_profiles"), related_name="browser_profiles_set", null=True,
                                 blank=True, on_delete=models.PROTECT)


    owner = models.ForeignKey(User, verbose_name=_("owner"), related_name="accounts_created_owner_set", null=True,
                                 blank=True, on_delete=models.PROTECT)
    
    accounts_emails = models.ForeignKey(AccountsEmails, verbose_name=_("accounts_emails"), related_name="accounts_emails_set", null=True,
                                blank=True, on_delete=models.PROTECT)

    note = models.TextField(verbose_name=_("note"), blank=True, null=True)
    
    email = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    username = models.CharField(
        blank=True, null=True, max_length=255, db_index=True)
    
    password = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    proxy = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    socks5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    proxy_username = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    proxy_password = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    state_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    state = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    phone_number = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    phone_service = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    
    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)

    signup_ip = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    status = models.PositiveSmallIntegerField(choices=AccountStatus.ChoiceList(), default=AccountStatus.normal,
                                                   db_index=True)
    viewed = models.PositiveSmallIntegerField(default=0, db_index=True)
    two_factor_auth = models.CharField(verbose_name=_("two_factor_auth"), blank=True, null=True, max_length=255, default='', db_index=True)
    cookies = models.TextField(verbose_name=_("cookies"), blank=True, null=True, default='')
    subscription = models.CharField(verbose_name=_("subscription"), blank=True, null=True, max_length=255, default='', db_index=True)
    subscription_owner = models.CharField(verbose_name=_("subscription_owner"), blank=True, null=True, max_length=255, default='', db_index=True)
    
    auto_view = models.BooleanField(verbose_name=_(
        "auto_view"), default=False, db_index=True)
    
    auto_viewed = models.DateTimeField(verbose_name=_("auto_viewed"), auto_now=True, db_index=True, blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        # Auto-link to AccountsEmails if username or email is an email address
        email_candidate = None
        if self.username and '@' in self.username:
            email_candidate = self.username.strip()
            if not self.email:
                self.email = email_candidate
        elif self.email and '@' in self.email:
            email_candidate = self.email.strip()
            if not self.username:
                self.username = email_candidate
                
        if email_candidate:
            # Look up email in AccountsEmails case-insensitively
            email_qs = AccountsEmails.objects.filter(email__iexact=email_candidate)
            email_obj = None
            if self.owner:
                email_obj = email_qs.filter(owner=self.owner).first()
            if not email_obj:
                email_obj = email_qs.first()
                
            if email_obj:
                self.accounts_emails = email_obj
                # Mark email as used without triggering recursive save()
                if email_obj.used != 1:
                    AccountsEmails.objects.filter(pk=email_obj.pk).update(used=1)

        user = get_current_user()
        if user:
            self.modified_by = user
            if self._state.adding:
                self.created_by = user

        super(AccountsCreated, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email  
    

class AgentCommand(models.Model):
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    user = models.ForeignKey(User, related_name='agent_commands', on_delete=models.CASCADE)
    hwid = models.CharField(verbose_name=_("hwid"), max_length=255, db_index=True)
    command_type = models.CharField(verbose_name=_("command_type"), max_length=50) # 'open_profile', 'close_profile'
    profile_id = models.IntegerField(verbose_name=_("profile_id"))
    profile_data = models.TextField(verbose_name=_("profile_data"), blank=True, null=True, default='') # JSON encoded profile details
    status = models.CharField(verbose_name=_("status"), max_length=20, default='pending', db_index=True) # 'pending', 'sent', 'success', 'failed'
    
    def __str__(self):
        return f"{self.command_type} for Profile {self.profile_id} ({self.status})"
    
