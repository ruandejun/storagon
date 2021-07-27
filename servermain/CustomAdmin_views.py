#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  custom_admin_view
#
#
#  Created by TVA on 12/16/14.
#  Copyright (c) 2014 storagon. All rights reserved.
#

import datetime
import ast
import re
import calendar

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django import forms
from suit.widgets import SuitSplitDateTimeWidget
from django.utils import timezone
from django.utils.html import escape
from django.db import connection
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers

from servermain.controllers import PaymentController
from storagon.PrivateAPI_SDK import SignalSDK
from models import User, ServerFile
from mongo_models import Session
from storagon.enum import *
from storagon.tool import *
from system_configure.controllers import SystemConfigureController


@staff_member_required
def customAdminTest(request):
	return shortcuts.render_to_response('custom_admin_site/custom_site_example.html', {
		'root_path': reverse('admin:index'),
	}, context_instance=RequestContext(request))


@staff_member_required
def userFileUpload(request):
	return shortcuts.render_to_response('custom_admin_site/userFile_upload.html', {
		'root_path': reverse('admin:index'),
	}, context_instance=RequestContext(request))


# Mongo Session CRUD
class SessionFilterForm(forms.Form):
	session_id = forms.CharField(required=False, max_length=24, min_length=24)  # 24 is fixed length of MongoDB ObjectID
	type = forms.TypedChoiceField(required=True, coerce=int, choices=SessionType.ChoiceList(), initial=SessionType.upload)
	status = forms.TypedChoiceField(required=False, coerce=int, choices=[(None, '---')] + SessionStatus.ChoiceList())
	from_date = forms.SplitDateTimeField(required=False, widget=SuitSplitDateTimeWidget, initial=datetime.datetime.today() - datetime.timedelta(days=30))
	to_date = forms.SplitDateTimeField(required=False, widget=SuitSplitDateTimeWidget)
	offset = forms.IntegerField(required=True, initial=0)
	limit = forms.IntegerField(required=True, min_value=1, initial=25)


