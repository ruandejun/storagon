#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  CustomAdmin_urls
#
#
#  Created by TVA on 12/16/14.
#  Copyright (c) 2014 storagon. All rights reserved.
#

from django.conf.urls import  url
from django.views.generic import RedirectView, TemplateView
from .CustomAdmin_views import *
urlpatterns = [
	#url(r'^home/$', TemplateView.as_view(template_name='example/home.html'), name="home"),
	#url(r'^/?$', RedirectView.as_view(pattern_name="home")),

	url(r'^customAdminTest/$', customAdminTest, name='custom_site_example'),

	# session CRUD
	url(r'^session/$', mongoListSessionView, name='mongoListSessionView'),
	url(r'^session/(\w+)/$', mongoEditSessionView, name='mongoEditSessionView'),
	url(r'^session/(\w+)/delete/$', mongoDeleteSessionView, name='mongoDeleteSessionView'),

	# tool
	url(r'^userFileUpload/$', userFileUpload, name='userFileUpload'),
	url(r'^sendServerFileSignal/$', sendServerFileSignal, name='sendServerFileSignal'),
	url(r'^verifyBillManual/$', verifyBillManual, name='verifyBillManual'),

	url(r'^showUserStatistic/$', showUserStatistic, name='showUserStatistic'),
	url(r'^showSessionStatistic/$', showSessionStatistic, name='showSessionStatistic'),
]
