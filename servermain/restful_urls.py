#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  restful_urls
#  
#
#  Created by TVA on 5/18/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from .api import User_RestfulAPI_urls, File_RestfulAPI_urls, Statistics_RestfulAPI_urls, Session_RestfulAPI_urls, Card_RestfulAPI_urls

from system_configure.controllers.Tool import FullRouter

restfullRouter = FullRouter();
restfullRouter.include(User_RestfulAPI_urls.router);
restfullRouter.include(File_RestfulAPI_urls.router);
restfullRouter.include(Statistics_RestfulAPI_urls.router);
restfullRouter.include(Session_RestfulAPI_urls.router);
restfullRouter.include(Card_RestfulAPI_urls.router);

urlpatterns = restfullRouter.urls