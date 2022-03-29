#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Session_PrivateAPI_urls.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from .Session_PrivateAPI import *
urlpatterns = [
	url(r'^getSession/', getSession, name='getSession'),
	url(r'^doneSession/', doneSession, name='doneSession'),
	url(r'^listSession/', listSession, name='listSession'),
]
