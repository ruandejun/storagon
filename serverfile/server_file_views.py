#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  server_file_views.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

# -*- coding: utf-8 -*-
import datetime,time
import os
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
import jwt

from django.http import *
from django.utils import timezone
from django.core.cache import cache
from django.urls import reverse

from storagon.PrivateAPI_SDK import SessionSDK, FileSDK
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import signature_test
from servermain.mongo_models import Session
from serverfile.tasks import recursive_mkdir, processMoveFileSessionList, processDeleteFileSessionList, processClearTemporaryFolder
from celery.exceptions import TimeoutError
from rest_framework.decorators import api_view
from private_tracker.controllers import TorrentController

@api_view(['GET','POST','PUT'])
def downloadTorrentView(request, downloadSessionID, token, fileName):
	""" Serve file download with data in downloadSesstionID via torrent downloader
		@param downloadSessionID , use to retrive info of current download in mainServer (or encrypt data in downloadSessionID)
		data must include: file_path , file_name, limit_rate
		@return
	"""
	if request.method == 'GET':

		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)

		# get from cache first
		session = cache.get(settings.CACHE_MONGO_SESSION_PREFIX + downloadSessionID, None)

		#get from jwt token
		if not session and token:
			try:
				decodedSessionData = jwt.decode(token, settings.SECRET_KEY);
			except jwt.DecodeError as e:
				logging.error(u"Failed to decode JWT token");
			else:
				session = Session.from_json(json.dumps(decodedSessionData));
				# logging.debug(u"Success decode JWT token");

		#get from server main
		if not session:
			session = sessionSDK.getSession(downloadSessionID)
			if not session:
				return errorResponse(u"Unable to retrive download session, cancel download!", code=0)
			else:  # set cache
				cache.set(settings.CACHE_MONGO_SESSION_PREFIX + downloadSessionID, session, settings.MONGO_SESSION_EXPIRES)

		if session.type != SessionType.download and session.status == SessionStatus.completed:
			return errorResponse(u"Upload has already completed!")

		if session.type != SessionType.download or session.status == SessionStatus.failed or timezone.now() > session.created + datetime.timedelta(seconds=settings.MONGO_SESSION_EXPIRES):
			return errorResponse(u"Invalid download session, cancel download!", code=0)

		# if session.data['ip_address'] in ['10.0.0.1','10.0.2.2','127.0.0.1'] or '192.168.1.' or '192.168.31.' in session.data['ip_address']:
		# 	logging.info(u"Allow session IP=%s to download without checking REMOTE_ADDR=%s"%(session.data['ip_address'] , request.META['REMOTE_ADDR']));
		# elif session.data['ip_address'] != request.META['REMOTE_ADDR']:
		# 	return errorResponse(u"Invalid user IP address=%s, cancel download!"%(request.META['REMOTE_ADDR']), code=0)

		file_name = session.data['file_name']
		file_location = session.data['file_location']
		file_size = session.data['file_size']
		speed_limit = session.data['speed_limit']
		connection_limit = session.data['connection_limit']

		torrent_file_name = session.data['file_name']+'.torrent';
		real_file_name = file_location.split('/')[-1];

		tracker_url = session.data['tracker_url'];
		sample_torrent_path = settings.MEDIA_ROOT+'/torrent/sample/%s.torrent'%(real_file_name);
		torrent_file_path = settings.MEDIA_ROOT+'/torrent/%s.torrent'%(downloadSessionID);
		web_seed_url = request.build_absolute_uri(reverse('downloadView',args=(downloadSessionID,token,'')))

		recursive_mkdir(settings.MEDIA_ROOT+'/torrent/sample/');

		skip_edit_torrent = False;
		skip_make_torrent = False;
		if os.path.isfile(torrent_file_path):
			skip_make_torrent = True;
			skip_edit_torrent = True;
			logging.debug(u"skip edit torrent")
		elif os.path.isfile(sample_torrent_path):
			skip_make_torrent = True;
			logging.debug(u"skip make torrent")

		download_file_path = '/media/torrent/%s.torrent'%(downloadSessionID);

		if not skip_make_torrent:
			skip_edit_torrent=True;
			result = TorrentController.makeTorrentFile(tracker_url, fileName ,sample_torrent_path, web_seed_url, settings.MEDIA_ROOT + '/' + file_location);
			if result!=0:
				return errorResponse(u"Unable to make torrent file.");
			download_file_path = '/media/torrent/sample/%s.torrent'%(real_file_name);
			torrent_file_path = sample_torrent_path;
		elif not skip_edit_torrent:
			try:
				TorrentController.editTorrentFile(sample_torrent_path,torrent_file_path,tracker_url,fileName,web_seed_url);
			except IOError as e:
				logging.error(u"Unable to edit torrent file. error=%s"%(e))
				return errorResponse(u"Unable to edit torrent file.");

		for ti in range(3):
			if os.path.isfile(torrent_file_path):break;
			time.sleep(3)
		else:
			os.remove(sample_torrent_path);#try remove the original torrent
			return errorResponse(u"Unable to generate torrent file.");

		# These lines let nginx handle download file
		logging.debug(u"download_file_path=%s"%download_file_path);
		response = HttpResponse()
		response["Content-Disposition"] = 'attachment; filename="%s"' % (torrent_file_name)
		response['X-Accel-Redirect'] = download_file_path
		return response;

