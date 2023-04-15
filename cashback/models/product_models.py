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
# from auditlog.models import CreatingUserField, LastUserField
# from audit_log.models.fields import CreatingUserField, LastUserField

from mptt.models import MPTTModel, TreeForeignKey



class TypeCategory(models.Model):
    class Meta:
        verbose_name = _("TypeCategory")
        verbose_name_plural = _("TypeCategory")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)

    def __str__(self):
        return str(self.label)

class CategoryTranslate(models.Model):
    class Meta:
        verbose_name = _("CategoryTranslate")
        verbose_name_plural = _("CategoryTranslate")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    typecategory = models.ForeignKey("TypeCategory", verbose_name=_("type"), on_delete=models.PROTECT)
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)
    label_vn = models.CharField(verbose_name=_("label_vn"), max_length=512, null=True,blank=True)


    def __str__(self):
        return str(self.label)

class ProductTranslate(models.Model):
    class Meta:
        verbose_name = _("ProductTranslate")
        verbose_name_plural = _("ProductTranslate")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)
    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=512)
    label_vn = models.CharField(verbose_name=_("label_vn"), max_length=512,null=True,blank=True)
    url = models.CharField(verbose_name=_("url"), max_length=512)
    image_url = models.CharField(verbose_name=_("image_url"), max_length=2048)
    categorytranslate = models.ManyToManyField("CategoryTranslate", verbose_name=_("categorytranslate"))

    def __str__(self):
        return str(self.label)

class Category(MPTTModel):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Category")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    code = models.CharField(verbose_name=_("code"), unique=True, max_length=255)
    label = models.CharField(verbose_name=_("label"), db_index=True, max_length=255)
    metadata = models.TextField(verbose_name=_("metadata"), blank=True)

    order_index = models.PositiveIntegerField(verbose_name=_("order_index"), null=True, default=0,
                                              db_index=True)  # TODO: remove null=True

    class MPTTMeta:
        order_insertion_by = ['order_index']

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return str("%s" % (self.label if self.label else self.code))


class ProductOption(models.Model):
    class Meta:
        verbose_name = _("ProductOption")
        verbose_name_plural = _("ProductOption")

        unique_together = ('value', 'name')

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    name = models.CharField(verbose_name=_("name"), max_length=255)
    value = models.CharField(verbose_name=_("value"), max_length=255)
    label = models.CharField(verbose_name=_("label"), db_index=True, blank=True, max_length=255)
    translated = models.CharField(verbose_name=_("translated"), db_index=True, blank=True, max_length=255)

    def __str__(self):
        return str('%s: %s' % (self.label if self.label else self.name,
                               self.translated if self.translated else self.value))


class Product(models.Model):
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Product")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    is_hidden = models.BooleanField(verbose_name=_("is_hidden"), default=False)
    slug = models.SlugField(verbose_name=_("slug"), max_length=255, unique=True, db_index=True)
    categories = models.ManyToManyField("Category", verbose_name=_("categories"), blank=True)

    shopping_domain = models.CharField(verbose_name=_("shopping_domain"), blank=True, max_length=255, db_index=True)
    vendor = models.ForeignKey("Vendor", verbose_name=_("vendor"), null=True, blank=True, on_delete=models.PROTECT)
    detail_url = models.CharField(verbose_name=_("detail_url"), max_length=2048)
    name = models.CharField(verbose_name=_("name"), max_length=512, db_index=True)
    sku = models.CharField(verbose_name=_("sku"), blank=True, max_length=255, unique=True, db_index=True)
    image_url = models.CharField(verbose_name=_("image_url"), max_length=2048, blank=True)
    short_description = models.TextField(verbose_name=_("short_description"), blank=True)
    html_cache_path = models.CharField(verbose_name=_("html_cache_path"), max_length=2048, blank=True, null=True)
    currency = models.ForeignKey("Currency", verbose_name=_("currency"), on_delete=models.PROTECT)
    price = models.DecimalField(verbose_name=_("price"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)], db_index=True)
    shipping = models.DecimalField(verbose_name=_("shipping"), default=decimal.Decimal(0), max_digits=MONEY_MAX_DIGITS,
                                   decimal_places=MONEY_DECIMAL_PLACES, validators=[MinValueValidator(0)],
                                   db_index=True)
    weight = models.DecimalField(verbose_name=_("weight"), default=decimal.Decimal(0), max_digits=9, decimal_places=2);
    inventory_quantity = models.PositiveIntegerField(verbose_name=_("inventory_quantity"), default=0);
    options_selected = models.ManyToManyField("ProductOption", verbose_name=_("options_selected"), blank=True)
    options_metadata = models.TextField(verbose_name=_("options_metadata"), blank=True)

    def __str__(self):
        return str("%s: %s" % (self.shopping_domain, self.name))

    def image_tag(self):
        return '<img src="%s" style="width:64px;height:64px;" />' % self.image_url

    image_tag.allow_tags = True
    image_tag.short_description = _("Image")


