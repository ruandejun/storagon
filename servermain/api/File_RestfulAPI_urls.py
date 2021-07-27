#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  File_RestfulAPI_urls
#  
#
#  Created by TVA on 4/14/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView


from servermain.api.File_RestfulAPI import CurrentUserFileView,CurrentUserFolderView,FolderAPI

from rest_framework.urlpatterns import format_suffix_patterns
# urlpatterns = format_suffix_patterns([
#
# 	url(r'^userfile/$', CurrentUserFileView.as_view()),
# 	url(r'^folder/$', CurrentUserFolderView.as_view()),
# 	url(r'^backTrace/$', BackTraceFolder.as_view()),
# ])

from system_configure.controllers.Tool import FullRouter

router = FullRouter('file');
router.register(r'userfile', CurrentUserFileView, base_name='UserFile')
router.register(r'folder', CurrentUserFolderView, base_name='Folder')
router.register(r'folderAPI', FolderAPI, base_name='FolderAPI')

urlpatterns = router.urls