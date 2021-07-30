#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  urls
#  
#
#  Created by TVA on 3/17/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import url
from .views import *
urlpatterns = [
	#url(r'^home/$', TemplateView.as_view(template_name='example/home.html'), name="home"),
	#url(r'^/?$', RedirectView.as_view(pattern_name="home")),

	url(r'^submitAttendance/$', submitAttendance, name='AT_submitAttendance'),
	url(r'^checkAttendance/$', checkAttendance, name='AT_checkAttendance'),
]