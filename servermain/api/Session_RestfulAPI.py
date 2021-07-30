#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Session_RestfulAPI.py
#  
#
#  Created by TVA on 6/11/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse

from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from mongoengine import Q

from storagon.enum import *
from servermain.models import UserFile
from servermain.mongo_models import Session
from system_configure.controllers import Tool
from munch import Munch
from rest_framework import serializers, mixins, permissions, exceptions, filters, status, generics, viewsets
from rest_framework.decorators import detail_route,list_route
from servermain.controllers import RestfulController

from rest_framework_mongoengine import generics as mongo_generics
from rest_framework_mongoengine import viewsets as mongo_viewsets



class SessionSerializer(Tool.CustomDocumentSerializer):
	class Meta:
		model = Session
		fields = ('id', 'type', 'status', 'created', 'uid', 'fid', 'sid', 'oid', 'data', 'text')


class SessionFilterForm(serializers.Serializer):
	type = serializers.IntegerField(min_value=0,default=SessionType.download);
	status = serializers.IntegerField(min_value=-1,default=-1);
	fid = serializers.IntegerField(min_value=0,default=0);
	oid = serializers.IntegerField(min_value=0,default=0);
	from_date = serializers.DateField(format=None);
	to_date = serializers.DateField(format=None, default=None);
	text = serializers.CharField(default='');


class CreateReportForm(serializers.Serializer):
	text = serializers.CharField();
	fid = serializers.IntegerField(min_value=0,default=0);
	sid = serializers.IntegerField(min_value=0,default=0);
	detail = serializers.CharField();


class SessionClientAPI(mongo_viewsets.MongoGenericViewSet, mongo_generics.ListAPIView):
	""" GET \n\n
	type = serializers.IntegerField(min_value=0,default=SessionType.download);
	status = serializers.IntegerField(min_value=-1,default=-1);
	fid = serializers.IntegerField(min_value=0,default=0);
	oid = serializers.IntegerField(min_value=0,default=0);
	from_date = serializers.DateField(format=None);
	to_date = serializers.DateField(format=None, default=timezone.datetime.today());
	text = serializers.CharField(required=False,default='');
	"""
	# permission_classes = [permissions.IsAuthenticated, RestfulController.IsSignatureVerified]
	serializer_class = SessionSerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
	# filter_class = SesssionFilter
	# filter_fields = ('type', 'status', 'created', 'uid', 'fid', 'sid', 'oid')
	# search_fields = ('text', )
	ordering_fields = ('created', )
	pagination_class = Tool.StandardResultsSetPagination

	def get_queryset(self): #getter for queryset, overide queryset
		form=SessionFilterForm(data=self.request.QUERY_PARAMS);
		if not form.is_valid():
			raise Tool.BadRequest(form.errors);
		#::type: SessionFilterForm
		data=Munch(form.data)

		if data.type not in [SessionType.upload, SessionType.download, SessionType.report, SessionType.inbox]:
			raise Tool.ServerError(u"SessionType=%s is not allowed" % (data.type))

		#convert date to datetime
		from_date = timezone.datetime.combine(data.from_date, timezone.datetime.min.timetz())

		query = Session.objects.all()
		query = query.filter(type=data.type).filter(created__gt=from_date)

		if data.status >= 0:
			query = query.filter(status=data.status)

		if data.to_date:
			to_date = timezone.datetime.combine(data.to_date, timezone.datetime.max.timetz())
			query = query.filter(created__lt=to_date)

		if data.fid == 0 and data.oid == 0 and data.text=='deviceId':
			# if self.request.user.is_staff:
			query = query.filter(text='deviceId');
			return query;
			# else:
			# 	raise Tool.ServerError(u"This kind of query is not allowed");

		if data.fid > 0:
			userFile = Tool.getObjectOrNone(UserFile, id=data.fid);
			if not userFile:
				raise Tool.ServerError(u"UserFile with id=%s is not exist" % (data.fid))
			if userFile.user != self.request.user:
				raise Tool.ServerError(u"UserFile with id=%s is not belong to you" % (data.fid))
			query = query.filter(fid=data.fid)
		elif data.oid >0:
			if data.oid != self.request.user.id:
				raise Tool.ServerError(u"You can't get DownloadSession file of other user")
			query = query.filter(oid=data.oid)
		else:
			if data.type == SessionType.report or data.type == SessionType.inbox:
				query = query.filter(Q(uid=self.request.user.id) | Q(sid=self.request.user.id))
			else:
				query = query.filter(uid=self.request.user.id)

		return query
		# return Session.objects.all();


class SessionClientAPIView(viewsets.GenericViewSet):

	@list_route(methods=['post'], serializer_class=CreateReportForm, permission_classes=[])
	def createReport(self, request, *args, **kwargs):
		formPOST=CreateReportForm(data=request.data);
		if not formPOST.is_valid():
			return Tool.errorResponseRestful(formPOST.errors,code=status.HTTP_400_BAD_REQUEST);
		#::type: CreateReportForm
		data=Munch(formPOST.data)

		user_id=0;
		if request.user:
			user_id=request.user.id;

		report = Session(uid=user_id, type=SessionType.report)
		report.text = data.text
		if data.sid > 0:
			report.sid = data.sid  # user_id
		if data.fid > 0:
			report.fid = data.fid
			# notify uploadFile user of DMCA report
			try:
				uploadFile = UserFile.objects.get(id=data.fid)
			except UserFile.DoesNotExist:
				return Tool.errorResponseRestful(u"Reported file doesn't exists!")
			else:
				report.sid = uploadFile.user.id
				report.data['file_link'] = uploadFile.get_absolute_url(withFileKey=False);

		if request.user:
			report.data['reporter_username'] = request.user.username

		report.data['ip_address'] = request.META['REMOTE_ADDR']
		try: response = settings.geo_reader.country(report.data['ip_address']);
		except: report.data['iso_code']='Unknow';
		else: report.data['iso_code']=response.country.iso_code

		report.data['detail'] = data.detail

		if report.text=='deviceId' and report.data['iso_code']!='US':
			return Tool.successResponseRestful();#do not save non US deviceId

		report.save()

		return Tool.successResponseRestful();