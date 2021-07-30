#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  File_ClientAPI_urls.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from .File_ClientAPI import *

urlpatterns = [
	#url(r'^home/$', TemplateView.as_view(template_name='example/home.html'), name="home"),
	#url(r'^/?$', RedirectView.as_view(pattern_name="home")),

	url(r'^moveFile/', moveFile, name='moveFile'),
	url(r'^deleteFile/', deleteFile, name='deleteFile'),
	url(r'^newFolder/', newFolder, name='newFolder'),
	url(r'^moveFolder/', moveFolder, name='moveFolder'),
	url(r'^deleteFolder/', deleteFolder, name='deleteFolder'),
	url(r'^listFileAndFolder/', listFileAndFolder, name='listFileAndFolder'),
	url(r'^editFolder/', editFolder, name='editFolder'),
	url(r'^editFile/', editFile, name='editFile'),
	url(r'^getLink/', getLink, name='getLink'),
]
