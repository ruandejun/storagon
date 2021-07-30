#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Session_PrivateAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

# from django import shortcuts
# from django.template import RequestContext
# from django.http import *
# from django.urls import reverse
#
# from django.conf import settings  # site setting
# from django.views.decorators.csrf import csrf_exempt, csrf_protect
# from django.contrib.auth.decorators import login_required
# from bson import json_util

from django.utils import timezone
from django.db.models import F
from servermain.models import UserFile, RealFile
from servermain.mongo_models import Session, ServerFileStorage
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import signature_test

from servermain.controllers import AffiliateController, ServerFileController


@signature_test()
def getSession(request):
	""" Get a session

	request.GET = {
		session_id : id of session
	}

	response = bson JSON [{
		type : Enum SessionType,
		uid : user id,
		fid : file_id UserFile and RealFile or folder_id
		sid : server_id
		status : Enum SessionStatus
		data : Dict contain session data
		created : DateTime
	}]

	"""
	if request.method == 'GET':
		session_id = getParamsOr400(request, 'session_id')

		session = getObjectOr404(Session, id=session_id)

		return successResponse(session.to_json(), encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@signature_test()
def doneSession(request):
	""" Change status of a session or multiple session at a time

	request.POST = {
		session_id : id of session
	or session_id_list : list id of session
		status : new status
		type : SessionType
	}

	response = JSON {
		'success' : number of success
		'updated' : number of session has update to match new status
	}

	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		sessionIDList, status, type = getParamsOr400(request, ('session_id', list), ('status', int), ('type', -1))

		try:
			query = Session.objects.all().filter(id__in=sessionIDList)
		except Exception as e:
			logging.error(u"Bulk update failed with error=%s" % (e))
			return errorResponse(u"Bulk update failed with error=%s" % (e))

		result = 0;
		# AffiliacateController PPD
		if type == SessionType.download and status == SessionStatus.completed:
			fid_list = [];
			for session in query:
				if session.status!=SessionStatus.completed:
					if session.data.get('download_type') in [DownloadType.browser,DownloadType.direct]:
						session.data['ppd_bonus']= AffiliateController.payPerDownloadBonus(session);
					fid_list += [session.fid];

				#update individual
				session.status = status;
				session.created = timezone.now();
				session.save();
				result+=1;

			#update download_count
			UserFile.objects.all().filter(id__in=fid_list).update(download_count=F('download_count')+1, last_download_date=timezone.now());

		#delete file on old server
		elif type == SessionType.move and status == SessionStatus.completed:
			for session in query:
				# check whether a session has been created to delete this realFile exist or not, if not create one
				try:
					deleteSession, created = Session.objects.get_or_create(
				type=SessionType.delete, fid=session.fid, sid=session.data['old_server_id'], text=session.data['file_location']		, defaults={
					'status': SessionStatus.waiting, 'type': SessionType.delete, 'fid': session.fid, 'sid': session.data['old_server_id'], 'text': session.data['file_location']})
				except Session.MultipleObjectsReturned:
					pass
				else:
					if created:
						logging.warning(u"realFile_id=%s has been mark as deleted already" % (session.fid))
						# automaticaly increase ServerFileStorage waiting_delete_session_count atomicaly
						ServerFileStorage.objects(pk=session.data['old_server_id']).update_one(inc__waiting_delete_session_count=1)

				#update individual
				session.status = status;
				session.save();
				result+=1;
		else:
			#update bulk
			result = query.update(set__status=status)

		if result==0:
			logging.info(u"Bulk update success with no result, sessionIDList=%s" % (sessionIDList))
		else:
			logging.info(u"Bulk update success with result=%s" % (result))
		return successResponse()
	else:
		raise Http404()


@signature_test()
def listSession(request):
	""" List session using filter param

	request.GET = {
		type : Enum SessionType, required
		status : Enum SessionStatus, required
		uid : user id,
		fid : file_id UserFile and RealFile or folder_id
		sid : server_id
		from_date : filter created DateTime
		to_date : filter created DateTime
		order_by : String to put in query.order_by(...);
	}

	response = bson JSON [{
		_id: {"$oid": "54881833df3a1a268573fb18"},
		type : Enum SessionType,
		uid : user id,
		fid : file_id UserFile and RealFile or folder_id
		sid : server_id
		status : Enum SessionStatus
		data : Dict contain session data
		created : DateTime
	}]

	"""
	if request.method == 'GET':

		type, status, uid, fid, sid, from_date, to_date, offset, limit, order_by = getParamsOr400(request,
		('type', int), ('status', int), ('uid', 0), ('fid', 0), ('sid', 0), ('from_date', ''), ('to_date', ''), ('offset', 0), ('limit', 0), ('order_by', '-created')
		)

		if from_date:
			from_date = timezone.datetime.strptime(from_date, "%Y-%m-%d_%H-%M-%S")
		if to_date:
			to_date = timezone.datetime.strptime(to_date, "%Y-%m-%d_%H-%M-%S")

		sessionListQuery = Session.objects.all().filter(type=type, status=status)
		if uid:
			sessionListQuery = sessionListQuery.filter(uid=uid)
		if fid:
			sessionListQuery = sessionListQuery.filter(fid=fid)

		if sid < 0: #auto get server id using request.META['REMOTEADDR']
			currentServerFile = ServerFileController.getCurrentConnectingServerFile(request);
			if not currentServerFile:
				return errorResponse(u"Unable to determine serverfile");
			else:
				sid=currentServerFile.id;

		if sid > 0:
			sessionListQuery = sessionListQuery.filter(sid=sid)

		if from_date:
			sessionListQuery = sessionListQuery.filter(created__gt=from_date)
		if to_date:
			sessionListQuery = sessionListQuery.filter(created__lt=to_date)

		sessionListQuery = sessionListQuery.order_by(order_by)
		sessionListQuery = sessionListQuery.skip(offset)
		if limit > 0:
			sessionListQuery = sessionListQuery.limit(limit)
		return successResponse(sessionListQuery.to_json(), encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()








