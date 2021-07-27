#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  calculatescore
#  
#
#  Created by TVA on 6/20/15.
#  Copyright (c) 2015 vietcomfund. All rights reserved.
#

from django.core.management.base import BaseCommand,CommandError

import os, fnmatch, re, datetime, jwt

from storagon.enum import *
from storagon.tool import *
from storagon.PrivateAPI_SDK import SessionSDK, FileSDK
from servermain.mongo_models import Session


class Command(BaseCommand):
	help='Scan tmp folder and clear'

	def add_arguments(self,parser):
		pass;
		# parser.add_argument('poll_id',nargs='+',type=int)

	def handle(self,*args,**options):
		""" Move file between serverFile (in worker)

		:param clearUploadedChunkDateTime: clear all chunk that have uploaded time before this
		:return:
		"""
		clearUploadedChunkExistSeconds=8*3600

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

		return 'deleted_count=%d'%count;