@permission_required(['sessions.change_session'])
@staff_member_required
def mongoListSessionView(request):
	has_delete_permission = request.user.has_perm('sessions.delete_session')
	if request.method == 'GET':
		if len(request.GET) > 0:
			form = SessionFilterForm(request.GET)
		else:
			form = SessionFilterForm()

		query = Session.objects.all()
		# totalCount=Session.objects.all().count();
		result_headers_dict = {
		'id': {'class_attrib': '', 'sortable': False, 'text': 'Session_ID'},
		'type': {'class_attrib': '', 'sortable': False, 'text': 'Type'},
		'status': {'class_attrib': '', 'sortable': False, 'text': 'Status'},
		'created': {'class_attrib': '', 'sortable': False, 'text': 'Created'},

		'uid': {'class_attrib': '', 'sortable': False, 'text': 'User_ID'},
		'fid': {'class_attrib': '', 'sortable': False, 'text': 'File_ID'},
		'ufid': {'class_attrib': '', 'sortable': False, 'text': 'UserFile_ID'},
		'rfid': {'class_attrib': '', 'sortable': False, 'text': 'RealFile_ID'},

		'sid': {'class_attrib': '', 'sortable': False, 'text': 'Server_ID'},
		'usid': {'class_attrib': '', 'sortable': False, 'text': 'To_User_ID'},
		'bid': {'class_attrib': '', 'sortable': False, 'text': 'Bill_ID'},

		'data': {'class_attrib': '', 'sortable': False, 'text': 'Data'},
		'text': {'class_attrib': '', 'sortable': False, 'text': 'Text'},
		}

		def statusHTML_label(s):
			value = SessionStatus.AllLabelList()[s.status]
			if s.status == SessionStatus.waiting:
				html = u'<span class="label label-info">%s</span>' % value
			elif s.status == SessionStatus.working:
				html = u'<span class="label label-warning">%s</span>' % value
			elif s.status == SessionStatus.completed:
				html = u'<span class="label label-success">%s</span>' % value
			elif s.status == SessionStatus.failed:
				html = u'<span class="label label-important">%s</span>' % value
			else:
				html = u'<span class="label">%s</span>' % value
			return html

		value_eval_dict = {
		'id': lambda s: s.id,
		'type': lambda s: SessionType.AllLabelList()[s.type],
		#'status':	lambda s:SessionStatus.AllLabelList()[s.status] ,
		'status': statusHTML_label,
		'created': lambda s: s.created,

		#'uid':		lambda s:s.uid ,
		'uid': lambda s: u'<a href="%s"><span class="badge badge-info">%s</span></a>' % (reverse('admin:servermain_userprofile_change', args=[s.uid]), s.uid),

		'fid': lambda s: s.fid,
		'ufid': lambda s: u'<a href="%s"><span class="badge badge-warning">%s</span></a>' % (reverse('admin:servermain_userfile_change', args=[s.fid]), s.fid),
		'rfid': lambda s: u'<a href="%s"><span class="badge badge-warning">%s</span></a>' % (reverse('admin:servermain_realfile_change', args=[s.fid]), s.fid),

		'sid': lambda s: u'<a href="%s"><span class="badge">%s</span></a>' % (reverse('admin:servermain_serverfile_change', args=[s.sid]), s.sid),
		# its User.id but using session.sid field to store
		'usid': lambda s: u'<a href="%s"><span class="badge badge-info">%s</span></a>' % (reverse('admin:servermain_userprofile_change', args=[s.sid]), s.sid),
		# its Bill.id but using session.sid field to store
		'bid': lambda s: u'<a href="%s"><span class="badge badge-sucess">%s</span></a>' % (reverse('admin:servermain_bill_change', args=[s.sid]), s.sid),

		'data': lambda s: escape(s.data),
		'text': lambda s: escape(s.text),
		}

		if form.is_valid():
			fd = form.cleaned_data
			if fd['type'] == SessionType.upload:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'sid', 'data']
			elif fd['type'] == SessionType.download:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'ufid', 'sid', 'data']
			elif fd['type'] == SessionType.bill:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'bid', 'data', 'text']
			elif fd['type'] == SessionType.delete:
				propertyList = ['id', 'type', 'status', 'created', 'rfid', 'sid', 'text']
			elif fd['type'] == SessionType.report:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'ufid', 'usid', 'data', 'text']
			elif fd['type'] == SessionType.inbox:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'usid', 'text']
			elif fd['type'] == SessionType.move:
				propertyList = ['id', 'type', 'status', 'created', 'rfid', 'sid', 'data']
			else:
				propertyList = ['id', 'type', 'status', 'created', 'uid', 'fid', 'sid', 'data', 'text']

			if fd.get('session_id'):
				query = query.filter(id=fd.get('session_id'))
			else:
				query = query.filter(type=fd['type'])
				if fd['type'] == SessionType.bill and not request.user.has_perm('servermain.change_bill'):  # check permission for bill session
					raise PermissionDenied()

				if fd.get('status') or fd.get('status') == 0:
					query = query.filter(status=fd['status'])
				if fd.get('from_date'):
					query = query.filter(created__gt=fd['from_date'])
				if fd.get('to_date'):
					query = query.filter(created__lt=fd['to_date'])

			query = query.order_by('-created')
			filter_count = query.count()
			resultList = query[fd['offset']:fd['offset'] + fd['limit']]
			offset = form.cleaned_data['offset']
			limit = form.cleaned_data['limit']
		else:
			propertyList = ['id', 'type', 'status', 'created', 'uid', 'sid', 'data']
			query = query.filter(type=SessionType.upload)
			query = query.order_by('-created')
			filter_count = query.count()
			resultList = query[:25]
			offset = 0
			limit = 25

		# retrive header into result_headers
		result_headers = []
		for property in propertyList:
			result_headers += [result_headers_dict[property]]

		# retrive value into results
		results = []
		for s in resultList:
			result_values = []
			for property in propertyList:
				result_values += [value_eval_dict[property](s)]
			results.append(result_values)
		if len(results) == 0:
			results.append(['N/a'] * len(propertyList))

		page_range = filter_count / limit
		if page_range <= 10:
			page_range = [(limit * i, i + 1) for i in range(page_range)]
		else:
			page_range = [(limit * i, i + 1) for i in range(7)]\
					   	+ [(-1, '...')]\
					   	+ [(offset + limit, 'next')]\
						+ [(-1, '...')]\
					   	+ [(limit * i, i + 1) for i in range(page_range - 2, page_range)]

		# use for clickable paging
		page_url = re.sub(r'&offset=\d+', '', request.get_full_path())
		if '?' not in page_url:
			page_url += '?type=%s&limit=%s' % (SessionType.upload, limit)

		show_all_url = re.sub(r'&limit=\d+', '', page_url) + '&offset=0&limit=%s' % (filter_count)

		return shortcuts.render_to_response('custom_admin_site/mongo_session/change_list_results.html', {
		'root_path': reverse('admin:index'),
		'result_headers': result_headers,
		'results': results,
		'form': form,
		'has_add_permission': has_delete_permission,
		'filter_count': filter_count,
		'offset': offset,
		'limit': limit,
		'page_range': page_range,
		'page_url': page_url,
		'show_all_url': show_all_url,
		}, context_instance=RequestContext(request))
	elif request.method == 'POST':
		session_id_list, action = getParamsOr400(request, ('_selected_action', []), 'action')

		if action == 'delete_selected':
			if not has_delete_permission:
				raise PermissionDenied()
			try:
				result = Session.objects.filter(id__in=session_id_list).delete()
			except Exception as e:
				return errorResponse(u"mongoListSessionView.deleteSession: Bulk update failed with error=%s" % (e))
			return shortcuts.redirect(request.get_full_path())
		else:
			return HttpResponseBadRequest(u"Unknow post action")
	else:
		raise Http404()


