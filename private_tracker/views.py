#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  views.py
#  
#
#  Created by TVA on 5/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import urllib2, urllib, bencode, re

from django.conf import settings;
from django import shortcuts
from django.http import *
from django.utils import timezone
from django.db.models import F

from servermain.models import UserFile
from servermain.mongo_models import Session
from storagon.enum import *
from system_configure.controllers.Tool import *


def announce(request):
	if request.method == 'GET':
		ip=request.META['REMOTE_ADDR'];
		session_id,event,downloaded,uploaded,left = getParamsOr400(request,'session_id', ('event',''), ('downloaded',0),('uploaded',0),('left',0));
		#fix stupid torrent client bug
		if '?' in session_id:
			stupid_param = session_id;
			session_id = stupid_param.split('?')[0]

		try:
			session = getObjectOrNone(Session,3600,id=session_id);
		except Exception as e:
			session = None;

		if event=='started':
			#mark session as working
			if session and session.status == SessionStatus.waiting:
				session.status = SessionStatus.working;
				session.save();
				try: cache.delete(session._cacheKey);
				except AttributeError: pass;
		elif event=='completed':
			#mark session as completed
			if session and session.status != SessionStatus.completed:
				session.status = SessionStatus.completed;
				session.save();
				try: cache.delete(session._cacheKey);
				except AttributeError: pass;
				UserFile.objects.all().filter(id=session.fid).update(download_count=F('download_count')+1, last_download_date=timezone.now());
		elif left==0 and uploaded>0:
			#track seeding torrent_uploaded of this session
			if session and session.status == SessionStatus.completed and session.data.get('uploaded',0) < uploaded:
				session.data['uploaded'] = uploaded;
				session.text='seeding';
				session.save();
				try: cache.delete(session._cacheKey);
				except AttributeError: pass;

		m = re.search(r'/announce\?(.+)',request.get_full_path())
		if not m: return HttpResponseBadRequest();

		param_str = m.group(1).replace('?','&');#fix stupid torrent client
		param_str +='&ip=%s'%ip;

		url = settings.OPEN_TRACKER_ANNOUNCE_URL+'?'+ param_str;
		logging.debug(u"Announce RequestURL: %s"%url)
		request = urllib2.Request(url);
		try:
			response = urllib2.urlopen(request)
			response_body = response.read()
			status = response.getcode()
		except urllib2.HTTPError, e:
			response_body = e.read()
			status = e.code
			logging.error(u"Announce Error %s: %s"%(e.code,response_body))
			return HttpResponse(response_body, status=status)
		else:
			# logging.debug(u"Announce Response Decode: %s"%bencode.bdecode(response_body));
			return HttpResponse(response_body, status=status, content_type=response.headers['content-type'])
	else:
		raise Http404()


def scrape(request):
	if request.method == 'GET':
		if not settings.PRIVATE_TRACKER_ENABLE_SCRAPE:return HttpResponseNotFound();
		params = request.GET.copy();

		param_str = request.get_full_path()
		param_str = param_str.replace('/scrape?','');

		url = settings.OPEN_TRACKER_SCRAPE_URL+'?'+ param_str;
		logging.debug("Announce RequestURL: %s"%url)
		request = urllib2.Request(url);
		try:
			response = urllib2.urlopen(request)
			response_body = response.read()
			status = response.getcode()
			logging.debug("Announce Response: %s"%response_body)
		except urllib2.HTTPError, e:
			response_body = e.read()
			status = e.code
			logging.error("Announce Error %s: %s"%(e.code,response_body))
			return HttpResponse(response_body, status=status)
		else:
			return HttpResponse(response_body, status=status, content_type=response.headers['content-type'])
	else:
		raise Http404()
