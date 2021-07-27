#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Session_ClientAPI_urls.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('servermain.api.Session_ClientAPI',
	url(r'^createUploadSession/', 'createUploadSession', name='createUploadSession'),
	url(r'^createDownloadSession/', 'createDownloadSession', name='createDownloadSession'),
	url(r'^createReport/', 'createReport', name='createReport'),
	url(r'^sendInboxMessage/', 'sendInboxMessage', name='sendInboxMessage'),
	url(r'^getListSession/', 'getListSession', name='getListSession'),
)
