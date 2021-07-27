#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Statistics_RestfulAPI_urls.py
#  
#
#  Created by TVA on 6/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#
from Statistics_RestfulAPI import AffiliateStatisticsAPI
from system_configure.controllers.Tool import FullRouter

router = FullRouter('statistics');
router.register(r'aff', AffiliateStatisticsAPI, base_name='Aff')

urlpatterns = router.urls