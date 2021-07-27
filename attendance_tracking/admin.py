#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  admin
#  
#
#  Created by TVA on 3/17/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.contrib import admin

# Register your models here.
from models import AttendanceLog

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
	search_fields = ['user__username', 'note']
	list_display = ('__unicode__', 'ip_address', 'device_id', 'created_date', 'modified_date')
	list_filter = ('created_date', 'device_id')
	# list_editable = ('note',)
	# readonly_fields = ('ip_address', 'device_id')

