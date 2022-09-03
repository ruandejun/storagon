#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Tool.py
#  
#
#  Created by TVA on 4/21/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError, Http404
from django.conf import settings  # site setting
from django.core.cache import cache
from django import shortcuts
# add logging
import logging, json, os, urllib, urllib3, sys
from django.core.exceptions import PermissionDenied as Http403
from django.core.exceptions import SuspiciousOperation as Http400
from django.core.files.storage import FileSystemStorage
import tempfile
from django.urls.resolvers import NoReverseMatch
from django.urls import reverse

from rest_framework import serializers,exceptions,status,permissions
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..tasks import runCMD
from celery.exceptions import TimeoutError
from rest_framework_mongoengine.serializers import DocumentSerializer
from urllib.parse import urlencode, quote_plus

#/var/log/system.log
logFilePath = getattr(settings, 'LOG_FILE_PATH', 'logging_local.log')

logging.basicConfig(filename=logFilePath,
					filemode='a',
					format='%(asctime)s,%(msecs)d | %(name)s | %(levelname)s | %(filename)s->%(funcName)s: %(message)s',
					datefmt='%Y-%m-%d %H:%M:%S',
					level=logging.DEBUG)


__all__ = ['logging','cache','shortcuts','Http403','Http400','Http404','custom_400',
			'checkRecaptcha', 'reverseBase', 'BadRequest', 'ServerError',
			'get_media_storage','get_temp_storage','banIPUsingCeleryWorkerCMD','DisableCSRF','ipsh',
			'getObjectOrNone','getObjectOr404','getParamsOr400','getParamsOrRaise400','errorResponse','successResponse',
			'successResponseRestful','errorResponseRestful']


class CustomModelSerializer(serializers.ModelSerializer):

	def _include_additional_options(self, *args, **kwargs):
		return self.get_extra_kwargs()

	def _get_default_field_names(self, *args, **kwargs):
		return self.get_field_names(*args, **kwargs)


class CustomDocumentSerializer(CustomModelSerializer, DocumentSerializer):
	pass


class LargeResultsSetPagination(PageNumberPagination):
	page_size = 100
	page_size_query_param = 'page_size'
	max_page_size = 1000


class StandardResultsSetPagination(PageNumberPagination):
	page_size = 10
	page_size_query_param = 'page_size'
	max_page_size = 100


class BadRequest(exceptions.APIException):
	status_code = 400
	default_detail = 'Bad Request'


class ServerError(exceptions.APIException):
	status_code = 500
	default_detail = 'Server Error'


def reverseBase(request,view_name,absolute=False,urlconf=None,args=None,kwargs=None,prefix=None,current_app=None):
	if not request.resolver_match.namespace: namespace=''
	else: namespace=request.resolver_match.namespace+':'
	url = reverse(namespace+view_name,urlconf,args,kwargs,current_app);
	if absolute:
		url = request.build_absolute_uri(url)
	return url;


def custom_400(request,exception):
	type, value, traceback = sys.exc_info();

	return errorResponse(value.message, code=400);
# def custom_400(request,exception):
# 	type, value, traceback = sys.exc_info();
# 	# respose = errorResponse(value.message, code=400)
# 	context = {
# 		'status': '400', 'reason': value.message
# 	}
# 	response = HttpResponse(json.dumps(context), content_type='application/json')
# 	response.staus_code = 400
# 	return response;

def checkRecaptcha(request):
	data = {
		'response': getParamsOr400(request, 'g-recaptcha-response'),
		'remoteip': request.META['REMOTE_ADDR'],
		'secret': settings.RECAPTCHA_SECRET
	}
	request = urllib3.HTTPConnectionPool('https://www.google.com/recaptcha/api/siteverify', data=urlencode(data))
	try:
		response = urllib3.HTTPConnectionPool(request)
		response_body = response.read()
		status = response.getcode()
	except urllib3.exceptions.HTTPError as e:
		response_body = e
		status = 400
		logging.error(u"Unable to connect to google to verify captcha, error:" % response_body)
		return None

	result = json.loads(response_body)
	if result['success'] is False:
		logging.error(u"Unable verify captcha with error-codes:%s" % (result['error-codes']))

	return result['success']


