#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  TelegramBot_RestfulAPI



from storagon.enum import *
from rest_framework import serializers
import rest_framework_bulk as restbulk
from telegram_bot.models import AccountsSelling, BrowserProfiles

class AccountsSellingSerializer(serializers.ModelSerializer):
	class Meta:
		model=AccountsSelling

		fields=('id','created','created_by','modified','modified_by','warranty_date','warranty','customer','type','ordered','ordered_date','owner','details','note','price','selling_status')
		# read_only_fields=('id','user','created_date','modified_date')


	created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

	modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

	customer = serializers.SlugRelatedField(slug_field='username', read_only=True)

	owner = serializers.SlugRelatedField(slug_field='username', read_only=True)

class BrowserProfilesSerializer(serializers.ModelSerializer):
	class Meta:
		model = BrowserProfiles
		fields = ('id', 'created', 'modified', 'created_by','profile_owner'
				'modified_by', 'profile_name', 'profile_os',
				'profile_browser', 'profile_version', 'profile_proxy_type',
				'profile_proxy_details', 'profile_proxy_username',
				'profile_proxy_username','profile_path_cookies',
    			'profile_user_agent','profile_original_name',
       			'profile_resolution','profile_cpu', 'profile_canvas',
				'profile_rects', 'profile_font', 'profile_start_url',
				'profile_audio', 'profile_webgl', 'profile_time_zone',
				'profile_webrtc', 'profile_geo', 'profile_vendor',
				'profile_renderer', 'profile_note', 'profile_status'
          )

	profile_owner = serializers.SlugRelatedField(slug_field='username', read_only=True);