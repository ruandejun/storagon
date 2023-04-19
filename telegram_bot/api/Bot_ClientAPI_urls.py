#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Bot_ClientAPI_urls.py


from django.conf.urls import url
from .Bot_clientAPI import *

urlpatterns = [
	url(r'^telegram_bot/', telegram_bot, name='telegram_bot'),
	url(r'^telegram_gpt_bot/', telegram_gpt_bot, name='telegram_gpt_bot'),
	url(r'^telegram_cashback_bot/', telegram_cashback_bot, name='telegram_cashback_bot'),
	url(r'^coinbase_bot/', coinbase_bot, name='coinbase_bot'),
	url(r'^create_browser_profile/', create_browser_profile, name='create_browser_profile'),
	url(r'^get_browser_profile_by_id/', get_browser_profile_by_id, name='get_browser_profile_by_id'),
	url(r'^get_profile_by_account_id/', get_profile_by_account_id, name='get_profile_by_account_id'),
	url(r'^get_inject_info/', get_inject_info, name='get_inject_info'),
	url(r'^update_profile_by_id/', update_profile_by_id, name='update_profile_by_id'),
	url(r'^update_account_by_id/', update_account_by_id, name='update_account_by_id'),
	url(r'^update_munproxies_by_id/', update_munproxies_by_id, name='update_munproxies_by_id'),
	url(r'^add_mun_proxies/', add_mun_proxies, name='add_mun_proxies'),
	url(r'^remove_mun_proxies/', remove_mun_proxies, name='remove_mun_proxies'),
	url(r'^remove_profiles/', remove_profiles, name='remove_profiles'),
	url(r'^remove_accounts/', remove_accounts, name='remove_accounts'),
	url(r'^remove_emails/', remove_emails, name='remove_emails'),
	url(r'^get_browser_profiles/', get_browser_profiles, name='get_browser_profiles'),
	url(r'^get_mun_proxies/', get_mun_proxies, name='get_mun_proxies'),
	url(r'^get_accounts_emails/', get_accounts_emails, name='get_accounts_emails'),
	url(r'^update_accounts_emails/', update_accounts_emails, name='update_accounts_emails'),
	url(r'^add_accounts_emails/', add_accounts_emails, name='add_accounts_emails'),
	url(r'^get_accounts_created/', get_accounts_created, name='get_accounts_created'),
	url(r'^get_accounts_data/', get_accounts_data, name='get_accounts_data'),
 	url(r'^update_accounts_data/', update_accounts_data, name='update_accounts_data'),
	url(r'^add_accounts_data/', add_accounts_data, name='add_accounts_data'),
	url(r'^add_accounts_created/', add_accounts_created, name='add_accounts_created'),
	url(r'^set_auto_views/', set_auto_views, name='set_auto_views'),
	url(r'^update_new_profiles/', update_new_profiles, name='update_new_profiles'),
	url(r'^accounts_update_new_profiles/', accounts_update_new_profiles, name='accounts_update_new_profiles'),
	url(r'^remove_auto_views/', remove_auto_views, name='remove_auto_views'),
	url(r'^get_profile_for_auto_views/',get_profile_for_auto_views, name='get_profile_for_auto_views'),
	url(r'^add_key_for_search/',add_key_for_search, name='add_key_for_search'),
	url(r'^get_key_for_search/',get_key_for_search, name='get_key_for_search'),
	url(r'^check_version_for_update/',check_version_for_update, name='check_version_for_update'),
	url(r'^get_link_checkout/', get_link_checkout, name='get_link_checkout'),
	url(r'^add_link_checkout/', add_link_checkout, name='add_link_checkout'),
	url(r'^update_link_checkout/', update_link_checkout, name='update_link_checkout'),
	url(r'^get_check_function/', get_check_function, name='get_check_function'),
	url(r'^get_create_function/', get_create_function, name='get_create_function'),
	url(r'^get_tool_setting/', get_tool_setting, name='get_tool_setting'),
	url(r'^get_checker_task/', get_checker_task, name='get_checker_task'),
	url(r'^get_checker_files/', get_checker_files, name='get_checker_files'),
	url(r'^update_checker_task/', update_checker_task, name='update_checker_task'),
	url(r'^add_checker_valid/', add_checker_valid, name='add_checker_valid'),
	url(r'^add_checker_invalid/', add_checker_invalid, name='add_checker_invalid'),
]