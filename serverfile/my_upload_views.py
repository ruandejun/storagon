#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  my_upload_views.py
#
#
#  Created by V.Anh Tran on 11/28/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import sys
import datetime
import hashlib
import os
import jwt
import time

from django.utils import timezone


from django.core.cache import cache

from admin_resumable.files import ResumableFile
from admin_resumable.views import get_storage, get_chunks_subdir
from storagon.PrivateAPI_SDK import SessionSDK, FileSDK
from storagon.tool import *
from storagon.enum import *
from servermain.mongo_models import Session


def upload_to_path(fileName, fileSize):
	d = datetime.datetime.today().date()

	prePath = '' + str(d.year) + '/' + str(d.month) + '/' + str(d.day) + '/'
	# not change name when move file	using upload
	# doesn't need anymore, now we use linux scp to move file between server
#	if '.' not in fileName and (len(fileName) == 32 or len(fileName) == 12):fileName=fileName;
#	else:
	fileName = hashlib.md5((str(datetime.datetime.now()) + fileName + str(fileSize)).encode()).hexdigest()

	return prePath + fileName


def handleCompleted(request, actual_filepath, session_id, resumableFile):
	print(u"Session %s is completing..." % (session_id))
	try:
		file_name = resumableFile.filename
	except UnicodeDecodeError:
		file_name = resumableFile.identifierName
	file_size = resumableFile.size
	# file_hash= you can't calculate file_hash here cause this file is already encrypted

	fileSDK = FileSDK(settings.SERVER_MAIN_URL)
	userFile_id = fileSDK.addFile(session_id, actual_filepath, file_name, file_size)
	if not userFile_id:
		print(u"Sesssion %s failed, delete file at:%s" % (session_id, actual_filepath))
		# remove file
		try:
			os.remove(settings.MEDIA_ROOT + '/' + actual_filepath)
		except OSError:
			pass
		return None
	print(u"Session %s completed with userFile_id=%s, save file to:%s" % (session_id, userFile_id, actual_filepath))
	return userFile_id


def parse_rate(rate):
	"""
	Given the request rate string, return a two tuple of:
	<allowed number of requests>, <period of time in seconds>
	"""
	if rate is None:
		return (None, None)
	num, period = rate.split('/')
	num_requests = int(num)
	duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
	return (num_requests, duration)


def checkAndBanIPOfClientMakingTooManyFailureRequest(request,key_prefix=settings.CACHE_MONGO_SESSION_PREFIX):
	remote_addr = request.META.get('REMOTE_ADDR')
	key_failure = key_prefix+'_failure_'+remote_addr;
	history_failure = cache.get(key_failure, [])
	now = time.time();
	num_requests, duration = parse_rate(settings.SCOPED_RATE_THROTTLE_BAN_IP_TOLERANCE_RATES)
	while history_failure and history_failure[-1] <= now - duration:
		history_failure.pop()

	if len(history_failure) >= num_requests:
		#ban ip
		if remote_addr: banIPUsingCeleryWorkerCMD(remote_addr,key_failure);
	else:
		history_failure.insert(0, now)
		cache.set(key_failure, history_failure, duration)


