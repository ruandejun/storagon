#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Bot_ClientAPI_urls.py


from django.conf.urls import url
from .Bot_clientAPI import *

urlpatterns = [
	url(r'^telegram_bot/', telegram_bot, name='telegram_bot'),
	url(r'^create_browser_profile/', create_browser_profile, name='create_browser_profile'),
]