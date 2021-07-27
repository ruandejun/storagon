#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Premium_ClientAPI_urls
#  
#
#  Created by TVA on 3/12/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('servermain.api.Premium_ClientAPI',
	#url(r'^home/$', TemplateView.as_view(template_name='example/home.html'), name="home"),
	#url(r'^/?$', RedirectView.as_view(pattern_name="home")),

	url(r'^getListPremiumKey/', 'getListPremiumKey', name='getListPremiumKey'),
	url(r'^buyPremiumKey/', 'buyPremiumKeyUsingCredit', name='buyPremiumKeyUsingCredit'),
	url(r'^exchangePremiumKey/', 'exchangePremiumKey', name='exchangePremiumKey'),
)
