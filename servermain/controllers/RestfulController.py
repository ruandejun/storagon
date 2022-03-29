#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  RestfulController
#  
#
#  Created by TVA on 4/15/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import urllib, hashlib
from django.conf import settings;

from system_configure.controllers.Tool import *
from storagon.enum import *
from rest_framework import serializers, generics, mixins, permissions, exceptions


class ServerError(exceptions.APIException):
	status_code = 500
	default_detail = 'Server Error'


class IsSignatureVerified(permissions.BasePermission):
	""" Signature Required Decoreator equivalent of Permission

	"""
	def has_permission(self, request, view):
		if settings.DEBUG:return True;#for testing.
		signature = request.META.get('HTTP_SIGNATURE_AUTHORIZATION')
		if not signature:
			# print request.META;
			# raise ServerError(u"Signature is required:%s"%(request.META));
			return False

		if request.method in ['GET','HEAD','DELETE','OPTIONS']:
			params = request.get_full_path()
			prefix='http://'
			if request.is_secure(): prefix='https://'
			params2 = prefix + request.get_host() + request.get_full_path(); #request.build_absolute_uri(params)

		elif request.method in ['POST','PATCH','PUT']:
			params2 = request.body  # case 2
			dataItems = sorted(request.data.items())
			# dataItems.sort()
			#convert unicode to fix urlencode error
			# try:params = urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in dataItems]);
			# except:params = urllib.urlencode(dataItems)  # case 1
			params = urllib.parse.urlencode(dataItems)  # case 1
		else:
			return False;#This Never Happend

		correct_signature = hashlib.md5(str(settings.SECRET_KEY + params).encode('utf-8')).hexdigest()
		if correct_signature != signature:
			# print params,'\n',params2
			correct_signature2 = hashlib.md5(str(settings.SECRET_KEY + params2).encode('utf-8')).hexdigest()
			if correct_signature2 != signature:
				msgError = u"correct_signature=%s or %s, but signature=%s" % (correct_signature, correct_signature2, signature);
				logging.debug(msgError)
				# raise ServerError(msgError);
				return False
		return True


class IsOwnerOrReadOnly(permissions.BasePermission):
	""" Custom permission to only allow owners of an object to edit it.
	"""
	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any request,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		# Write permissions are only allowed to the owner of the snippet.
		if request.method in ['PUT', 'PATCH', 'POST', 'DELETE']:
			if hasattr(obj, 'user'):
				return obj.user == request.user

		return False;


class IsOwnerOrNotAllow(permissions.BasePermission):
	"""
	Custom permission to only allow owners of an object to retrieve and edit it.
	"""
	def has_object_permission(self, request, view, obj):
		if hasattr(obj, 'user'):
			return obj.user == request.user
		return False;


class IsAffiliateProfile(permissions.BasePermission):
	"""
	Custom permission
	"""
	def has_permission(self, request, view):
		if request.user.profile.account_type == AccountType.affiliate or request.user.profile.account_type == AccountType.affiliatePPD:
			return True;
		return False;


class IsActiveProfile(permissions.BasePermission):
	"""
	Custom permission
	"""
	def has_permission(self, request, view):
		if request.user.is_active and request.user.profile.status in [AccountStatus.normal]:
			return True;
		return False;
