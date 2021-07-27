#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  File_PrivateAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse

from django.conf import settings  # site setting
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required

from servermain.models import UserFile, RealFile, UserProfile
from servermain.mongo_models import Session
from servermain.controllers import UserController
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import signature_test
import base64
from Crypto.Cipher import AES


@signature_test()
def addFile(request):
	""" Add a new file to Storagon

	request.POST={
		upload_session_id : id of upload session
		file_location : file_location where realfile is saved to disk on server file

		file_name : file_name if not sepecify in upload_session.data
		file_size : overide what in upload_session.data
	}

	response = {
		userFile_id : id of new upload file
	}
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':

		upload_session_id, file_location, file_name, file_size = getParamsOr400(request, 'upload_session_id', 'file_location', 'file_name', ('file_size', int))

		try:
			uploadSession = Session.objects.get(id=upload_session_id, type=SessionType.upload)
		except Session.DoesNotExist:
			return errorResponse(u"Session does not exist", code=0)
		if uploadSession.status in [SessionStatus.completed, SessionStatus.failed]:
			return errorResponse(u"Invalid upload session, cancel upload!", code=0)

		# add new RealFile
		file_hash = uploadSession.data['file_hash'].strip()
		try:
			duplicate = RealFile.objects.get(file_hash=file_hash)
		except RealFile.DoesNotExist:
			duplicate = None  # OK
		except RealFile.MultipleObjectsReturned:
			logging.warning(u"Found realfile duplicated for file_hash=%s" % (file_hash))
			duplicate = RealFile.objects.all().filter(file_hash=file_hash).first()

		if duplicate:
			uploadSession.data['duplicateFile_id'] = duplicate.id
			uploadSession.status = SessionStatus.working
			uploadSession.save()
			return addDuplicateFile(request)  # let the addDuplicateFile handle this request instead.

		resultCheck = UserController.checkUserCanUploadFile(uploadSession.uid, file_size);
		if resultCheck is not True:
			return errorResponse(u"You're not allowed to upload due to: %s"%(resultCheck), code=0);

		realFile = RealFile(file_location=file_location)
		realFile.serverFile_id = uploadSession.sid
		realFile.file_hash = file_hash
		# file_size override
		if file_size > 0:
			realFile.file_size = file_size
		else:
			realFile.file_size = uploadSession.data['file_size']
		realFile.save()
		# add new UserFile
		userFile = UserFile(realFile=realFile)
		if uploadSession.data.get('file_name'):
			userFile.file_name = uploadSession.data['file_name'].strip()
		else:
			userFile.file_name = file_name.strip()
		if uploadSession.fid:
			userFile.folder_id = uploadSession.fid  # as folder_id

		erfk = uploadSession.data.get('erfk')  # this is base64 encoded erfk
		if settings.ENABLE_ENCRYPTION and erfk:  # encryption of filekey
			upload_userProfile = UserProfile.objects.get(id=uploadSession.uid)
			eumk = base64.b64decode(upload_userProfile.eumk)
			cipher = AES.new(eumk, AES.MODE_ECB)
			cipherText = cipher.encrypt(base64.b64decode(erfk))
			userFile.erfk = base64.b64encode(cipherText)

		userFile.user_id = uploadSession.uid
		try:
			userFile.save()
		except Exception as e:
			logging.error(u"Couldn't save newFile with error=%s" % (e))
			return errorResponse(u"Couldn't save newFile", code=0)

		# complete session
		uploadSession.status = SessionStatus.completed
		uploadSession.text = str(realFile.id)  # save realFile.id in this field for later use
		uploadSession.save()
		logging.info("addFile: success with file_location=%s" % (file_location))
		return successResponse({
			'userFile_id': userFile.id,
		})
	else:
		raise Http404()


@signature_test()
def addDuplicateFile(request):
	""" Add a new file to Storagon that is found duplicate with previous file

	request.POST={
		upload_session_id : id of upload session
	}

	response = {
		userFile_id : id of new upload file
	}
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		upload_session_id = getParamsOr400(request, 'upload_session_id')
		try:
			uploadSession = Session.objects.get(id=upload_session_id, type=SessionType.upload)
		except Session.DoesNotExist:
			return errorResponse(u"Session does not exist", code=0)
		if uploadSession.status in [SessionStatus.completed, SessionStatus.failed]:
			return errorResponse(u"Invalid upload session, cancel upload!", code=0)

		file_name = uploadSession.data['file_name']
		folder_id = uploadSession.fid

		try:
			duplicateFile = RealFile.objects.get(id=uploadSession.data['duplicateFile_id'])
		except RealFile.DoesNotExist:
			logging.error(u"coundn't find duplicate file!")
			return errorResponse(u"Couldn't find duplicate file!", code=0)

		resultCheck = UserController.checkUserCanUploadFile(uploadSession.uid, duplicateFile.file_size);
		if resultCheck is not True:
			return errorResponse(u"You're not allowed to upload due to: %s"%(resultCheck), code=0);

		newFile = UserFile(file_name=file_name, folder_id=folder_id, user_id=uploadSession.uid, realFile=duplicateFile)

		# get one of duplicate's UserFile for resolving data
		try:
			userFile = duplicateFile.userfile_set.all().first()
		except:
			userFile = None

		if settings.ENABLE_ENCRYPTION:
			if userFile and userFile.erfk:  # decryption of fileKey
				last_userProfile = userFile.user.profile
				eumk = base64.b64decode(last_userProfile.eumk)
				cipher = AES.new(eumk, AES.MODE_ECB)
				erfk = cipher.decrypt(base64.b64decode(userFile.erfk))
			else:
				# solve the case duplicateFile.userfile_set.count()==0 by check for UploadSession of this duplicateFile and retrive erfk from that
				try:
					lastUploadSession = Session.objects.get(text=str(duplicateFile.id), type=SessionType.upload, status=SessionStatus.completed)
				except Session.DoesNotExist:
					logging.error(u"Couldn't resolve duplicateFile.id=%s due to no UserFile and last uploadSession is not saved!" % (duplicateFile.id))
					#delete realFile immediately due to unable to solve conflict.
					duplicateFile.delete();
					return errorResponse(u"Couldn't resolve duplicate file", code=0)
				except Session.MultipleObjectsReturned:
					lastUploadSession = Session.objects.filter(text=str(duplicateFile.id), type=SessionType.upload, status=SessionStatus.completed).first()

				erfk = base64.b64decode(lastUploadSession.data['erfk'])
				if not erfk or len(erfk) != 32:
					logging.error(u"Couldn't resolve duplicateFile.id=%s due to invalid erfk=%s from last uploadSession!" % (duplicateFile.id, erfk))
					#delete realFile immediately due to unable to solve conflict.
					duplicateFile.delete();
					return errorResponse(u"Couldn't resolve duplicate file", code=0)

			# reencryption of filekey
			upload_userProfile = UserProfile.objects.get(id=uploadSession.uid)
			new_eumk = base64.b64decode(upload_userProfile.eumk)
			new_cipher = AES.new(new_eumk, AES.MODE_ECB)
			cipherText = new_cipher.encrypt(erfk)
			newFile.erfk = base64.b64encode(cipherText)
			#save erfk to upload session
			uploadSession.data['erfk'] = base64.b64encode(erfk)

		#save new duplicated file
		try:
			newFile.save()
		except Exception as e:
			logging.error(u"Couldn't save newFile with error=%s" % (e))
			return errorResponse(u"Couldn't save newFile", code=0)

		if userFile is None:#realFile dont have userfile anymore and this add a new userFile to it. remove marked delete session
			result = Session.objects.filter(status=SessionStatus.waiting, type=SessionType.delete, fid=duplicateFile.id, sid=duplicateFile.serverFile.id, text=duplicateFile.file_location).delete();
			logging.info(u"Remove marked delete session of realFile_id=%s with result=%s"%(duplicateFile.id, result));

		uploadSession.status = SessionStatus.completed
		uploadSession.save()
		logging.info(u"success with realFile_id=%s and userFile_id=%s" % (duplicateFile.id, newFile.id))
		return successResponse({
			'userFile_id': newFile.id,
		})
	else:
		raise Http404()


