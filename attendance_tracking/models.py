#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  models
#  
#
#  Created by TVA on 3/17/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AttendanceLog(models.Model):
	user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	created_date = models.DateTimeField(auto_now_add=True, db_index=True)
	modified_date = models.DateTimeField(auto_now=True, db_index=True)

	device_id = models.CharField(max_length=255, db_index=True)
	ip_address = models.CharField(max_length=255, db_index=True)

	note = models.TextField(blank=True)

	def __unicode__(self): return "%s : %s" % (self.user, timezone.template_localtime(self.created_date).strftime('%Y-%m-%d    %H:%M')) #self.created_date.strftime('%Y-%m-%d    %H:%M'))

	class Meta:
		default_permissions = (
			("submit_attendancelog", "Can submit attendancelog"),
			("view_attendancelog", "Can view attendancelog"),
		)