def get_media_storage():
	return FileSystemStorage(location=settings.MEDIA_ROOT);


def get_temp_storage():
	return FileSystemStorage(location=tempfile.gettempdir(), file_permissions_mode=0o600);


def banIPUsingCeleryWorkerCMD(remote_addr,key_failure=None):
	if remote_addr and remote_addr not in settings.SCOPED_RATE_THROTTLE_BAN_IP_WHITE_LIST:
		cmd = settings.SCOPED_RATE_THROTTLE_BAN_IP_CMD.format(remote_addr)
		if key_failure is None: key_failure=remote_addr;
		if cache.get(key_failure+'_ban', None) is None:
			taskResult = runCMD.delay(cmd);
			cache.set(key_failure+'_ban','executing',30);#wait 30s to ban ip effectively
			try:
				taskResult.wait(timeout=10);
			except TimeoutError:
				logging.warning(u"Try to ban IP=%s due to tolerance failure check!"%(remote_addr))
			else:
				if 'success' in taskResult.result or 'ALREADY_ENABLED' in taskResult.result:
					logging.warning(u"All request from IP=%s got banned due to tolerance failure check!"%(remote_addr))
					unbanCMD = settings.SCOPED_RATE_THROTTLE_UNBAN_IP_CMD.format(remote_addr)
					runCMD.apply_async(args=[unbanCMD], countdown=settings.SCOPED_RATE_THROTTLE_BAN_IP_DURATION);
				else:
					logging.error(u"Unable to ban IP=%s with result=%s using cmd=%s"%(remote_addr,taskResult.result, cmd))


class ScopedRateThrottleBanIP(ScopedRateThrottle):

	def get_cache_key(self, request, view):
		"""
		If `view.throttle_scope` is not set, don't apply this throttle.

		Otherwise generate the unique cache key by concatenating the user id
		with the '.throttle_scope` property of the view.
		"""
		if request.user.is_authenticated:
			ident = request.user.id
		else:
			ident = self.get_ident(request)

		self.request=request;

		return self.cache_format % {
			'scope': self.scope,
			'ident': ident
		}

	def throttle_failure(self):
		"""
		Called when a request to the API has failed due to throttling.
		"""
		self.key_failure = self.key+'_failure';
		self.history_failure = self.cache.get(self.key_failure, [])
		self.now = self.timer()

		num_requests, duration = self.parse_rate(settings.SCOPED_RATE_THROTTLE_BAN_IP_TOLERANCE_RATES)

		# Drop any requests from the history which have now passed the
		# throttle duration
		while self.history_failure and self.history_failure[-1] <= self.now - duration:
			self.history_failure.pop()

		if len(self.history_failure) >= num_requests:
			#ban ip using firewall-cmd
			remote_addr = self.request.META.get('REMOTE_ADDR')
			if remote_addr: banIPUsingCeleryWorkerCMD(remote_addr,self.key_failure);
		else:
			self.history_failure.insert(0, self.now)
			self.cache.set(self.key_failure, self.history_failure, duration)

		return False

from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from django.conf.urls import include, url


