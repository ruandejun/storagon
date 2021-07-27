#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  mongo_models.py
#
#
#  Created by V.Anh Tran on 11/28/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import datetime

from storagon.tool import *
from storagon.enum import *
import mongoengine
from mongoengine import signals
from django.utils import timezone

class Session(mongoengine.Document):
	type = mongoengine.IntField(required=True, default=0, choices=SessionType.ChoiceList())
	uid = mongoengine.IntField(required=False)  # user_id
	fid = mongoengine.IntField(required=False)  # file_id UserFile and RealFile or folder_id
	sid = mongoengine.IntField(required=False)  # server_id or bill_id
	oid = mongoengine.IntField(required=False)  # owner_id (user_id)

	status = mongoengine.IntField(required=True, default=SessionStatus.waiting, choices=SessionStatus.ChoiceList())

	data = mongoengine.DictField(required=False, default={})
	text = mongoengine.StringField(required=False)  # text for query on string
	created = mongoengine.DateTimeField(required=True, default=timezone.now)

	def __unicode__(self): return "%s (%s %s)" % (self.id, SessionType.AllLabelList()[self.type], SessionStatus.AllLabelList()[self.status])


def postSaveSession(sender, document, **kwargs):
	if kwargs['created']:
		pass  # new session is created
	else:  # a session is saved
		# logging.debug(u"postSaveSession, document=%s"%(document));
		if document.status == SessionStatus.completed and document.type == SessionType.upload:
			# upload complete
			if 'file_size' not in document.data:
				logging.error(u'UploadSession.data not contain file_size')
				return
			file_size = document.data['file_size']

			if document.uid:
				UserStorage.objects(pk=document.uid).update_one(inc__upload_bandwidth=file_size)
			if document.sid:
				ServerFileStorage.objects(pk=document.sid).update_one(inc__upload_bandwidth=file_size)

		elif document.status == SessionStatus.completed and document.type == SessionType.download:
			# download complete
			if 'file_size' not in document.data:
				logging.error(u'DownloadSession.data not contain file_size')
				return
			file_size = document.data['file_size']

			if document.uid:
				UserStorage.objects(pk=document.uid).update_one(inc__download_bandwidth=file_size)
			if document.sid:
				ServerFileStorage.objects(pk=document.sid).update_one(inc__download_bandwidth=file_size)

signals.post_save.connect(postSaveSession, sender=Session)


class UserStorage(mongoengine.Document):
	user_id = mongoengine.IntField(primary_key=True)
	file_count = mongoengine.IntField(required=True, default=0)  # number of UserFile is in storage
	folder_count = mongoengine.IntField(required=True, default=0)  # number of UserFile is in storage
	storage_used = mongoengine.LongField(required=True, default=0)  # total sum UserFile.file_size is in storage

	download_bandwidth = mongoengine.LongField(required=True, default=0)
	upload_bandwidth = mongoengine.LongField(required=True, default=0)

	calculated_date = mongoengine.DateTimeField(required=True, default=timezone.now)

	def __unicode__(self): return "%s (%s files %s folders)" % (self.user_id, self.file_count, self.folder_count)


class ServerFileStorage(mongoengine.Document):
	serverFile_id = mongoengine.IntField(primary_key=True)
	file_count = mongoengine.IntField(required=True, default=0)  # number of RealFile is in storage
	storage_used = mongoengine.LongField(required=True, default=0)  # total sum RealFile.file_size is in storage

	download_bandwidth = mongoengine.LongField(required=True, default=0)
	upload_bandwidth = mongoengine.LongField(required=True, default=0)

	calculated_date = mongoengine.DateTimeField(required=True, default=timezone.now)
	waiting_delete_session_count = mongoengine.IntField(required=True, default=0)  # number of delete session awaiting for process

	def __unicode__(self): return "%s (%s files)" % (self.serverFile_id, self.file_count)