def my_resumable(request, upload_session_id=None, token=None):
	if request.method == 'POST':
		kwarg = request.POST
	elif request.method == 'GET':
		kwarg = request.GET
	else:
		checkAndBanIPOfClientMakingTooManyFailureRequest(request)
		return Http403(u"method not allowed");

	resumableChunkNumber = int(kwarg.get('resumableChunkNumber', 0))
	resumableTotalChunks = int(kwarg.get('resumableTotalChunks', 0))

	session = None
	# try to get session from cache if this is not first chunk
	if resumableChunkNumber != 1:
		session = cache.get(settings.CACHE_MONGO_SESSION_PREFIX + upload_session_id, None)

	if not session and token:
		decodedSessionData = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256");
		# try:
		#
		# except jwt.DecodeError as e:
		# 	logging.error(u"Failed to decode JWT token");
		# else:
		session = Session.from_json(json.dumps(decodedSessionData));
		logging.debug(u"Success decode JWT token");

	# check session before upload here
	if session is None:  # cache miss
		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
		session = sessionSDK.getSession(upload_session_id)
		# try:

		# except Exception as e:
		# 	session = None
		# 	logging.error(u"my_resumable: Unable to getSession, error=%s" % (e))

	if not session:
		checkAndBanIPOfClientMakingTooManyFailureRequest(request)
		return errorResponse(u"Unable to retrive upload session, cancel upload!", code=0)
	else:  # set cache
		cache.set(settings.CACHE_MONGO_SESSION_PREFIX + upload_session_id, session, settings.MONGO_SESSION_EXPIRES)

	if session.type == SessionType.upload and session.status == SessionStatus.completed:
		checkAndBanIPOfClientMakingTooManyFailureRequest(request)
		return HttpResponse("Upload completed but unable to return file_id")

	if session.type != SessionType.upload or session.status in [SessionStatus.completed,
		SessionStatus.failed] or timezone.now() > session.created + datetime.timedelta(seconds=settings.MONGO_SESSION_EXPIRES):
		checkAndBanIPOfClientMakingTooManyFailureRequest(request)
		return errorResponse(u"Invalid upload session, cancel upload!", code=0)

	if session.status == SessionStatus.working and session.data.get('duplicateFile_id', 0) > 0:
		if resumableChunkNumber == resumableTotalChunks and resumableChunkNumber > 0:
			fileSDK = FileSDK(settings.SERVER_MAIN_URL)
			try:
				userFile_id = fileSDK.addDuplicateFile(upload_session_id)
			except Exception as e:
				userFile_id = None
				logging.error(u"my_resumable: Sesssion failed, can't make userfile from duplicate file, error=%s" % (e))
			if not userFile_id:
				checkAndBanIPOfClientMakingTooManyFailureRequest(request)
				return errorResponse(u"Unable to finish upload session, cancel upload!", code=0)
			return HttpResponse('file_id=' + str(userFile_id))
		return HttpResponse('chunks already exists')  # hash check detected duplicate file

	# check and process chunk
	tmp_storage = get_temp_storage()
	if request.method == 'POST':
		file = request.FILES.get('file')
		if not file:
			checkAndBanIPOfClientMakingTooManyFailureRequest(request)
			return errorResponse(u"chunk is missing")

		if len(file) == 0:
			checkAndBanIPOfClientMakingTooManyFailureRequest(request)
			# logging.error(u"POST: %s\nfile:%s"%(request.POST,file));
			# logging.error(u"len file:%s"%(len(file)));
			return errorResponse(u"chunk is invalid")

		# logging.debug(u"POST: %s\nfile:%s"%(request.POST,file));

		try:
			r = ResumableFile(tmp_storage, request.POST)
		except Exception as e:
			return HttpResponseServerError(str(e));
		r.process_chunk(file)
	elif request.method == 'GET':  # handle reuploaded chunks:
		try:
			r = ResumableFile(tmp_storage, request.GET)
		except Exception as e:
			return HttpResponseServerError(str(e));
		if not r.chunk_exists:
			return HttpResponse('chunk not found', status=200)

	# check completed
	if resumableChunkNumber >= resumableTotalChunks-9: #Just for sure, due to last chunk may completed before other chunks
		if r.is_complete:
			#mark this session as completed to prevent multiple addFile.
			session.status = SessionStatus.completed;
			cache.set(settings.CACHE_MONGO_SESSION_PREFIX + upload_session_id, session, settings.MONGO_SESSION_EXPIRES);

			storage = get_storage()
			actual_filename = storage.save(upload_to_path(r.identifierName, r.size), r.file)
			r.delete_chunks()
			actual_filepath = get_chunks_subdir() + actual_filename
			userFile_id = handleCompleted(request, actual_filepath, upload_session_id, r)  # post upload, file actualy saved
			return HttpResponse('file_id=' + str(userFile_id))
		elif resumableChunkNumber == resumableTotalChunks:
			return HttpResponse("Upload finished but resumable file is not complete")

	# if request.method == 'POST':
	# 	return HttpResponse('chunk uploaded')
	# elif request.method == 'GET':
	return HttpResponse('chunk uploaded')


def main():
	pass

if __name__ == "__main__":
	sys.exit(main())
