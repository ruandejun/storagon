import re
import os
import urllib.parse as urlparse

from django import shortcuts
from django.http import *
from django.conf import settings
from servermain.controllers import UserController
from .models import UserFile
from storagon.tool import *
from system_configure.controllers import SystemConfigureController

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework import serializers, generics, mixins, permissions, exceptions
from django.views.decorators.cache import cache_page

class DownloadView(generics.GenericAPIView):

	throttle_scope = 'heavy_api'

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