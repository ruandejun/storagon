#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  models.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.db import models
from django.contrib.auth.models import User


# Config
class SystemConfig(models.Model):
	key = models.CharField(max_length=255, primary_key=True, unique=True)
	value = models.TextField(blank=True)
	description = models.CharField(blank=True, max_length=511, default='')

	def __unicode__(self):
		if not self.description: return self.pk;
		return '%s (%s)'%(self.pk, self.description)


class TemplateHTML(models.Model):
	key = models.CharField(max_length=255, primary_key=True, unique=True)
	body = models.TextField(blank=True)
	description = models.CharField(blank=True, max_length=511, default='')


	def __unicode__(self):
		if not self.description: return self.pk;
		return '%s (%s)'%(self.pk, self.description)