class SessionEditForm(forms.Form):
	# session_id = forms.CharField(max_length=24,min_length=24,required=False);#24 is fixed length of MongoDB ObjectID
	type = forms.TypedChoiceField(required=True, coerce=int, choices=SessionType.ChoiceList())

	uid = forms.ModelChoiceField(required=False, queryset=User.objects.all(), empty_label="None")
	# uid = forms.IntegerField(required=False);#user_id
	fid = forms.IntegerField(required=False)  # file_id UserFile and RealFile or folder_id
	sid = forms.IntegerField(required=False)  # server_id or bill_id
	status = forms.TypedChoiceField(required=True, coerce=int, initial=SessionStatus.waiting, choices=SessionStatus.ChoiceList())

	data = forms.CharField(required=True, initial='{}', widget=forms.Textarea)
	text = forms.CharField(required=False)  # text for query on string
	created = forms.SplitDateTimeField(required=True, initial=timezone.now, widget=SuitSplitDateTimeWidget)


@permission_required(['sessions.change_session'])
@staff_member_required
def mongoEditSessionView(request, session_id):
	has_delete_permission = request.user.has_perm('sessions.delete_session')
	if request.method == 'GET':
		if session_id == 'add':
			if not request.user.has_perm('sessions.add_session'):
				raise PermissionDenied()
			form = SessionEditForm()
		else:
			try:
				session = Session.objects.get(id=session_id)
			except:
				raise Http404()
			form = SessionEditForm(initial={
				'type': session.type,
				'uid': session.uid,
				'fid': session.fid,
				'sid': session.sid,
				'status': session.status,
				'data': str(session.data),
				'text': session.text,
				'created': session.created,
			})
		return shortcuts.render_to_response('custom_admin_site/mongo_session/change_form.html', {
			'root_path': reverse('admin:index'),
			'form': form,
			'has_delete_permission': has_delete_permission,
		}, context_instance=RequestContext(request))
	elif request.method == 'POST':
		form = SessionEditForm(request.POST)

		if form.is_valid():
			fd = form.cleaned_data
			if fd['type'] == SessionType.bill and not request.user.has_perm('servermain.add_bill'):
				raise PermissionDenied()  # check permission for bill session
			# convert form data to corresponding mongo type
			for key, value in fd.items():
				if key == 'data':
					fd[key] = ast.literal_eval(value)  # convert string to dict safely
				elif key == 'created':
					# fd[key]=timezone.make_aware(value,timezone.get_current_timezone());
					fd[key] = timezone.make_naive(value, timezone.get_current_timezone())
				elif key == 'uid':
					if value is not None:
						fd[key] = value.id  # this value is User model object not id
			if session_id == 'add' or '_saveasnew' in request.POST:
				if not request.user.has_perm('sessions.add_session'):
					raise PermissionDenied()
				session = Session()  # new session
			else:  # edit session
				try:
					session = Session.objects.get(id=session_id)
				except:
					raise Http404()

			for key, value in fd.items():
				setattr(session, key, value)  # set atribute
			session.save()
			# route to correct path with each button
			if '_save' in request.POST:
				return shortcuts.redirect(reverse('CustomAdmin:mongoListSessionView') + '?type=%s&status=%s&offset=0&limit=25' % (session.type, session.status))
			elif '_saveasnew' in request.POST:
				return shortcuts.redirect(reverse('CustomAdmin:mongoEditSessionView', args=(session.id,)))
			elif '_addanother' in request.POST:
				return shortcuts.redirect(reverse('CustomAdmin:mongoEditSessionView', args=('add',)))
			elif '_continue' in request.POST:
				return shortcuts.redirect(reverse('CustomAdmin:mongoEditSessionView', args=(session.id,)))
			else:
				return HttpResponseBadRequest(u"Unknow post action")

		# display not valid form error
		return shortcuts.render_to_response('custom_admin_site/mongo_session/change_form.html', {
			'root_path': reverse('admin:index'),
			'form': form,
			'has_delete_permission': has_delete_permission,
		}, context_instance=RequestContext(request))
	else:
		raise Http404()