@api_view(['GET','POST','PUT'])
def downloadView(request, downloadSessionID, token, fileName):
	""" Serve file download with data in downloadSesstionID
		@param downloadSessionID , use to retrive info of current download in mainServer (or encrypt data in downloadSessionID)
		data must include: file_path , file_name, limit_rate
		@return
	"""
	if request.method == 'GET':

		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)

		# get from cache first
		session = cache.get(settings.CACHE_MONGO_SESSION_PREFIX + downloadSessionID, None)

		#get from jwt token
		if not session and token:
			try:
				decodedSessionData = jwt.decode(token, settings.SECRET_KEY);
			except jwt.DecodeError as e:
				logging.error(u"Failed to decode JWT token");
			else:
				session = Session.from_json(json.dumps(decodedSessionData));
				# logging.debug(u"Success decode JWT token");

		#get from server main
		if not session:
			session = sessionSDK.getSession(downloadSessionID)
			if not session:
				return errorResponse(u"Unable to retrive download session, cancel download!", code=0)
			else:  # set cache
				cache.set(settings.CACHE_MONGO_SESSION_PREFIX + downloadSessionID, session, settings.MONGO_SESSION_EXPIRES)

		if session.type != SessionType.download and session.status == SessionStatus.completed:
			return errorResponse(u"Upload has already completed!")

		if session.type != SessionType.download or session.status == SessionStatus.failed or timezone.now() > session.created + datetime.timedelta(seconds=settings.MONGO_SESSION_EXPIRES):
			return errorResponse(u"Invalid download session, cancel download!", code=0)

		if session.data['ip_address'] in ['192.168.1.1', '192.168.31.1','10.0.0.1','10.0.2.2','127.0.0.1']:
			logging.info(u"Allow session IP=%s to download without checking REMOTE_ADDR=%s"%(session.data['ip_address'] , request.META['REMOTE_ADDR']));
		# elif session.data.get('tracker_url',None) is not None:
		# 	logging.info(u"Allow torrent session IP=%s to download without checking REMOTE_ADDR=%s"%(session.data['ip_address'] , request.META['REMOTE_ADDR']));
		# elif session.data['ip_address'] != request.META['REMOTE_ADDR']:
		# 	return errorResponse(u"Invalid user IP address=%s, cancel download!"%(request.META['REMOTE_ADDR']), code=0)
		print('==session.data==', session.data)
		if fileName:
			file_name = fileName;
		else:
			file_name = session.data['file_name']+'.storagon';

		file_location = session.data['file_location']
		file_size = session.data['file_size']
		speed_limit = session.data['speed_limit']
		connection_limit = session.data['connection_limit']

		interface = request.META.get('GATEWAY_INTERFACE')
		rangeHeader = request.META.get('HTTP_RANGE')
		# nginxRealIP = request.META.get('X_REAL_IP')
		# print("Range header=" + rangeHeader)
		# print("RealIP=" + nginxRealIP)

		if interface == 'CGI/1.1':  # request not come from nginx
			offset = block = 0
			if rangeHeader:
				try:
					offset, end = rangeHeader[6:].split('-')
					# print offset,end;
					offset = int(offset)
					if end:
						end = int(end)
						block = end - offset
					else:
						end = file_size
				except Exception as e:
					return errorResponse(u"Invalid Range Header", code=0)
			# django serve file
			print(request.META)
			print(u"Warning: File serve direcly from django not nginx with offset=%s, block=%s" % (offset, block))
			fsock = open(settings.MEDIA_ROOT + '/' + file_location, 'rb')

			fsock.seek(offset, 0)
			if block:
				data = fsock.read(block)
			else:
				data = fsock.read()
			fsock.close()
			response = HttpResponse(data)
			response["Content-Disposition"] = 'attachment; filename="%s"' % (file_name)
		else:
			response = HttpResponse()
			response["Content-Disposition"] = 'attachment; filename="%s"' % (file_name)
			file_path = '/media/' + file_location
			print('==file_path==',file_path);
			# These lines let nginx handle download file
			response['X-Accel-Redirect'] = file_path
			# Set speed limit
			if speed_limit <= 0: #unlimited
				response['X-Accel-Limit-Rate'] = 'off' #unlimited
			else:
				response['X-Accel-Limit-Rate'] = speed_limit;

			if connection_limit>2:
				response['X-Accel-Redirect'] = '/nolimit'+file_path
		return response
	else:
		return Http404()

