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
	url(r'^get_inject_info/', get_inject_info, name='get_inject_info'),
	url(r'^update_profile_by_id/', update_profile_by_id, name='update_profile_by_id'),
	url(r'^remove_profiles/', remove_profiles, name='remove_profiles'),
	url(r'^remove_accounts/', remove_accounts, name='remove_accounts'),
	url(r'^get_browser_profiles/', get_browser_profiles, name='get_browser_profiles'),
	url(r'^get_accounts_emails/', get_accounts_emails, name='get_accounts_emails'),
	url(r'^get_accounts_created/', get_accounts_created, name='get_accounts_created'),
	url(r'^get_accounts_data/', get_accounts_data, name='get_accounts_data'),
	url(r'^add_accounts_created/', add_accounts_created, name='add_accounts_created'),
	url(r'^set_auto_views/', set_auto_views, name='set_auto_views'),
]