@permission_required(['sessions.delete_session'])
@staff_member_required
def mongoDeleteSessionView(request, session_id):
	try:
		session = Session.objects.get(id=session_id)
		session.delete()
	except:
		raise Http404()
	return shortcuts.redirect(reverse('CustomAdmin:mongoListSessionView') + '?type=%s&status=%s&offset=0&limit=25' % (session.type, session.status))

# tool


class SendServerFileSignalForm(forms.Form):

	signal = forms.ChoiceField(required=True, choices=[
		('initiateDeleteSessionProcess', 'initiateDeleteSessionProcess'),
		('initiateMoveSessionProcess', 'initiateMoveSessionProcess'),
		('initiateClearTemporaryFolderProcess', 'initiateClearTemporaryFolderProcess'),
	])

	serverFile = forms.ModelChoiceField(required=True, queryset=ServerFile.objects.all())
	# initiate Delete/Move SessionProcess
	maxFile = forms.TypedChoiceField(required=False, coerce=int, choices=[(x, x) for x in range(100, 900, 100)])
	retry = forms.ChoiceField(required=False, choices=[('waiting', 'waiting'), ('failed', 'failed'), ('working', 'working')])


@staff_member_required
def sendServerFileSignal(request):
	serverFileList = ServerFile.objects.all()
	if request.method == 'GET':
		form = SendServerFileSignalForm()
		return shortcuts.render_to_response('custom_admin_site/send_serverfile_signal.html', {
			'root_path': reverse('admin:index'),
			'form': form,
		}, context_instance=RequestContext(request))
	if request.method == 'POST':
		form = SendServerFileSignalForm(request.POST)
		result = ''
		if form.is_valid():
			fd = form.cleaned_data
			serverFile = fd['serverFile']
			print u"Send signal to %s =" % serverFile.server_address,
			signalSDK = SignalSDK(serverFile.server_address)
			if fd['signal'] == 'initiateDeleteSessionProcess':
				# print u'initiateDeleteSessionProcess'
				try:
					result = signalSDK.initiateDeleteSessionProcess(fd.get('maxFile', 100), fd.get('retry'))
				except Exception as e:
					logging.error(u"initiateDeleteSessionProcess -> Unable to send delete signal to serverFile with error=%s" % (e))
					result = str(e);

			if fd['signal'] == 'initiateMoveSessionProcess':
				# print u'initiateMoveSessionProcess'
				try:
					result = signalSDK.initiateMoveSessionProcess(fd.get('maxFile', 100), fd.get('retry'))
				except Exception as e:
					logging.error(u"initiateMoveSessionProcess -> Unable to send move signal to serverFile with error=%s" % (e))
					result = str(e);

			if fd['signal'] == 'initiateClearTemporaryFolderProcess':
				# print u'initiateClearTemporaryFolderProcess'
				try:
					result = signalSDK.initiateClearTemporaryFolderProcess();
				except Exception as e:
					logging.error(u"initiateClearTemporaryFolderProcess -> Unable to send clearTemporaryFolder signal to serverFile with error=%s" % (e))
					result = str(e);

		return shortcuts.render_to_response('custom_admin_site/send_serverfile_signal.html', {
			'root_path': reverse('admin:index'),
			'form': form,
			'result': str(result),
		}, context_instance=RequestContext(request))
	else:
		raise Http404()


class VerifyBillForm(forms.Form):
	session_id = forms.CharField(required=False, max_length=24, min_length=24)  # 24 is fixed length of MongoDB ObjectID

	billSession = forms.ModelChoiceField(required=False, queryset=Session.objects.all().filter(
		type=SessionType.bill, status=SessionStatus.waiting
	), empty_label="None")


