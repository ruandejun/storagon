from django.db import models
from audit_log.models.fields import CreatingUserField, LastUserField
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from storagon.enum import *
import decimal
MONEY_MAX_DIGITS = getattr(settings, 'MONEY_MAX_DIGITS', 24)
MONEY_DECIMAL_PLACES = getattr(settings, 'MONEY_DECIMAL_PLACES', 2)
XRATE_MAX_DIGITS = getattr(settings, 'XRATE_MAX_DIGITS', 15)
XRATE_DECIMAL_PLACES = getattr(settings, 'XRATE_DECIMAL_PLACES', 0)
# Create your models here.

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

class AccountsSelling(models.Model):
	class Meta:
		verbose_name = _("AccountsSelling")
		verbose_name_plural = _("AccountsSelling")
	created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True, db_index=True)
	modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True, db_index=True)
	created_by = CreatingUserField(verbose_name=_("created by"), limit_choices_to={'is_staff': True},
								   related_name="created_%(app_label)s_%(class)s_set", on_delete=models.PROTECT, null=True)
	modified_by = LastUserField(verbose_name=_("modified by"), limit_choices_to={'is_staff': True},
								related_name="modified_%(app_label)s_%(class)s_set", on_delete=models.PROTECT, null=True)

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

	status = models.ForeignKey(Status, verbose_name=_("status"),
							   on_delete=models.PROTECT, null=True, blank=True)



	def __unicode__(self):
		return self.details

	def __str__(self):
		return self.type