@signature_test()
def moveFile(request):
	""" Move file from a server to another server
	Don't need to do bulk update because moveFile between servers is a very slow process
	request.POST = {
		file_location: realFile location ,
	or fileLocationList
		old_server_id: move realfile from server,
		new_server_id: to server,
	}

	response = success or error

	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		fileLocationList, old_server_id, new_server_id = getParamsOr400(request, ('file_location', list), ('old_server_id', int), ('new_server_id', int))

		# change realFile
		try:
			result = RealFile.objects.filter(file_location__in=fileLocationList, serverFile_id=old_server_id).update(serverFile_id=new_server_id)
		except Exception as e:
			logging.error(u"Bulk update failed with error=%s" % (e))
			# return errorResponse(u"Unable to change realFile.serverFile from old_server_id=%s to new_server_id=%s"%(old_server_id,new_server_id));
		else:
			logging.info(u"Bulk update success with result=%s" % (result))
		return successResponse()
	else:
		raise Http404()


@signature_test()
def deleteFile(request):
	""" Server file will call this after actually delete a file

	request.POST = {
		file_location: realFile location ,
	or fileLocationList
		server_id: server_id has delete these files,
	}

	response = success or error

	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		fileLocationList, server_id = getParamsOr400(request, ('file_location', list), ('server_id', int))

		# delete realFile corresponding to these file_location
		try:
			result = RealFile.objects.filter(file_location__in=fileLocationList, serverFile_id=server_id).delete()
		except Exception as e:
			logging.error(u"Bulk delete failed with error=%s" % (e))
		else:
			logging.info(u"Bulk delete success with result=%s" % (result))
		return successResponse()
	else:
		raise Http404()




