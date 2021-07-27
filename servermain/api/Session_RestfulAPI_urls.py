#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Session_RestfulAPI_urls.py
#  
#
#  Created by TVA on 6/11/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from Session_RestfulAPI import SessionClientAPI, SessionClientAPIView
from system_configure.controllers.Tool import FullRouter

router = FullRouter('mongo');
router.register(r'session', SessionClientAPI, base_name='session')
router.register(r'sessionView', SessionClientAPIView, base_name='sessionView')

urlpatterns = router.urls