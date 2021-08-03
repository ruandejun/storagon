#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  frontend_urls.py
#
#
#  Created by TVA on 12/27/14.
#  Copyright (c) 2014 storagon. All rights reserved.
#

from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView


urlpatterns = [

	# url(r'^/?$', TemplateView.as_view(template_name="storagon_main/index.html"), name='home'),
	# url(r'^/?$', 'main_views.home', name='home'),
	# url(r'^dl/(\d+)/(.+)$', 'main_views.download', name='download'),
]

from rest_framework.urlpatterns import format_suffix_patterns
from .junshare_views import HomeView, DownloadView, DownloadView2, DownloadToolView, AffiliateToolView, PaymentSuccessView, PaymentFailView, activateAccount
from django.views.decorators.cache import cache_page

urlpatterns += format_suffix_patterns([
	# url(r'^/?$', cache_page(600)(HomeView.as_view()), name='home'), #cache for 10 minutes

	url(r'^/?$', HomeView.as_view(), name='home'),
	url(r'^dl/(\d+)/(.+)$', DownloadView.as_view(), name='download'),
	url(r'^dl/(\d+)j(.+)$', DownloadView2.as_view(), name='download2'),
	url(r'^download-tool/$', DownloadToolView.as_view(), name='download-tool'),
	url(r'^affiliate-tool/$', AffiliateToolView.as_view(), name='affiliate-tool'),
	url(r'^payment-success/$', PaymentSuccessView.as_view(), name='payment-success'),
	url(r'^payment-fail/$', PaymentFailView.as_view(), name='payment-fail'),
	url(r'^activateAccount/$', activateAccount, name='activateAccount'),
]);