from audit_log.models.fields import CreatingUserField, LastUserField
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime


CALCULATE_DATE = datetime.datetime.now().replace(month=8, day=1, hour=00, minute=00)

class CommentTicketBox(models.Model):
    class Meta:
        verbose_name = _("CommentTicketBox")
        verbose_name_plural = _("CommentTicketBox")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")

    body = models.TextField(blank=True)

    ticket_box = models.ForeignKey("TicketBox", verbose_name=_("TicketBox"), on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.body
    @property
    def created_tag(self):
        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created
    @property
    def created_by_tag(self):
        if self.created_by:
            return self.created_by.username
        else:
            return None
class TicketBoxGroup(models.Model):
    class Meta:
        verbose_name = _("TiketBoxType")
        verbose_name_plural = _("TiketBoxType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)

class TicketBoxType(models.Model):
    class Meta:
        verbose_name = _("TiketBoxType")
        verbose_name_plural = _("TiketBoxType")

    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    value = models.CharField(verbose_name=_("value"), max_length=255, primary_key=True, unique=True)
    label = models.CharField(verbose_name=_("label"), max_length=255)
    default = models.BooleanField(verbose_name=_("default"), default=False, db_index=True)

    def __str__(self):
        return str(self.label)


class TicketBox(models.Model):
    class Meta:
        verbose_name = _("TicketBox")
        verbose_name_plural = _("TicketBox")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    customer = models.ForeignKey(User, verbose_name=_("customer"), related_name="ticketbox_customer_set", on_delete=models.PROTECT)

    type = models.ForeignKey("TicketBoxType", verbose_name=_("TiketBoxType"), on_delete=models.PROTECT, null=True)

    group_care = models.ForeignKey("TicketBoxGroup", verbose_name=_("TicketBoxGroup"), on_delete=models.PROTECT, null=True)

    order = models.ForeignKey("Order", verbose_name=_("order"),blank=True, null=True)

    shipment_package = models.ForeignKey("ShipmentPackage", verbose_name=_("ShipmentPackage"),blank=True, null=True)

    order_item = models.ForeignKey("OrderItem", verbose_name=_("OrderItem"),blank=True, null=True)

    title = models.CharField(blank=True, max_length=511, default='')

    body = models.TextField(blank=True)

    status = models.ForeignKey("Status", verbose_name=_("status"), on_delete=models.PROTECT, null=True, blank=True)

    note = models.TextField(verbose_name=_("note"), blank=True)

    takecare_by = models.ForeignKey(User, verbose_name=_("takecare_by"), related_name="ticketbox_takecare_by_set", on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    takecare =  models.DateTimeField(verbose_name=_("takecare Date"), null=True, blank=True)

    closed = models.DateTimeField(verbose_name=_("closed Date"), null=True, blank=True)

    deadline = models.DateTimeField(verbose_name=_("deadline Date"), null=True, blank=True)

    closed_by = models.ForeignKey(User, verbose_name=_("closed_by"), related_name="closed_by_set", on_delete=models.PROTECT, limit_choices_to={'is_staff': True}, null=True, blank=True)

    def __str__(self):
        return str("[%s] (%s)" % (self.title, str(self.status)))

    @property
    def created_tag(self):

        if self.created:
            return self.created.strftime("%d-%m-%Y %H:%M")
        else:
            return self.created
    @property
    def created_by_tag(self):
        if self.created_by:
            return self.created_by.username
        else:
            return None
    @property
    def customer_tag(self):
        if self.customer:
            return self.customer.username
        else:
            return None
    @property
    def type_tag(self):
        if self.type:
            return self.type.label
        else:
            return None
    @property
    def group_care_tag(self):
        if self.group_care:
            return self.group_care.label
        else:
            return None
    @property
    def status_tag(self):
        if self.status:
            return self.status.label
        else:
            return None
    @property
    def takecare_by_tag(self):
        if self.takecare_by:
            return self.takecare_by.label
        else:
            return None
    @property
    def takecare_tag(self):
        if self.created:
            return self.takecare.strftime("%d-%m-%Y %H:%M")
        else:
            return self.takecare
    @property
    def closed_tag(self):
        if self.closed:
            return self.closed.strftime("%d-%m-%Y %H:%M")
        else:
            return self.closed
    @property
    def deadline_tag(self):
        if self.deadline:
            return self.deadline.strftime("%d-%m-%Y %H:%M")
        else:
            return self.deadline
    @property
    def closed_by_tag(self):
        if self.deadline:
            return self.closed_by.username
        else:
            return None
    @property
    def full_name_tag(self):
        if self.customer:
            return self.customer.profile.full_name
        else:
            return None