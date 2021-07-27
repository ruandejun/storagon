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
	help='Scan traffic log for all completed session'

	def add_arguments(self,parser):
		pass;
		# parser.add_argument('poll_id',nargs='+',type=int)


	# def scanTrafficLogForCompletedSession(traffic_log_path, clear_log=True):
	def handle(self,*args,**options):
		""" Scan traffic log

		:return:
		"""
		traffic_log_path = settings.TRAFFIC_LOG_PATH
		clear_log=True
		completedSessionIDList=[];
		success=0;
		current = {}
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

				# get from current first
				session = current.get(settings.CACHE_MONGO_SESSION_PREFIX + session_id)
				if not session:
					# get from cache
					session = cache.get(settings.CACHE_MONGO_SESSION_PREFIX + session_id, None)

				#get from jwt token
				if not session:
					try:
						decodedSessionData = jwt.decode(session_JWT_data, settings.SECRET_KEY);
					except jwt.DecodeError as e:
						logging.error(u"Failed to decode JWT token");
					else:
						session = Session.from_json(json.dumps(decodedSessionData));
				if session.status == SessionStatus.completed:continue;
				total_bandwidth = session.data.get('total_bandwidth',0);

				body_bytes_sent = int(body_bytes_sent);
				session.data['total_bandwidth']=total_bandwidth+body_bytes_sent;

				if session.data['total_bandwidth'] >= session.data['file_size']*0.99:
					#mark this session as completed to prevent multiple download of same file.
					session.status = SessionStatus.completed;
					completedSessionIDList+=[session_id];

				current[settings.CACHE_MONGO_SESSION_PREFIX + session_id] = session
				cache.set(settings.CACHE_MONGO_SESSION_PREFIX + session_id, session, settings.MONGO_SESSION_EXPIRES);

		if len(completedSessionIDList):
			sessionSDK = SessionSDK(settings.SERVER_MAIN_URL)
			for ti in range(3):
				try:sessionSDK.doneSession(completedSessionIDList, SessionStatus.completed, SessionType.download);
				except:pass;
				else:break;
			else:
				msg_error = u"Unable to send request for marking completed download session."
				logging.error(msg_error);
				return msg_error;
			logging.info(u"Send request to marking completed download sessions success=%s"%(len(completedSessionIDList)));
			success+=len(completedSessionIDList)
		#clear log
		if clear_log: open(traffic_log_path, 'w').close();

		return 'success=%d'%success;