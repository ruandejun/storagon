#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  ServerFileController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.utils import timezone
from django.db.models import Sum
from servermain.models import ServerFile
from servermain.mongo_models import ServerFileStorage
from storagon.tool import *


def calculateServerFileStorage(serverFile_id):

	serverStorage = getServerFileStorage(serverFile_id);

	try:
		serverFile = ServerFile.objects.get(id=serverFile_id)
	except ServerFile.DoesNotExist:
		return None

	fileCount = serverFile.realfile_set.count()

	result = serverFile.realfile_set.aggregate(Sum('file_size'))
	storageUsed = result['file_size__sum']

	serverStorage.file_count = fileCount
	serverStorage.storage_used = storageUsed

	# todo: calculate upload/download bandwidth

	serverStorage.calculated_date = timezone.now()
	serverStorage.save()

	return serverStorage


def getServerFileStorage(serverFile_id):
	serverStorage, created = ServerFileStorage.objects.get_or_create(pk=serverFile_id, defaults={'pk': serverFile_id})
	return serverStorage


def getAvailableServerFileForUpload():
	""" Return the suitable ServerFile for upload
	"""
	bestServerFile = ServerFile.objects.all().order_by('priority').first()
	return bestServerFile


def getCurrentConnectingServerFile(request):
	ip=request.META['REMOTE_ADDR'];
	try:
		serverFile = ServerFile.objects.get(ip_address=ip);
	except Exception as e:
		logging.error(u"Unable to determine server file with IP=%s"%(ip));
		return None;
	return serverFile;