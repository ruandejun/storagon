#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  File_ClientAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse
from django.utils import timezone
from django.conf import settings  # site setting
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers

from servermain.controllers import FileController
from servermain.mongo_models import Session
from servermain.models import UserFile, RealFile, Folder, ServerFile
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import banned_check, login_required_ajax, signature_test
from rest_framework.decorators import api_view

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def moveFile(request):
	""" Move file in fileIDList to folder_id

	request.POST = {
			file_id: one or List of id
			folder_id:
	}

	response = Success or error

	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		fileIDList, folder_id = getParamsOr400(
			request, ('file_id', list), ('folder_id', int))

		if folder_id <= 0:
			folder_id = None

		try:
			result = UserFile.objects.filter(id__in=fileIDList, user=request.user).update(folder_id=folder_id, modified_date=timezone.now())
		except Exception as e:
			logging.error(u"File_ClientAPI.deleteFile: Bulk update failed with error={}".format(e))
		else:
			logging.info(u"File_ClientAPI.deleteFile: Bulk update success with result={}".format(result))
		for userFile in UserFile.objects.filter(id__in=fileIDList, user=request.user):
			FileController.autoReplaceUserFileWithSameNameInSameFolder(userFile);

		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def deleteFile(request):
	""" Delete file in fileIDList

	request.POST = {
			file_id: one or List of id
	}

	response = Success or error

	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		fileIDList = getParamsOr400(request, ('file_id', list))

		try:
			result = UserFile.objects.filter(id__in=fileIDList, user=request.user).delete()
		except Exception as e:
			logging.error(u"File_ClientAPI.deleteFile: Bulk update failed with error={}".format(e))
		else:
			logging.info(u"File_ClientAPI.deleteFile: Bulk update success with result={}".format(result))
		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def newFolder(request):
	""" Create new folder in parent folder_id

	resquest.POST = {
			folder_name:,
			folder_id:
	}

	response = {
			folder_id: new folder id
	}
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		folder_name, folder_id = getParamsOr400(
			request, 'folder_name', ('folder_id', 0))

		folder_name = folder_name.strip()
		if not folder_name:
			raise Http400(u"folder_name")

		if folder_id <= 0:
			folder_id = None
		newFolder = Folder(
			name=folder_name,
			parent_folder_id=folder_id,
			user=request.user)
		checkFolder = FileController.checkFolderWithSameNameInSameFolderExist(newFolder);
		if checkFolder:
			return successResponse({
				'folder_id': checkFolder.id,
				'created': False
			})
		newFolder.save()
		return successResponse({
			'folder_id': newFolder.id,
			'created': True
		})
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def moveFolder(request):
	""" Move folders to a new folder

	request.POST = {
			folder_id: one or list of folder id,
			to_folder_id: id of folder want to move to, 0 for root folder
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		folderIDList, to_folder_id = getParamsOr400(
			request, ('folder_id', list), ('to_folder_id', int))

		if to_folder_id <= 0:
			to_folder_id = None
		if to_folder_id in folderIDList:
			folderIDList.remove(to_folder_id);

		try:
			result = Folder.objects.filter(
				id__in=folderIDList,
				user=request.user).update(
					parent_folder_id=to_folder_id,
					modified_date=timezone.now())
		except Exception as e:
			logging.error(u"File_ClientAPI.deleteFile: Bulk update failed with error={}".format(e))
		else:
			logging.info(u"File_ClientAPI.deleteFile: Bulk update success with result={}".format(result))

		for folder in Folder.objects.filter(id__in=folderIDList, user=request.user):
			FileController.autoMergeFolderWithSameNameInSameFolder(folder);

		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def deleteFolder(request):
	""" Delete folder in folderIDList

	request.POST = {
			folder_id: folderIDList
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		folderIDList = getParamsOr400(request, ('folder_id', list))

		try:
			result = Folder.objects.filter(
				id__in=folderIDList,
				folder_type=FolderType.normal, #allow only folder_type=normal to be deleted
				user=request.user).delete()
		except Exception as e:
			logging.error(u"File_ClientAPI.deleteFile: Bulk update failed with error={}".format(e))
		else:
			logging.info(u"File_ClientAPI.deleteFile: Bulk update success with result={}".format(result))
		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def listFileAndFolder(request):
	""" Get list file and folder of folderIDList

	request.GET = {
			folder_id : folderIDList ( if '' in folderIDList: get root folder, if 'all' in folderIDList: get all folders)
			file_offset: int offset from last batch
			file_limit: int number of file want to retrive
			count_download: Bool y/n
	}

	response = {
			fileList : String list JSON encode data of UserFile
			folderList : String list JSON encode data of sub Folder
			folderExists : String list JSON encode data of Folder in folderIDList
			fileInfoDict : dict JSON encode extra data of UserFile
	}
	"""
	if request.method == 'GET':
		folderIDList, file_offset, file_limit, count_download, order_by_filename = getParamsOr400(request, ('folder_id', list), ('file_offset', 0), ('file_limit', 0), ('count_download', 'y'), ('order_by_filename','n'))

		if '' in folderIDList:  # root folder
			folderIDList.remove('')
			folderQuery = Folder.objects.filter(parent_folder=None, user=request.user)
			fileQuery = UserFile.objects.filter(folder=None, user=request.user)

			try:
				# cache timeout in 7 seconds, to avoid wrong cache of this
				# query
				folderQuery.timeout = fileQuery.timeout = 7
			except AttributeError:
				pass

			folderExistsData = ''
		elif 'all' in folderIDList:  # get all folder and fie of current user
			folderQuery = Folder.objects.filter(user=request.user)
			fileQuery = UserFile.objects.filter(user=request.user)

			try:
				# don't cache, to avoid wrong cache of this query
				folderQuery.timeout = fileQuery.timeout = 0
			except AttributeError:
				pass

			folderExistsData = ''
		else:  # sub folder
			try:
				folderIDList = [int(folderID) for folderID in folderIDList]
			except Exception as e:
				return HttpResponseBadRequest(str(e))
			# print u"folderIDList=%s"%(folderIDList);

			# get folder that have parrent_folder is one of foldeIDList
			if file_offset>0:
				folderQuery=[]
			else:
				folderQuery = Folder.objects.filter(
					parent_folder_id__in=folderIDList,
					user=request.user)
				try:# cache timeout in 7 seconds, to avoid wrong cache of this
					folderQuery.timeout = 7
				except AttributeError:
					pass

			# get file that store in one of foldeIDList
			fileQuery = UserFile.objects.filter(
				folder_id__in=folderIDList,
				user=request.user)
			try:# cache timeout in 7 seconds, to avoid wrong cache of this
				fileQuery.timeout = 7
			except AttributeError:
				pass

			if len(folderIDList) > 1:
				folderExistsQuery = Folder.objects.filter(
					id__in=folderIDList,
					user=request.user)
				try:
					folderExistsQuery.timeout = 7
				except AttributeError:
					pass
				folderExistsData = serializers.serialize('json', folderQuery)
			else:
				folderExistsData = ''

		# print u"len(fileQuery)=%s ,
		# len(folderQuery)=%s"%(len(fileQuery),len(folderQuery));
		folderListData = serializers.serialize('json', folderQuery)
		if order_by_filename:
			fileQuery.order_by('file_name');
		else:
			fileQuery.order_by('created_date');

		if file_offset==0:
			file_count = fileQuery.count();
		else:
			file_count = None;

		if file_limit > 0:
			fileQuery = fileQuery[file_offset:file_offset + file_limit]
		else:
			fileQuery = fileQuery[file_offset:]
		# serialize
		fileListData = serializers.serialize(
			'json',
			fileQuery,
			fields=(
				'file_name',
				'created_date',
				'modified_date',
				'folder',
				'last_download_date',
				'download_count',
				'file_mode'
			))

		# get fileSize and downloadCount
		fileInfoDict = {}
		for userFile in fileQuery:
			fileInfoDict[userFile.id] = {
				'file_size': userFile.realFile.file_size,
				'file_hash': userFile.realFile.file_hash,
			}
			if count_download:
				download_count = Session.objects.filter(
					type=SessionType.download,
					status=SessionStatus.completed,
					fid=userFile.id,
					created__gt=timezone.now() - timezone.timedelta(days=1)
				).count()
				fileInfoDict[userFile.id]['download_count_24h'] = download_count

		return successResponse({
			'folderList': folderListData,
			'fileList': fileListData,
			'folderExists': folderExistsData,
			'fileInfoDict': fileInfoDict,
			'file_count': file_count,
		})
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def editFolder(request):
	""" Edit a folder properties: name

	request.POST = {
			folder_id : folder_id
			name:
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		folder_id, name = getParamsOr400(request, ('folder_id', int), 'name')

		name = name.strip()
		if not name:
			raise Http400(u"name")

		folder = shortcuts.get_object_or_404(
			Folder,
			id=folder_id,
			user=request.user)

		folder.name = name

		if FileController.checkFolderWithSameNameInSameFolderExist(folder):
			return errorResponse(u"A folder with same name exist already in parent folder");
		try:
			folder.save()
		except Exception as e:
			logging.error(u"File_ClientAPI.editFolder: folder.save error=%s" % (e))
			return errorResponse(u"Failed to save folder")

		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def editFile(request):
	""" Edit a file properties: name

	request.POST = {
			file_id : file_id
			file_name:
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':

		file_id, file_name = getParamsOr400(
			request, ('file_id', int), 'file_name')
		file_name = file_name.strip()
		if not file_name:
			raise Http400(u"file_name")

		userFile = shortcuts.get_object_or_404(
			UserFile,
			id=file_id,
			user=request.user)
		userFile.file_name = file_name

		try:
			userFile.save()
		except Exception as e:
			logging.error(u"File_ClientAPI.editFile: userFile.save error=%s" % (e))
			return errorResponse(u"Failed to save file")

		FileController.autoReplaceUserFileWithSameNameInSameFolder(userFile);

		return successResponse()
	else:
		raise Http404()

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def getLink(request):
	""" Get download page url of file in fileIDList

	request.GET = {
			file_id: one or List of id
	}

	response = {
			file_id_list : [],
			download_url_list: [],
	}

	"""
	if request.method == 'GET':

		fileIDList = getParamsOr400(request, ('file_id', list))

		try:
			fileIDList = [int(file_id) for file_id in fileIDList]
		except Exception as e:
			return HttpResponseBadRequest(str(e))

		resultList = shortcuts.get_list_or_404(
			UserFile.objects.filter(
				id__in=fileIDList,
				user=request.user))

		# reorder by the order of fileIDList
		fileDict = {}
		for userFile in resultList:
			fileDict[userFile.id] = userFile

		download_url_list = []
		for file_id in fileIDList:
			download_url_list += [
				request.build_absolute_uri(
					fileDict[file_id].get_absolute_url(usingDownloadViewNumber=1))]

		download_url_no_filename_list = []
		for file_id in fileIDList:
			download_url_no_filename_list += [
				request.build_absolute_uri(
					fileDict[file_id].get_absolute_url(usingDownloadViewNumber=2))]

		return successResponse({
			'download_url_list': download_url_list,
			'download_url_no_filename_list':download_url_no_filename_list,
		})
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()
