from audit_log.models.fields import CreatingUserField, LastUserField
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime


CALCULATE_DATE = datetime.datetime.now().replace(month=8, day=1, hour=00, minute=00)




class TranslateKey(models.Model):
    class Meta:
        verbose_name = _("TranslateKey")
        verbose_name_plural = _("TranslateKey")

    version = IntegerVersionField()
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_("modified"), auto_now=True)
    created_by = CreatingUserField(verbose_name=_("created by"), related_name="created_%(app_label)s_%(class)s_set")
    modified_by = LastUserField(verbose_name=_("modified by"), related_name="modified_%(app_label)s_%(class)s_set")
    key = models.CharField(verbose_name=_("key"), max_length=255, primary_key=True, unique=True)
    zh_value = models.CharField(verbose_name=_("zh_value"), max_length=255)

    def __str__(self):
        return self.key

