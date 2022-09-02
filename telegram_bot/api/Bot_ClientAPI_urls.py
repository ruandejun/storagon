#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Bot_ClientAPI_urls.py


from django.conf.urls import url
from .Bot_clientAPI import *

urlpatterns = [
	url(r'^telegram_bot/', telegram_bot, name='telegram_bot'),
	url(r'^create_browser_profile/', create_browser_profile, name='create_browser_profile'),
	url(r'^get_browser_profile_by_id/', get_browser_profile_by_id, name='get_browser_profile_by_id'),
	url(r'^get_browser_profiles/', get_browser_profiles, name='get_browser_profiles'),
]