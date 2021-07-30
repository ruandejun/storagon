#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  urls.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import  include, url
from django.views.generic import RedirectView, TemplateView
from .views import *
urlpatterns = [
	url(r'^verifyCode/?$', verifyCode, name='verifyCode'),
]
