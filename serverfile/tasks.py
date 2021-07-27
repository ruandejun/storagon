#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  tasks
#
#
#  Created by TVA on 1/29/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#
import os, fnmatch, re, datetime, jwt

from celery import shared_task

from storagon.enum import *
from storagon.tool import *
from storagon.PrivateAPI_SDK import SessionSDK, FileSDK
from servermain.mongo_models import Session





@shared_task
def processDeleteFileSessionList(i, total_batch, sessionList):
	""" Move file between serverFile (in worker)

	:param i: current_batch
	:param total_batch: total_batch
	:param sessionList: List of all move sessions have been marked as working
	:return:
	"""
	sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
	fileSDK = FileSDK(settings.SERVER_MAIN_URL)
	completedSessionIDList = []
	failedSessionIDList = []
	fileLocationList = []
	storage = get_media_storage();
	for session_json in sessionList:
		session = Session.from_json(session_json);
		file_location = session.text
		if not file_location:
			continue
		fileLocationList += [file_location]
		# remove file

		# if not storage.exists(file_location):
		# 	logging.warning(u"File not exist at %s"%(file_location));
		# 	print storage.listdir('');

		try:
			# os.remove(settings.MEDIA_ROOT + '/' + file_location)
			storage.delete(file_location);
		except Exception as e:
			logging.error(u"Couldn't process session_id=%s, with error=%s remove file at %s"%(session.id, e, file_location));
			failedSessionIDList += [session.id]
		else:
			completedSessionIDList += [session.id]

	if len(fileLocationList)>0:
		for ti in range(3):  # retry this 3 time
			result = fileSDK.deleteFile(fileLocationList, settings.SERVER_FILE_ID)
			if result:  # server main has delete these realfile
				break
			else:
				logging.error(u"Unable to send deleteFile signal to servermain retry no.%d" % (ti + 1))
				continue
		else:  # failed all retry
			return errorResponse(u"Unable to send deleteFile signal to servermain after all retry", code=0)

	logging.info(u"Batch %d/%d Success delete %s file" % (i + 1, total_batch, len(completedSessionIDList)))
	if len(completedSessionIDList):
		try:
			sessionSDK.doneSession(completedSessionIDList, SessionStatus.completed)
		except Exception as e:
			pass;

	if len(failedSessionIDList) > 0:
		logging.error(u"Batch %d/%d Failed to delete %s file" % (i + 1, total_batch, len(failedSessionIDList)))
		try:
			sessionSDK.doneSession(failedSessionIDList, SessionStatus.failed)
		except Exception as e:
			pass;
	# end a batch


def recursive_mkdir(dirPath, stopAtDir='media'):
	parentPath, dirName = os.path.split(dirPath)

	if dirName == stopAtDir: return;
	if parentPath and parentPath != '/':
		recursive_mkdir(parentPath)
	try:
		os.mkdir(dirPath, 0o777)
	except OSError as e:
		try:
			os.chmod(dirPath, 0o777)
		except OSError as e:
			logging.error(u"Couldn't create folder:%s" % (dirPath))
		# else:
		# 	logging.debug(u"Success chmod folder:%s" % (dirPath))
	else:
		logging.info(u"Success create folder:%s" % (dirPath))

@shared_task
def processMoveFileSessionList(i, total_batch, sessionList):
	""" Move file between serverFile (in worker)

	:param i: current_batch
	:param total_batch: total_batch
	:param sessionList: List of all move sessions have been marked as working
	:return:
	"""
	sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
	fileSDK = FileSDK(settings.SERVER_MAIN_URL)
	completedSessionIDList = []
	failedSessionIDList = []
	fileLocationList = []

	fileLocationDict = {};

	new_server_id = None
	for session_json in sessionList:
		session = Session.from_json(session_json);

		file_location = session.data['file_location']

		old_server_id = session.data['old_server_id']
		old_server_address = session.data['old_server_address']
		new_server_id = session.data['new_server_id']
		new_server_address = session.data['new_server_address']

		if not file_location: continue


		# this localPath is used for testing only
		#localPath = os.path.join('/home/vagrant/media', file_location);

		localPath = os.path.join(settings.MEDIA_ROOT, file_location)

		# Download
		result=False;

		try:
			localFolderPath, saved_file_name = os.path.split(localPath);
			recursive_mkdir(localFolderPath);
			result=fileSDK.directDownloadFile(file_location, new_server_address, localPath);
		except Exception as e:
			failedSessionIDList += [session.id]
			logging.error(u"Unable to download file from remote server to:%s, error=%s" % (localPath, e))
			continue

		if result:# success
			completedSessionIDList += [session.id]
			fileLocationList = fileLocationDict.get(old_server_id, [])
			fileLocationList.append(file_location);
			fileLocationDict[old_server_id] = fileLocationList;

	for old_server_id, fileLocationList in fileLocationDict.items():
		for ti in range(3):  # retry this 3 time
			result = fileSDK.moveFile(fileLocationList, old_server_id, new_server_id);
			if result:  # server main has delete these realfile
				break
			else:
				logging.error(u"Unable to send moveFile signal to servermain retry no.%d" % (ti + 1))
				continue
		else:  # failed all retry
			return errorResponse(u"Unable to send moveFile signal to servermain after all retry", code=0)

	logging.info(u"Batch %d/%d Success move %s file" % (i + 1, total_batch, len(completedSessionIDList)))
	if len(completedSessionIDList) > 0:
		try:
			sessionSDK.doneSession(completedSessionIDList, SessionStatus.completed, type=SessionType.move)
		except Exception as e:
			pass

	if len(failedSessionIDList) > 0:
		logging.error(u"Batch %d/%d Failed to move %s file" % (i + 1, total_batch, len(failedSessionIDList)))
		try:
			sessionSDK.doneSession(failedSessionIDList, SessionStatus.failed, type=SessionType.move)
		except Exception as e:
			pass
	# end a batch