@permission_required(['servermain.add_bill'])
@staff_member_required
def verifyBillManual(request):
	paygate_id_list = SystemConfigureController.getConfigure('paygateIDList', [1])
	paygateConfigDict = {}
	for paygate_id in paygate_id_list:
		paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (paygate_id), settings.DEFAULT_PAYGATE_CONFIG)
		paygateConfigDict[paygate_id] = paygateConfig

	if request.method == 'GET':
		form = VerifyBillForm()

		return shortcuts.render_to_response('custom_admin_site/verify_bill_manual.html', {
			'root_path': reverse('admin:index'),
			'form': form,
			'paygateConfigDict': paygateConfigDict,
		}, context_instance=RequestContext(request))
	if request.method == 'POST':
		form = VerifyBillForm(request.POST)
		result = ''

		if form.is_valid():
			fd = form.cleaned_data
			if fd.get('session_id'):
				bill_session_id = fd['session_id']
			elif fd.get('billSession'):
				bill_session_id = str(fd['billSession'].id)
			resultHandle = PaymentController.paygateCallBackHandler(request, bill_session_id)
			if resultHandle:
				result = u'Success verify bill with result=%s' % (str(resultHandle))

		return shortcuts.render_to_response('custom_admin_site/verify_bill_manual.html', {
			'root_path': reverse('admin:index'),
			'form': form,
			'paygateConfigDict': paygateConfigDict,
			'result': result,
		}, context_instance=RequestContext(request))
	else:
		raise Http404()


def showUserStatistic(request):
	""" Count user statistic.

	:param request:
	:return:
	"""
	if request.method == 'GET':
		now = timezone.now();
		try:
			month = int(request.GET.get('m', now.month));
			year = int(request.GET.get('y', now.year));
		except:
			return HttpResponseBadRequest();

		month_range = calendar.monthrange(year, month);
		monthBegin = timezone.datetime(year, month, 1);
		nextMonthBegin = timezone.datetime(year, month+1, 1);

		cursor = connection.cursor();
		try:
			cursor.execute("""
				SELECT DATE(date_joined) as d, COUNT(id) as count_id FROM auth_user
				WHERE date_joined BETWEEN %s AND %s
				GROUP BY d
				;""", [monthBegin,nextMonthBegin])
			raw_result = cursor.fetchall();
		finally:
			cursor.close()

		new_user_count_by_date = [[str(date), count] for date, count in raw_result]

		return shortcuts.render_to_response('custom_admin_site/user_statistic_chart.html', {
			'root_path': reverse('admin:index'),
			'new_user_count_by_date': json.dumps(new_user_count_by_date),
		}, context_instance=RequestContext(request))
	else:
		raise Http404()



class ServerFileSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServerFile

def showSessionStatistic(request):
	""" Count user statistic.

	:param request:
	:return:
	"""
	if request.method == 'GET':
		now=timezone.now();
		try:
			month = int(request.GET.get('m', now.month));
			year = int(request.GET.get('y', now.year));
		except:
			return HttpResponseBadRequest();

		month_range = calendar.monthrange(year, month);
		monthBegin = timezone.datetime(now.year, now.month, 1);

		uploadSessionResult = Session._get_collection().aggregate([
				{ '$match' : {
					'type': SessionType.upload,
					'status': SessionStatus.completed,
					'created': { '$gt': monthBegin, '$lt': now }
					}},
				{ '$group' : {
					'_id': {
							'year': { '$year': "$created" },
							'month': { '$month': "$created" },
							'day': { '$dayOfMonth': "$created" } #,'sid': "$sid"
							},
					'count' : { '$sum' : 1 },
					'sum_bandwidth' : { '$sum' : "$data.file_size" }
					}} ,
				{ '$sort' : {"_id": 1}},
			  ]
		);

		downloadSessionResult = Session._get_collection().aggregate([
				{ '$match' : {
					'type': SessionType.download,
					'status': SessionStatus.completed,
					'created': { '$gt': monthBegin, '$lt': now }
					}},
				{ '$group' : {
					'_id': {
							'year': { '$year': "$created" },
							'month': { '$month': "$created" },
							'day': { '$dayOfMonth': "$created" } #,'sid': "$sid"
							},
					'count' : { '$sum' : 1 },
					'sum_bandwidth' : { '$sum' : "$data.file_size" }
					}} ,
				{ '$sort' : {"_id": 1}},
			  ]
		);

		# uploadSession_count_by_date = [[str(date), count] for date, count in raw_result]

		serializer = ServerFileSerializer(ServerFile.objects.all(), many=True)
		serverFileJSONData = JSONRenderer().render(serializer.data)

		# print downloadSessionResult

		return shortcuts.render_to_response('custom_admin_site/session_statistic_chart.html', {
			'root_path': reverse('admin:index'),
			'uploadSessionResult': json.dumps(uploadSessionResult['result']),
			'downloadSessionResult': json.dumps(downloadSessionResult.get('result', [])),

			'month': month,
			'year': year,
			'first_week_day': month_range[0],
			'last_month_day': month_range[1],
			'serverFileJSONData': serverFileJSONData,
		}, context_instance=RequestContext(request))
	else:
		raise Http404()