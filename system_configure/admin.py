#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  admin.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.contrib import admin
# Register your models here.
from models import SystemConfig, TemplateHTML
# Setting

from django.forms import ModelForm
from suit_redactor.widgets import RedactorWidget


class SystemConfigForm(ModelForm):

	class Meta:
		fields = ['key', 'description', 'value']
		# widgets = {
		# 	'value': RedactorWidget(editor_options={'lang': 'en'})
		# }


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
	search_fields = ['key', 'description']
	list_display = ('__unicode__',)

	form = SystemConfigForm


class TemplateHTMLForm(ModelForm):

	class Meta:
		fields = ['key', 'description', 'value']
		widgets = {
			'value': RedactorWidget(editor_options={'lang': 'en'})
		}


@admin.register(TemplateHTML)
class TemplateHTMLAdmin(admin.ModelAdmin):
	search_fields = ['key', 'description']
	list_display = ('__unicode__',)

	form = TemplateHTMLForm