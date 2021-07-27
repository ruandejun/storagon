#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  main_views.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import re
import os
import urlparse

from django import shortcuts
from django.http import *

from servermain.controllers import UserController
from models import UserFile
from storagon.tool import *
from system_configure.controllers import SystemConfigureController

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework import serializers, generics, mixins, permissions, exceptions
from django.views.decorators.cache import cache_page


class HomeView(generics.GenericAPIView):

	throttle_scope = 'static_page'	

	def get(self, request, *args, **kwargs):
		mainURL = 'junshare_main/index.html'
		# print "Home View";
		response = shortcuts.render(request, mainURL, {
		})

		return response;


class DownloadView(generics.GenericAPIView):

	throttle_scope = 'heavy_api'

	def render_download_page(self, request, userFile):
		# print(request.COOKIES)
		# response = shortcuts.render(request,"junshare_main/dl.html",{
		response = shortcuts.render(request, "junshare_main/download.html", {
			'file_name': userFile.file_name,
			'file_size': userFile.realFile.file_size,
			'file_id': userFile.id,
			'file': userFile
		})

		downloadCookieMaxAge = SystemConfigureController.getConfigure('downloadCookieMaxAge', 24 * 60 * 60)  # in seconds
		response.set_cookie('agency_id', value=str(userFile.user_id), max_age=downloadCookieMaxAge)
		response.set_cookie('userfile_id', value=str(userFile.id), max_age=downloadCookieMaxAge)

		refererURL = request.META.get('HTTP_REFERER')
		if refererURL and re.search(r'127\.0\.0\.1|localhost|storagon.com', refererURL) == None:
			# print u"Referer=%s" % (refererURL)
			parseData = urlparse.urlparse(refererURL)
			response.set_cookie('website_origin', value=parseData.hostname, max_age=downloadCookieMaxAge)
			response.set_cookie('website_url', value=refererURL, max_age=downloadCookieMaxAge)

		return response

	def get(self, request, *args, **kwargs):
		# print "Download View";
		file_id, file_name = args

		try:
			file_id = int(file_id)
		except Exception as e:
			return HttpResponseBadRequest('file_id')

		try:
			userFile = UserFile.objects.get(id=file_id)
		except:
			raise Http404
		if userFile.file_name != file_name.strip():
			raise Http404

		return self.render_download_page(request,userFile)


class DownloadView2(DownloadView):

	def get(self, request, *args, **kwargs):
		file_id, string_id = args
		logging.debug("file_id=%s,string_id=%s"%(file_id,string_id))
		try:
			file_id = int(file_id)
		except Exception as e:
			return HttpResponseBadRequest('file_id')

		try:
			userFile = UserFile.objects.get(id=file_id)
		except:
			raise Http404

		if userFile.string_id != string_id:
			raise Http404

		return self.render_download_page(request,userFile)


class DownloadToolView(generics.GenericAPIView):

	throttle_scope = 'static_page'

	def get(self, request, *args, **kwargs):
		# print "Home View";
		response = shortcuts.render(request, "junshare_main/download_tool.html", {
		})

		return response;

class AffiliateToolView(generics.GenericAPIView):

	throttle_scope = 'static_page'

	def get(self, request, *args, **kwargs):
		# print "Home View";
		response = shortcuts.render(request, "junshare_main/affiliate_tool.html", {
		})

		return response;

class PaymentSuccessView(generics.GenericAPIView):

	throttle_scope = 'static_page'

	def get(self, request, *args, **kwargs):
		# print "Home View";
		response = shortcuts.render(request, "junshare_main/payment_success.html", {
		})

		return response;

class PaymentFailView(generics.GenericAPIView):

	throttle_scope = 'static_page'

	def get(self, request, *args, **kwargs):
		# print "Home View";
		response = shortcuts.render(request, "junshare_main/payment_fail.html", {
		})

		return response;


def activateAccount(request):
	if request.method == 'GET':
		activation_code = request.GET.get('activation_code');
		if not activation_code: raise Http404();
		result = UserController.verifyAccountActivation(activation_code);
		if result:
			return shortcuts.redirect('/#/account');
		else:
			return errorResponse(u"Invalid activation_code or activation_code expired");
	else:
		raise Http404()