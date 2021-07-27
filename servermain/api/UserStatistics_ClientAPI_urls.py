#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  UserStatistics_ClientAPI_urls.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('servermain.api.UserStatistics_ClientAPI',
	#url(r'^home/$', TemplateView.as_view(template_name='example/home.html'), name="home"),
	#url(r'^/?$', RedirectView.as_view(pattern_name="home")),

	url(r'^getUserStorage/', 'getUserStorage', name='getUserStorage'),
	url(r'^listBill/', 'listBill', name='listBill'),
	url(r'^listTransaction/', 'listTransaction', name='listTransaction'),
	url(r'^getPlanAndPaygateInfo/', 'getPlanAndPaygateInfo', name='getPlanAndPaygateInfo'),
	url(r'^getExchangePointRateInfo/', 'getExchangePointRateInfo', name='getExchangePointRateInfo'),
	url(r'^exchangePoint/', 'exchangePoint', name='exchangePoint'),
	url(r'^downloadCountSessionStatistic/', 'downloadCountSessionStatistic', name='downloadCountSessionStatistic'),
	url(r'^newUserOriginFromDownloadLinkStatistic/', 'newUserOriginFromDownloadLinkStatistic', name='newUserOriginFromDownloadLinkStatistic'),
)
