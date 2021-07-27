#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  urls.py
#  
#
#  Created by TVA on 5/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout, logout_then_login

urlpatterns = patterns('private_tracker',
	url(r'^announce$', 'views.announce', name='PT_announce'),
	url(r'^scrape$', 'views.scrape', name='PT_scrape'),
)
