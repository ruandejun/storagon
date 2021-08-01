#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  UserStatistics_ClientAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import datetime
import re

from django.http import *
from django.core import serializers
from django.utils import timezone

from servermain.mongo_models import UserStorage, Session
from servermain.models import TransactionLog
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import login_required_ajax, signature_test
from servermain.controllers import PaymentController
from system_configure.controllers import SystemConfigureController
from django.db import connection


@login_required_ajax()
@signature_test()
def getUserStorage(request):
	""" Get current user storage
	"""
	if request.method == 'GET':
		userStorage = UserStorage(user_id=int(request.user.pk)).modify(upsert=True,
                                      set__user_id=int(request.user.pk))

		return successResponse(userStorage.to_json(), encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def listBill(request):
	""" List all bill for buying Premium of current user

	request.GET={
		from_date: default = before 1 month
		to_date:
	}

	response = JSON List [
		{
		u'fields': {u'plan_id': 1, u'paygate_id': 1,
					u'detail': u'{"_id": {"$oid": "54881833df3a1a268573fb18"}, "type": 2, "uid": 1, "status": 0, "data": {"plan_id": 1, "website_origin": "haivl.com", "paygate_id": 1, "download_bandwidth": 0, "price": 1000, "expires": 2592000, "storage": 10737418240, "agency_id": 2, "download_speed": 0, "upload_bandwidth": 0}, "created": {"$date": 1418230435641}}',
					u'user': 1, u'created_date': u'2014-12-10T09:53:55.662Z', u'money_charged': 1000},
		u'model': u'servermain.bill',
		u'pk': 1
		}
	]

	"""
	if request.method == 'GET':
		#?from_date=2014-11-06&to_date=2014-12-06
		from_date_string, to_date_string = getParamsOr400(request, ('from_date', ''), ('to_date', ''))

		from_date = timezone.now() - datetime.timedelta(days=30)
		if from_date_string:
			try: from_date = datetime.datetime.strptime(from_date_string, "%Y-%m-%d")
			except ValueError: pass;

		if to_date_string:
			today = timezone.now()
			try: to_date = datetime.datetime.strptime(to_date_string, "%Y-%m-%d")
			except ValueError: to_date=today;
			if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
				to_date = today  # in case client send to_date=today
			data = serializers.serialize('json', request.user.bill_set.all().filter(created_date__gt=from_date, created_date__lt=to_date))
		else:
			data = serializers.serialize('json', request.user.bill_set.all().filter(created_date__gt=from_date))

		return successResponse(data, encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def listTransaction(request):
	""" List history transaction of current user

	request.GET={
		from_date: default = before 1 month
		to_date:
		transaction_type: Enum transaction_type
	}

	response = JSON List [

	]

	"""
	if request.method == 'GET':
		#?from_date=2014-11-06&to_date=2014-12-06
		from_date_string, to_date_string, transaction_type = getParamsOr400(request, ('from_date', ''), ('to_date', ''), ('transaction_type', None))

		from_date = timezone.now() - datetime.timedelta(days=30)
		if from_date_string:
			try: from_date = datetime.datetime.strptime(from_date_string, "%Y-%m-%d")
			except ValueError: pass;

		transactionQuery = TransactionLog.objects.all().filter(balance__user=request.user, created_date__gt=from_date).select_related('invoice_bill__money_charged')
		if to_date_string:
			today = timezone.now()
			try: to_date = datetime.datetime.strptime(to_date_string, "%Y-%m-%d")
			except ValueError: to_date=today;
			if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
				to_date = today  # in case client send to_date=today
			transactionQuery = transactionQuery.filter(created_date__lt=to_date)

		if transaction_type is not None:
			try:
				transaction_type = int(transaction_type)
			except ValueError as e:
				return HttpResponseBadRequest(str(e))
			transactionQuery = transactionQuery.filter(transaction_type=transaction_type)

		data = serializers.serialize('json', transactionQuery)
		data_bill = [];
		for t in transactionQuery:
			if t.invoice_bill:
				data_bill.append(t.invoice_bill.money_charged)
			else:
				data_bill.append(0)

		return successResponse({'transactionList': data, 'billChargedList': data_bill}, encode=True)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@signature_test()
def getPlanAndPaygateInfo(request):
	""" Get PlanAndPaygateInfo
	"""
	if request.method == 'GET':
		planIDList = SystemConfigureController.getConfigure('planIDList', [1])
		paygateIDList = SystemConfigureController.getConfigure('paygateIDList', [1])

		planConfigDict = {
			0: SystemConfigureController.getConfigure('plan0', settings.DEFAULT_PLAN_CONFIG)
		}
		for plan_id in planIDList:
			plan_config = SystemConfigureController.getConfigure('plan%s' % (plan_id), settings.DEFAULT_PLAN_CONFIG)
			planConfigDict[plan_id] = plan_config

		paygateConfigDict = {}
		for paygate_id in planIDList:
			config = SystemConfigureController.getConfigure('paygate%s' % (paygate_id), settings.DEFAULT_PAYGATE_CONFIG)
			paygateConfigDict[paygate_id] = config

		return successResponse({
			'planIDList': planIDList,
			'paygateIDList': paygateIDList,
			'planConfigDict': planConfigDict,
			'paygateConfigDict': paygateConfigDict,
		})
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@signature_test()
def getExchangePointRateInfo(request):
	""" Get ExchangePointRate Info

	:param request:
	:return:
	"""
	if request.method == 'GET':
		exchangePointRateDict = SystemConfigureController.getConfigure('exchangePointRate', settings.DEFAULT_EXCHANGE_POINT)

		return successResponse({
			'packs': [
				{'name': key, 'value': value} for key, value in exchangePointRateDict.items()
			],
		})
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@signature_test()
def exchangePoint(request):
	""" Exchange point to premium

	:param request:
	:return:
	"""
	if request.method == 'POST':
		pack = getParamsOr400(request, 'pack')
		m = re.search(r'^plan(\d+)$', pack)
		if m:
			plan_id = m.group(1)
			result = PaymentController.exchangePointToPlan(request, request.user.id, plan_id)
			if result:
				return successResponse()
			else:
				if result is None:
					return errorResponse(u"Your balance is Insuficient", code=0)
				else:
					return errorResponse(u"Something wrong during exchange!", code=1)
		return errorResponse(u"Invalid pack identifier", code=2)
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def downloadCountSessionStatistic(request):
	""" Return download Count Session Statistic

	:param request:
	:return:
	"""
	if request.method == 'GET':
		from_date_string, to_date_string = getParamsOr400(request, ('from_date', ''), ('to_date', ''))
		from_date = timezone.now() - timezone.timedelta(days=30)
		if from_date_string:
			try: from_date = datetime.datetime.strptime(from_date_string, "%Y-%m-%d")
			except ValueError: pass;

		today = timezone.now()
		if to_date_string:
			try: to_date = datetime.datetime.strptime(to_date_string, "%Y-%m-%d")
			except ValueError: to_date=today;
			if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
				to_date = today  # in case client send to_date=today
		else:
			to_date = today;

		downloadSessionResult = Session._get_collection().aggregate([
				{ '$match' : {
					'type': SessionType.download,
					'status': SessionStatus.completed,
					'created': { '$gt': from_date, '$lt': to_date },
					'oid': request.user.id
				}},
				{ '$group' : {
					'_id': {
							'year': { '$year': "$created" },
							'month': { '$month': "$created" },
							'day': { '$dayOfMonth': "$created" },
					},
					'count' : { '$sum' : 1 },
				}},
				{ '$sort' : {"_id": 1}},
			]
		);

		return successResponse(downloadSessionResult.get('result', []));
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def newUserOriginFromDownloadLinkStatistic(request):
	""" Return download Count Session Statistic

	:param request:
	:return:
	"""
	if request.method == 'GET':
		from_date_string, to_date_string = getParamsOr400(request, ('from_date', ''), ('to_date', ''))

		from_date = timezone.now() - timezone.timedelta(days=30)
		if from_date_string:
			try: from_date = datetime.datetime.strptime(from_date_string, "%Y-%m-%d")
			except ValueError: pass;

		today = timezone.now()
		if to_date_string:
			try: to_date = datetime.datetime.strptime(to_date_string, "%Y-%m-%d")
			except ValueError: to_date=today;
			if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
				to_date = today  # in case client send to_date=today
		else:
			to_date = today;

		cursor = connection.cursor();
		try:
			cursor.execute("""
				SELECT DATE(auser.date_joined) as d, COUNT(auser.id) as count_id FROM auth_user as auser
				JOIN servermain_userprofile as profile ON profile.user_id = auser.id
				WHERE auser.date_joined BETWEEN %s AND %s AND profile.referer2_id = %s
				GROUP BY d
				;""", [from_date,to_date,request.user.id])
			raw_result = cursor.fetchall();
		finally:
			cursor.close()

		new_user_count_by_date = [[str(date), count] for date, count in raw_result]

		return successResponse(new_user_count_by_date);
	else:
		raise Http404()