class ReferUrl(models.Model):
    class Meta:
        verbose_name = _("ReferUrl")
        verbose_name_plural = _("ReferUrl")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)

    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created', on_delete=models.PROTECT)
    
    modified_by = models.ForeignKey(User, null=True, editable=True, related_name='%(class)s_modified', on_delete=models.PROTECT)

    customer = models.CharField(verbose_name=_("customer"), blank=True, null=True, max_length=255, db_index=True)

    telegram_id = models.CharField(verbose_name=_("telegram_id"), blank=True, null=True, max_length=255, db_index=True)

    zalo_id = models.CharField(verbose_name=_("zalo_id"), blank=True, null=True, max_length=255, db_index=True)

    wechat_id = models.CharField(verbose_name=_("wechat_id"), blank=True, null=True, max_length=255, db_index=True)

    order_item = models.ForeignKey('OrderItem', verbose_name=_("order_item"), null=True, blank=True)

    shopping_domain = models.CharField(verbose_name=_("shopping_domain"), blank=True, max_length=255, db_index=True)

    commission_rate = models.DecimalField(verbose_name=_("commission_rate"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    coupon_amount = models.DecimalField(verbose_name=_("coupon_amount"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    coupon_start_fee = models.DecimalField(verbose_name=_("coupon_start_fee"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)
    real_post_fee = models.DecimalField(verbose_name=_("real_post_fee"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    reserve_price = models.DecimalField(verbose_name=_("reserve_price"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    tk_total_commi = models.DecimalField(verbose_name=_("tk_total_commi"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    tk_total_sales = models.DecimalField(verbose_name=_("tk_total_sales"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    zk_final_price = models.DecimalField(verbose_name=_("zk_final_price"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    commission_price = models.DecimalField(verbose_name=_("commission_price"), default=decimal.Decimal(0),
                                         max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
                                         validators=[MinValueValidator(0)], db_index=True)

    coupon_end_time = models.DateTimeField(verbose_name=_("coupon_end_time"), null=True, blank=True)

    coupon_start_time = models.DateTimeField(verbose_name=_("coupon_start_time"), null=True, blank=True)

    coupon_id = models.CharField(verbose_name=_("coupon_id"), blank=True, null=True, max_length=512)

    coupon_info = models.CharField(verbose_name=_("coupon_info"), blank=True, null=True, max_length=512)

    coupon_remain_count = models.PositiveIntegerField(verbose_name=_("coupon_remain_count"), null=True, blank=True,
                                                   default=0, db_index=True)
    coupon_total_count = models.PositiveIntegerField(verbose_name=_("coupon_total_count"), null=True, blank=True,
                                                   default=0, db_index=True)
    volume = models.PositiveIntegerField(verbose_name=_("volume"), null=True, blank=True,
                                                   default=0, db_index=True)

    coupon_share_url = models.CharField(verbose_name=_("coupon_share_url"), blank=True, null=True, max_length=2048)

    item_description = models.CharField(verbose_name=_("item_description"), blank=True, null=True, max_length=2048)
    item_id = models.CharField(verbose_name=_("item_id"), blank=True, null=True, max_length=512)
    item_url = models.CharField(verbose_name=_("item_url"), blank=True, null=True, max_length=2048)
    nick = models.CharField(verbose_name=_("nick"), blank=True, null=True, max_length=512)
    pict_url = models.CharField(verbose_name=_("pict_url"), blank=True, null=True, max_length=2048)
    seller_id = models.CharField(verbose_name=_("seller_id"), blank=True, null=True, max_length=512)
    shop_title = models.CharField(verbose_name=_("shop_title"), blank=True, null=True, max_length=512)
    short_title = models.CharField(verbose_name=_("short_title"), blank=True, null=True, max_length=512)
    title = models.CharField(verbose_name=_("title"), blank=True, null=True, max_length=512)
    url = models.CharField(verbose_name=_("url"), blank=True, null=True, max_length=2048)
    x_id = models.CharField(verbose_name=_("x_id"), blank=True, null=True, max_length=512)
    taokouling = models.CharField(verbose_name=_("taokouling"), blank=True, null=True, max_length=2048)
    short_url = models.CharField(verbose_name=_("short_url"), blank=True, null=True, max_length=2048)
    note = models.TextField(verbose_name=_("note"), blank=True, null=True, max_length=2048)

    @property
    def share_link(self):
        if self.coupon_share_url:
            return self.coupon_share_url
        else:
            return self.url


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/user_{0}/{1}'.format(instance.user.id, filename)

def user_image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/user_{0}/{1}'.format(instance.user.id, filename)

class Document(models.Model):
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Document")
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    document = models.FileField(upload_to='upload_documents/%Y/%m/%d/')

class ImagesDocument(models.Model):
    class Meta:
        verbose_name = _("ImagesDocument")
        verbose_name_plural = _("ImagesDocument")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    description = models.CharField(verbose_name=_("description"),max_length=255, blank=True, null=True)
    name = models.CharField(verbose_name=_("name"),max_length=255, blank=True, null=True)
    upload_images = models.ImageField(upload_to='upload_images/%Y/%m/%d/')


class CartItem(models.Model):
    class Meta:
        verbose_name = _("CartItem")
        verbose_name_plural = _("CartItem")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

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