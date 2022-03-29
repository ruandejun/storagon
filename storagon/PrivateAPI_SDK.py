#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  PrivateAPI_SDK.py
#
#
#  Created by V.Anh Tran on 12/2/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#


import json
import hashlib
import urllib
from storagon.browser import Rqbrowser
from servermain.mongo_models import Session
from urllib.parse import urlencode
#remember to set the head in correct format or apache won't allow it.
SIGNATURE_HEADER = 'Signature-Authorization'
SECRET_KEY = '7yn^8pwp+yzd2l4ki6+v9kp(h)rzs$9gxu4ao^_p+9x_5+1*6o'


def generateAuthorizationHeader(params):
	if isinstance(params, str) or isinstance(params, bytes):
		signature = hashlib.md5(str(SECRET_KEY + str(params)).encode('utf-8')).hexdigest()
	else:
		signature = hashlib.md5(str((SECRET_KEY) + str(urlencode(params))).encode('utf-8')).hexdigest()

	return {SIGNATURE_HEADER: signature}


class FileSDK():

	def __init__(self, serverMainURL):
		self.browser = Rqbrowser()
		self.serverMainURL = serverMainURL

	def addFile(self, upload_session_id, file_location, file_name, file_size):
		""" Add file to server main
		"""
		dataPOST = {
			'upload_session_id': upload_session_id,
			'file_location': file_location,
			'file_name': file_name,
			'file_size': file_size,
		}
		html = self.browser.open(self.serverMainURL + '/prapi/file/addFile/', dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))
		# print('___addFile:',html)
		result = json.loads(html)
		return result['userFile_id']

	def addDuplicateFile(self, upload_session_id):
		""" Add file to server main that found duplicate
		"""
		dataPOST = {
			'upload_session_id': upload_session_id,
		}
		html = self.browser.open(self.serverMainURL + '/prapi/file/addDuplicateFile/', dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))

		result = json.loads(html)
		return result['userFile_id']

	def moveFile(self, file_location_list, serverFileID, new_server_id):
		""" Move file to another serverFile
		"""
		dataPOST = [('file_location', file_location) for file_location in file_location_list] + [('old_server_id', serverFileID), ('new_server_id', new_server_id)]
		result = self.browser.open(self.serverMainURL + '/prapi/file/moveFile/', dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))

		return True

	def deleteFile(self, file_location_list, serverFileID):
		""" Delete realfile on servermain after actualy delete the file
		"""
		dataPOST = [('file_location', file_location) for file_location in file_location_list] + [('server_id', serverFileID)]
		result = self.browser.open(self.serverMainURL + '/prapi/file/deleteFile/', dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))

		return True

	def directDownloadFile(self, file_location, remoteServerFileURL, path_to_save):
		""" Download file directly from serverFile
		:param file_location:
		:param remoteServerFileURL:
		:return:
		"""
		self.browser.setAddHeader('Authorization', 'Basic YWRtaW46aGFub2kxMjM2NTQ=');
		self.browser.download(remoteServerFileURL+'/direct/media/'+file_location, path_to_save);

		return True;


class SessionSDK():

	def __init__(self, serverMainURL):
		self.browser = Rqbrowser()
		self.serverMainURL = serverMainURL

	def getSession(self, session_id):
		""" Get session from server main

		session_id: id of session

		return JSON session
		"""
		dataGET = '?session_id=%s' % (session_id)
		url = str(self.serverMainURL + '/prapi/session/getSession/' + dataGET)
		html = self.browser.open(url, extraHeader=generateAuthorizationHeader(url))
		# print('session_url==',url)
		# print('html==',html)
		session = Session.from_json(html)
		return session

	def doneSession(self, session_id_list, status, type=None):
		""" Change status of one or multiple session at a time

		session_id_list: list session id
		status : new status

		"""

		dataPOST = [('session_id', session_id) for session_id in session_id_list] + [('status', status)]
		if type is not None:
			dataPOST += [('type', type)]

		result = self.browser.open(self.serverMainURL + '/prapi/session/doneSession/', dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))
		return True

	def listSession(self, type, status, uid=None, fid=None, sid=None, from_date=None, to_date=None, offset=0, limit=0, order_by=None):
		""" Get List session from server main

		type : Enum SessionType, required
		status : Enum SessionStatus, required
		uid : user id,
		fid : file_id UserFile and RealFile or folder_id
		sid : server_id
		from_date : filter created DateTime
		to_date : filter created DateTime
		offset :
		limit :
		order_by : order_by ?
		return JSON list session
		"""
		dataGET = '?type=%s&status=%s' % (type, status)
		if uid:
			dataGET += '&uid=%s' % (uid)
		if fid:
			dataGET += '&fid=%s' % (fid)
		if sid:
			dataGET += '&sid=%s' % (sid)

		if from_date:
			dataGET += '&from_date=%s' % (from_date.strftime("%Y-%m-%d_%H-%M-%S"))
		if to_date:
			dataGET += '&to_date=%s' % (to_date.strftime("%Y-%m-%d_%H-%M-%S"))
		if offset:
			dataGET += '&offset=%s' % (offset)
		if limit:
			dataGET += '&limit=%s' % (limit)
		if order_by:
			dataGET += '&order_by=%s' % (order_by)

		url = str(self.serverMainURL + '/prapi/session/listSession/' + dataGET)

		html = self.browser.open(url, extraHeader=generateAuthorizationHeader(url))

		sessionList = [Session.from_json(json.dumps(sessionData)) for sessionData in json.loads(html)]
		return sessionList


class SignalSDK():

	def __init__(self, serverFileURL):
		self.browser = Rqbrowser()
		self.serverFileURL = serverFileURL

	def initiateDeleteSessionProcess(self, maxFileDelete, retry=None):
		""" Initiate delete session process of server file

		maxFileDelete: max number of file want this process to delete
		retry: 'working','failed' to retry these DeleteSession, eitherwhile will process only 'waiting' DeleteSession

		return
		"""
		dataPOST = {
			'maxFileDelete': int(maxFileDelete),
			'retry': retry,
		}
		url = str(self.serverFileURL + '/sf/initiateDeleteSessionProcess/')
		result = self.browser.open(url, dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))
		return True

	def initiateMoveSessionProcess(self, maxFileMove, retry=None):
		""" Initiate move session process of server file

		maxFileMove: max number of file want this process to move
		retry: 'working','failed' to retry these DeleteSession, eitherwhile will process only 'waiting' DeleteSession

		return
		"""
		dataPOST = {
			'maxFileMove': int(maxFileMove),
			'retry': retry,
		}
		url = str(self.serverFileURL + '/sf/initiateMoveSessionProcess/')
		result = self.browser.open(url, dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))
		return True

	def initiateClearTemporaryFolderProcess(self, clearUploadedChunkExistSeconds=-1):
		""" Initiate move session process of server file

		maxFileMove: max number of file want this process to move
		retry: 'working','failed' to retry these DeleteSession, eitherwhile will process only 'waiting' DeleteSession

		return
		"""
		dataPOST = {
			'clearUploadedChunkExistSeconds': clearUploadedChunkExistSeconds,
		}
		url = str(self.serverFileURL + '/sf/initiateClearTemporaryFolderProcess/')
		html = self.browser.open(url, dataPOST, extraHeader=generateAuthorizationHeader(dataPOST))
		result = json.loads(html);
		return result;