@shared_task
def processClearTemporaryFolder(clearUploadedChunkExistSeconds=-1):
	""" Move file between serverFile (in worker)

	:param clearUploadedChunkDateTime: clear all chunk that have uploaded time before this
	:return:
	"""

	if clearUploadedChunkExistSeconds<0:
		clearUploadedChunkExistSeconds=settings.MONGO_SESSION_EXPIRES;

	clearUploadedChunkDateTime=datetime.datetime.now() - datetime.timedelta(seconds=clearUploadedChunkExistSeconds);

	storage = get_temp_storage();
	chunk_suffix = "_part_"

	files = sorted(storage.listdir('')[1])
	count=0;
	ignore=0;
	for file in files:
		if fnmatch.fnmatch(file, '*%s*' % (chunk_suffix)):
			uploaded_time = storage.created_time(file);
			if uploaded_time < clearUploadedChunkDateTime:
				storage.delete(file); #remove chunk.
				count+=1;
			else:
				ignore+=1;

	logging.info(u"Success removed temporary chunks=%s before %s and ignore %s chunks"%(count, clearUploadedChunkDateTime, ignore));

	return count;


@shared_task
def scanTrafficLogForCompletedSession(traffic_log_path, clear_log=True):
	""" Scan traffic log

	:return:
	"""
	completedSessionIDList=[];
	with open(traffic_log_path) as f:
		line = True;
		while line:
			line = f.readline();
			# "$request"|$http_range|$remote_addr|$body_bytes_sent|$status
			splited = line.split('|');
			if len(splited)!=5:continue;
			request,http_range,remote_addr,body_bytes_sent,status = tuple(splited);
			m=re.search(r'download/(\w+)/(.*?)/(.*) HTTP',request);
			if not m:continue;
			session_id=m.group(1);
			session_JWT_data=m.group(2);

			# m=re.search(r'bytes=(\d*)-(\d*)',http_range);
			# bytes_begin=0;
			# if m:
			# 	try:bytes_begin=int(m.group(1));
			# 	except:bytes_begin=0;

			# get from cache first
			session = cache.get(settings.CACHE_MONGO_SESSION_PREFIX + session_id, None)
			#get from jwt token
			if not session:
				try:
					decodedSessionData = jwt.decode(session_JWT_data, settings.SECRET_KEY);
				except jwt.DecodeError as e:
					logging.error(u"Failed to decode JWT token");
				else:
					session = Session.from_json(json.dumps(decodedSessionData));

			total_bandwidth = session.data.get('total_bandwidth',0);

			body_bytes_sent = int(body_bytes_sent);
			session.data['total_bandwidth']=total_bandwidth+body_bytes_sent;

			if session.data['total_bandwidth'] >= session.data['file_size']*0.99:
				#mark this session as completed to prevent multiple download of same file.
				session.status = SessionStatus.completed;
				completedSessionIDList+=[session_id];
			cache.set(settings.CACHE_MONGO_SESSION_PREFIX + session_id, session, settings.MONGO_SESSION_EXPIRES);

	if len(completedSessionIDList):
		sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
		for ti in range(3):
			try:sessionSDK.doneSession(completedSessionIDList, SessionStatus.completed, SessionType.download);
			except:pass;
			else:break;
		else:
			logging.error(u"Unable to send request for marking completed download session.");
			return False;
		logging.info(u"Send request to marking completed download sessions success=%s"%(len(completedSessionIDList)));

	#clear log
	if clear_log: open(traffic_log_path, 'w').close();

	return True;

