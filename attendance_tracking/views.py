#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  views
#  
#
#  Created by TVA on 3/17/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
import json, pytz
from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from models import AttendanceLog
from django.utils import timezone
from models import AttendanceLog
import calendar

@permission_required(['attendance_tracking.submit_attendancelog'])
@login_required()
def submitAttendance(request):
	if request.method == 'GET':
		return shortcuts.render_to_response('attendance_track_template/submitAttendance.html', {
			'root_path': reverse('admin:index'),
		}, context_instance=RequestContext(request))
	elif request.method == 'POST':
		device_id = request.POST.get('device_id');
		note = request.POST.get('note', '');
		if not device_id:
			return HttpResponseForbidden();
		if request.META['REMOTE_ADDR'] not in settings.ATTENDANCE_TRACK_ALLOW_IP_LIST:
			return HttpResponseForbidden();

		attLog = AttendanceLog(user=request.user);
		attLog.device_id = device_id;
		attLog.ip_address = request.META['REMOTE_ADDR'];
		attLog.note = note;

		lastAttLog=request.user.attendancelog_set.all().reverse().first();
		if lastAttLog and lastAttLog.created_date + timezone.timedelta(seconds=settings.ATTENDANCE_TRACK_TIME_BETWEEN_SUBMIT) > timezone.now():
			print "Dont save due to lastAttLog.created_date = %s"%(lastAttLog.created_date)
		else:
			attLog.save(); #dont saved multiple attendance during ATTENDANCE_TRACK_TIME_BETWEEN_SUBMIT

		return HttpResponse();
	else:
		return Http404();

@permission_required(['attendance_tracking.submit_attendancelog']) #, 'attendance_tracking.view_attendancelog'
@login_required()
def checkAttendance(request):
	if request.method == 'GET':
		username = request.GET.get('username');
		device_id = request.GET.get('device_id');
		tzname = request.GET.get('tzname', timezone.get_default_timezone_name());

		now=timezone.now();

		to_date_string = request.GET.get('to_date');
		if to_date_string:
			try:
				to_date = timezone.datetime.strptime(to_date_string, "%Y-%m-%d");
			except ValueError:
				to_date = now;
		else:
			to_date = now;

		month_range = calendar.monthrange(to_date.year, to_date.month);

		if to_date is not now:
			to_date = timezone.datetime(year=to_date.year, month=to_date.month, day=month_range[1], hour=23, minute=59, second=59);

		if not username or request.user.has_perm('attendance_tracking.view_attendancelog') is False:
			username=request.user.username;

		# start_date = timezone.datetime(year=year, month=month, day=1);
		from_date = timezone.datetime(year=to_date.year, month=to_date.month, day=1);
		# print start_date, now;

		attLogQuery = AttendanceLog.objects.all().filter(user__username=username);
		attLogQuery = attLogQuery.filter(created_date__gt=from_date, created_date__lt=to_date);

		postProcessData=[];
		rawData=[];
		noteDict = {}
		deviceIDList = [];
		for log in attLogQuery:
			if log.device_id not in deviceIDList:
				deviceIDList.append(log.device_id);

			if device_id:
				if log.device_id != device_id: continue;#skip other deviceID

			localTime = timezone.localtime(log.created_date, timezone=pytz.timezone(tzname))
			postProcessData.append([localTime.day, localTime.hour, localTime.minute]);
			noteDict[localTime.day] = log.note.replace(r'\n','<br/>');
			rawData.append([localTime.strftime('%Y-%m-%dT%H:%M:%S'),log.note.strip().replace(r'\n','<br/>')]);

		# print postProcessData;
		return shortcuts.render_to_response('attendance_track_template/checkAttendance.html', {
			'root_path': reverse('admin:index'),
			'month': to_date.month,
			'year': to_date.year,
			'to_date': to_date_string,
			'first_week_day': month_range[0],
			'last_month_day': month_range[1],
			'postProcessData': postProcessData,
			'rawData': json.dumps(rawData),
			'noteDictJSON': json.dumps(noteDict),
			'deviceIDList': deviceIDList,
			'device_id': device_id,
			'tzname': tzname,
			'username': username,
		}, context_instance=RequestContext(request))
	elif request.method == 'POST':
		return Http404();
	else:
		return Http404();