#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  User_RestfulAPI_urls
#  
#
#  Created by TVA on 4/2/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from servermain.api.User_RestfulAPI import CurrentUserProfileView,CurrentUserAccountBalanceView,CurrentUserWebsiteAgencyView,CurrentUserUserApplyList,CurrentUserUserApplyView,CurrentUserView

# urlpatterns = format_suffix_patterns([
#
# 	#url(r'^profile/(?P<pk>[0-9]+)/$', UserProfileDetail.as_view()),
#
# 	url(r'^profile/$', CurrentUserProfileView.as_view()),
#
# 	url(r'^accountBalance/$', CurrentUserAccountBalanceView.as_view()),
# 	url(r'^websiteAgency/$', CurrentUserWebsiteAgencyView.as_view()),
# 	url(r'^userApply/$', CurrentUserUserApplyView.as_view()),
#
# ])

from system_configure.controllers.Tool import FullRouter

router = FullRouter('user');
router.register(r'profile', CurrentUserProfileView, base_name='Profile')
router.register(r'accountBalance', CurrentUserAccountBalanceView, base_name='AccountBalance')
router.register(r'websiteAgency', CurrentUserWebsiteAgencyView, base_name='WebsiteAgency')
router.register(r'userApplyList', CurrentUserUserApplyList, base_name='UserApplyList')
router.register(r'userApplyView', CurrentUserUserApplyView, base_name='UserApplyView')
router.register(r'auth', CurrentUserView, base_name='UserView')

urlpatterns = router.urls