class FullRouter(DefaultRouter):
	"""
	The default router extends the SimpleRouter, but also adds in a default
	API root view, and adds format suffix patterns to the URLs.
	"""
	include_root_view=True
	include_format_suffixes=True
	root_view_name='api-root'

	def __init__(self,root_view_name='api-root'):
		super(self.__class__,self).__init__();
		self.includeRouterList = []
		self.root_view_name=root_view_name

	def get_api_root_view(self,api_urls=None):
		"""
		Return a view to use as the API root.
		"""
		api_root_dict={}
		list_name=self.routes[0].name
		for prefix,viewset,basename in self.registry:
			api_root_dict[prefix]=basename,viewset #list_name.format(basename=basename)
		routerSelf=self;
		class_name = self.root_view_name.replace('-','_').capitalize()

		class APIRoot(APIView):
			_ignore_model_permissions=True

			def get(self,request,*args,**kwargs):
				ret=[]
				for r in routerSelf.includeRouterList:
					try:
						ret+=[{
							'name':r.root_view_name,
							'url':reverseBase(request,r.root_view_name,absolute=True),
						}]
					except NoReverseMatch:continue;

				for prefix in api_root_dict:
					basename, viewset = api_root_dict[prefix]
					# print(routerSelf.get_routes(viewset))
					for url, mapping, name, detail, initkwargs in routerSelf.get_routes(viewset):
						correctName=name.format(basename=basename);

						reverseKwagrs={};

						# suffix = initkwargs.get('suffix');
						# if suffix==u'List':
						# 	pass;
						# elif suffix==u'Instance':
						# 	reverseKwagrs = {'pk':1}

						if 'lookup' in url:
							reverseKwagrs = {'pk':1}

						try:
							ret+=[{
								'name': correctName,
								'methods':mapping,
								'url' : reverseBase(request,correctName,absolute=True,kwargs=reverseKwagrs),
								# 'url': request.build_absolute_uri(request.get_full_path()+url[1:-1].format(prefix=prefix,lookup='1',trailing_slash='/')),
								# 'initKwagrs': str(initkwargs),

							}];
						except NoReverseMatch:continue;

				return Response(ret)
		APIRoot.__name__ = self.root_view_name;
		return APIRoot.as_view()

	def get_urls(self):
		urlpatterns = super(self.__class__,self).get_urls();
		for r in self.includeRouterList:
			urlpatterns.append( url('^'+r.root_view_name+'/', include(r.urls) ) );

		return urlpatterns;

	def include(self,r):
		""" Include another router to this route

		:param r: an instance of DefaultRouter
		:return:
		"""
		self.includeRouterList.append(r);


