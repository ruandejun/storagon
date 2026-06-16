#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  TelegramBot_RestfulAPI



from storagon.enum import *
from rest_framework import serializers
import rest_framework_bulk as restbulk
from telegram_bot.models import AccountsCreated, AccountsData, AccountsEmails, AccountsSelling, BrowserProfiles, MunAnti, MunProxies, LinkCheckout, UserCheckFunction, UserCreateFunction, UserHwid, CheckerType, CreatorType, CheckerTask




class CheckerTaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = CheckerTask
		fields = ('id', 'created', 'modified', 'download_url','file_name','file_id', 'file_unique_id', 'note', 'status', 'checker_type', 'owner', 'status_message_id','details','display_page_valid','display_page_invalid', 'display_value'
		)
	checker_type = serializers.SlugRelatedField(slug_field='value', read_only=True)

	owner = serializers.SlugRelatedField(slug_field='username', read_only=True)

 
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
		fields = ('id', 'created', 'modified', 'created_by','profile_owner',
				'modified_by', 'profile_name', 'profile_os',
				'profile_browser', 'profile_version', 'profile_proxy_type',
				'profile_proxy_details', 'profile_socks5_details', 'profile_proxy_username',
				'profile_proxy_password','profile_path_cookies',
    			'profile_user_agent','profile_original_name',
       			'profile_resolution','profile_cpu', 'profile_canvas',
				'profile_rects', 'profile_font', 'profile_start_url',
				'profile_audio', 'profile_webgl', 'profile_time_zone',
				'profile_webrtc', 'profile_geo', 'profile_vendor',
				'profile_renderer', 'profile_note', 'profile_status',
          )
	profile_owner = serializers.SlugRelatedField(slug_field='username', read_only=True);
 
class MunAntiSerializer(serializers.ModelSerializer):
	class Meta:
		model = MunAnti
		fields = ('id', 'created', 'modified', 'update_url','version',
		)

class MunProxiesSerializer(serializers.ModelSerializer):
	class Meta:
		model = MunProxies
		fields = ('id', 'created', 'socks_port', 'control_port','bridges_string','rotating_time', 'country_code', 'country_name',
		) 
 
 
class AccountsDataSerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountsData
		fields = ('id', 'created', 'modified', 'created_by','customer',
				'modified_by', 'type', 'owner',
				'note', 'first_name', 'last_name',
				'address1', 'address2',
				'city','state',
    			'zipcode','dob',
       			'ssn','status', 'price',
				'used',
          )
	customer = serializers.SlugRelatedField(slug_field='username', read_only=True);
	owner = serializers.SlugRelatedField(slug_field='username', read_only=True);

class AccountsEmailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountsEmails
		fields = ('id', 'created', 'modified', 'created_by','customer',
				'modified_by', 'type', 'owner',
				'note', 'accounts_data', 'email',
				'password', 'proxy',
				'socks5','state',
    			'state_ip','phone_number',
       			'phone_service','status', 'price',
				'used', 'refresh_token', 'client_id',
          )
	customer = serializers.SlugRelatedField(slug_field='username', read_only=True);
	owner = serializers.SlugRelatedField(slug_field='username', read_only=True);
 
class AccountsCreatedSerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountsCreated
		fields = ('id', 'created', 'modified', 'created_by','customer','profile_os',
				'modified_by', 'type', 'owner',
				'note', 'accounts_data', 'email',
				'password', 'proxy',
				'socks5','state','proxy_username', 'proxy_password',
    			'state_ip','phone_number',
       			'phone_service','status', 'price','auto_view',
				'viewed', 'browser_profiles', 'accounts_emails', 'username', 'signup_ip',
				'two_factor_auth', 'cookies',
				'subscription', 'subscription_owner',
          )
	customer = serializers.SlugRelatedField(slug_field='username', read_only=True);
	owner = serializers.SlugRelatedField(slug_field='username', read_only=True);
	created_by = serializers.SlugRelatedField(slug_field='username', read_only=True);
	profile_os = serializers.SerializerMethodField()
 
	@staticmethod
	def get_profile_os(accounts_created):
		if accounts_created.browser_profiles:
			return accounts_created.browser_profiles.profile_os
		else:
			return ''
class LinkCheckoutSerializer(serializers.ModelSerializer):
	class Meta:
		model = LinkCheckout
		fields = ('id', 'created', 'modified', 'created_by','modified_by', 'url', 'status', 'note', 'type')
  
class UserCheckFunctionSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserCheckFunction
		fields = ('id', 'created', 'modified', 'value', 'status', 'note', 'label')
  
class UserCreateFunctionSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserCreateFunction
		fields = ('id', 'created', 'modified', 'value', 'status', 'note', 'label')  
  
class CheckerTypeFunctionSerializer(serializers.ModelSerializer):
	class Meta:
		model = CheckerType
		fields = ('created', 'modified', 'value', 'status', 'label')  
  
class CreatorTypeFunctionSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreatorType
		fields = ('created', 'modified', 'value', 'status', 'label')  

