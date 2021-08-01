#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  StatisticsController.py
#  
#
#  Created by TVA on 6/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse

from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from servermain.mongo_models import Session
from django.db import connection


def countSessionByDayOfFileOwnerUser(user_id, session_type,session_status,from_date,to_date):
	countSessionResult = Session._get_collection().aggregate([
			{ '$match' : {
				'type': session_type,
				'status': session_status,
				'created': { '$gt': from_date, '$lt': to_date },
				'oid': user_id
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

	countSessionResult = list(countSessionResult)
	print('countSessionResult===',countSessionResult)
	return countSessionResult['result'];


def countAndSumTransactionByDayOfUser(user_id, transaction_type, from_date,to_date):
	to_date += timezone.timedelta(days=1);
	cursor = connection.cursor();
	try:
		cursor.execute("""
			SELECT DATE(tlog.created_date) as d, COUNT(tlog.id) as count_id, SUM(tlog.amount) as sum_amount FROM servermain_transactionlog as tlog
			JOIN servermain_accountbalance as balance ON balance.id = tlog.balance_id
			WHERE tlog.created_date BETWEEN %s AND %s AND balance.user_id = %s AND tlog.transaction_type = %s
			GROUP BY d
			;""", [from_date,to_date,user_id,transaction_type])
		raw_result = cursor.fetchall();
	except:
		raw_result = []
	finally:
		cursor.close()

	return raw_result