class DisableCSRF(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		setattr(request, '_dont_enforce_csrf_checks', True)
		response = self.get_response(request)
		return response


# Wrap it in a function that gives me more context:
def ipsh():
	# First import the embed function
	from IPython.terminal.embed import InteractiveShellEmbed
	import inspect
	ipshell = InteractiveShellEmbed()  # config=cfg, banner1=banner_msg, exit_msg=exit_msg
	frame = inspect.currentframe().f_back
	msg = 'Stopped at {0.f_code.co_filename} at line {0.f_lineno}'.format(frame)
	# Go back one level!
	# This is needed because the call to ipshell is inside the function ipsh()
	ipshell(msg, stack_depth=2)


def getObjectOrNone(ModelObject, *args, **kwargs):
	cacheTime = 60
	if len(args) >= 1:
		cacheTime = int(args[0])
	cacheKey = ModelObject.__name__ + '?' + '&'.join(['%s=%s' % (k, v) for k, v in kwargs.items()])

	# try to get from cache first
	object = cache.get(cacheKey, None)
	if object is None:  # cache miss
		try:
			object = ModelObject.objects.get(**kwargs)
		except ModelObject.DoesNotExist:
			return None
		except ModelObject.MultipleObjectsReturned:
			if len(args) >= 2:
				return None
			object = ModelObject.objects.filter(**kwargs).first()
		# set cache
		# print "setCache:"+cacheKey
		if cacheTime > 0:
			cache.set(cacheKey, object, cacheTime)
			object._cacheKey=cacheKey;
		else:
			object._cacheKey=None;

	return object


def getObjectOr404(ModelObject, *args, **kwargs):
	try:
		object = ModelObject.objects.get(**kwargs)
	except ModelObject.DoesNotExist:
		raise Http404()
	return object


def getParamsOr400(request, *paramNameAndDefaultValueList):
	if request.method == 'GET':
		return getParamsOrRaise400(request.GET, *paramNameAndDefaultValueList)
	else:
		return getParamsOrRaise400(request.POST, *paramNameAndDefaultValueList)

def getParamsOr400Restful(request, *paramNameAndDefaultValueList):
	if request.method in permissions.SAFE_METHODS:
		return getParamsOrRaise400(request.query_params, *paramNameAndDefaultValueList, raise400Restful=True)
	else:
		return getParamsOrRaise400(request.data, *paramNameAndDefaultValueList, raise400Restful=True)

def getParamsOrRaise400(paramDict, *paramNameAndDefaultValueList, **kwargs):
	""" Get a list of param from request.GET, request.POST  if not found, raise 400 if not provide defaul value

	paramDict=request.GET/request.POST
	paramNameAndDefaultValueList= [('param1','default1'),'param2',('param3',3)]
	paramNameAndDefaultValueList= [('param1','int'),('param2',list),('param3',[])]
	"""
	if kwargs.get('raise400Restful',False):
		BadRequestException=BadRequest
	else:
		BadRequestException=Http400

	resultSet = []
	if isinstance(paramNameAndDefaultValueList, str):
		paramNameAndDefaultValueList = [paramNameAndDefaultValueList]
	for pd in paramNameAndDefaultValueList:
		if isinstance(pd, str):  # no default value, only one string
			paramName = pd
			if paramName not in paramDict:  # raise 400 here
				print(u"Invalid Param:%s" % (paramName))
				raise BadRequestException(paramName)
			else:
				resultSet += [paramDict.get(paramName)]
		else:  # there is default value or formated function
			paramName, defaultValue = pd
			formatedFunction = None
			if defaultValue == list:
				defaultValue = None
				formatedFunction = list
			elif defaultValue == int:
				defaultValue = None
				formatedFunction = int
			elif isinstance(defaultValue, list):
				formatedFunction = list
			elif isinstance(defaultValue, int):
				formatedFunction = int
			elif isinstance(defaultValue, float):
				formatedFunction = float

			if paramName not in paramDict:
				if defaultValue is not None:
					resultSet += [defaultValue]
				else:
					# print u"Invalid Param:%s" % (paramName)
					raise BadRequestException(paramName)  # raise 400 here
			else:  # exists param in paramDict
				if formatedFunction == list:  # getlist
					resultSet += [paramDict.getlist(paramName)]
				elif formatedFunction is None:  # non format param
					resultSet += [paramDict.get(paramName)]
				else:  # formated param
					value = paramDict.get(paramName);
					if formatedFunction == int or float: #get number
						if value == '': value=0;#auto correct
					try:
						resultSet += [formatedFunction(value)]
					except Exception as e:  # invalid format
						# print u"Invalid Param:%s" % (e)
						raise BadRequestException(str(e))

	if len(resultSet) == 1:
		return resultSet[0]
	return tuple(resultSet)


def errorResponse(error, code=0, response=None):
	if response:
		HttpResponseServerError(json.dumps({"error": error, 'code': code, "response": str(response)}))
	return HttpResponseServerError(json.dumps({"error": error, 'code': code}))


def successResponse(data=None, encode=True):
	status = {'success': True, 'msg': 'success'}
	if data is not None:
		if encode:
			status.update(dict(data))
			print('status=====',status)
			return HttpResponse(json.dumps(status), content_type='application/json')
		else:
			return HttpResponse(data)

	return HttpResponse(json.dumps(status), content_type='application/json')


def successResponseRestful(data=None):
	if data is not None:
		return Response(data);
	else:
		return Response({"success":True});


def errorResponseRestful(error, code=None):
	if code is not None:
		return Response({"success":False, "error":error},status=code);
	else:
		return Response({"success":False, "error":error},status=406); #HTTP_406_NOT_ACCEPTABLE