@api_view(['GET','POST','PUT'])
@signature_test()
def initiateDeleteSessionProcess(request):
	""" Serve file will get DeleteSession from server main. Then delete all these file and send back deleteFile request
		@return
	"""
	if request.method == 'POST':
		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
		fileSDK = FileSDK(settings.SERVER_MAIN_URL)

		maxFileDelete, retry = getParamsOr400(request, ('maxFileDelete', 500), ('retry', None))

		if retry == 'working':
			process_session_status = SessionStatus.working
		elif retry == 'failed':
			process_session_status = SessionStatus.failed
		else:  # default
			process_session_status = SessionStatus.waiting

		current_offset = 0
		total_batch = maxFileDelete / 100 + 1
		for i in range(total_batch):
			try:
				sessionList = sessionSDK.listSession(SessionType.delete, process_session_status, sid=-1, offset=current_offset, limit=100)
			except Exception as e:
				logging.error(u"unable to get sessionList with error=%s" % (e))
				return errorResponse(u"Unable to get sessionList with error=%s" % (e))

			sessionIDList = [str(session.id) for session in sessionList]

			if len(sessionIDList) == 0:
				logging.warning(u"Batch %d/%d ,There is no more delete session to process" % (i + 1, total_batch))
				return successResponse()

			if not sessionSDK.doneSession(sessionIDList, SessionStatus.working, type=SessionType.delete):
				logging.error(u"Skip Batch %d/%d ,Unable to mark delete session list as working session" % (i + 1, total_batch))
				current_offset += 100
				continue  # ignore this batch

			# async worker call
			try:
				processDeleteFileSessionList.delay(i, total_batch, [s.to_json() for s in sessionList])
			except Exception as e:
				logging.error(u"Skip Batch %d/%d ,Unable to make async worker call with error=%s" % (i + 1, total_batch, e));
		return successResponse()
	else:
		return Http404()

@api_view(['GET','POST','PUT'])
@signature_test()
def initiateMoveSessionProcess(request):
	""" Serve file will get MoveSession from server main. Then delete all these file and send back deleteFile request
		@return
	"""
	if request.method == 'POST':
		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
		fileSDK = FileSDK(settings.SERVER_MAIN_URL)

		maxFileMove, retry = getParamsOr400(request, ('maxFileMove', 500), ('retry', None))

		if retry == 'working':
			process_session_status = SessionStatus.working
		elif retry == 'failed':
			process_session_status = SessionStatus.failed
		else:  # default
			process_session_status = SessionStatus.waiting

		current_offset = 0
		batchSize = 100
		total_batch = maxFileMove / batchSize + 1
		for i in range(total_batch):
			try:
				sessionList = sessionSDK.listSession(SessionType.move, process_session_status, sid=-1, offset=current_offset, limit=batchSize, order_by='sid')
			except Exception as e:
				logging.error(u"unable to get sessionList with error=%s" % (e))
				return errorResponse(u"Unable to get sessionList with error=%s" % (e))

			sessionIDList = [str(session.id) for session in sessionList]

			if len(sessionIDList) == 0:
				logging.warning(u"Batch %d/%d ,There is no more delete session to process" % (i + 1, total_batch))
				return successResponse()

			try:
				sessionSDK.doneSession(sessionIDList, SessionStatus.working, type=SessionType.move)
			except Exception as e:
				logging.error(u"Skip Batch %d/%d ,Unable to mark delete session list as working session, error=%s" % (i + 1, total_batch, e))
				current_offset += batchSize
				continue  # ignore this batch

			# async worker call
			try:
				processMoveFileSessionList.delay(i, total_batch, [s.to_json() for s in sessionList])
			except Exception as e:
				logging.error(u"Skip Batch %d/%d ,Unable to make async worker call with error=%s" % (i + 1, total_batch, e));

		return successResponse()
	else:
		return Http404()

@api_view(['GET','POST','PUT'])
@signature_test()
def initiateClearTemporaryFolderProcess(request):
	""" Serve file will remove all chunk in temorary folder that exist more than an amount of time.
		@return
	"""
	if request.method == 'POST':
		# async worker call
		try:
			# 0 = clear all
			clearUploadedChunkExistSeconds = int(request.POST.get('clearUploadedChunkExistSeconds', -1));
			taskResult = processClearTemporaryFolder.delay(clearUploadedChunkExistSeconds);
		except Exception as e:
			return errorResponse(u"Unable to make async worker call with error=%s" % (e));

		try:
			taskResult.wait(timeout=30);
		except TimeoutError:
			logging.warning(u"Worker couldn't complete task in 30 seconds");
			return successResponse({'result': '?'})
		except Exception as e:
			return errorResponse(u"Worker failed to complete task with error=%s"%(e));

		if taskResult.successful():
			return successResponse({'result': taskResult.result});
		else:
			return errorResponse(u"Worker failed to complete task with unknow reason");

	else:
		return Http404();