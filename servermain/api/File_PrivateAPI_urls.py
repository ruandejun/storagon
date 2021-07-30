#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  File_PrivateAPI_urls.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from .File_PrivateAPI import *
urlpatterns = [
	url(r'^addFile/', addFile, name='addFile'),
	url(r'^addDuplicateFile/', addDuplicateFile, name='addDuplicateFile'),
	url(r'^moveFile/', moveFile, name='moveFile'),
	url(r'^deleteFile/', deleteFile, name='deleteFile'),
]
