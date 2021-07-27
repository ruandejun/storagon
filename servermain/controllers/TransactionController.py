#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  TransactionController.py
#  
#
#  Created by TVA on 6/5/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.db import IntegrityError, transaction
from servermain.models import AccountBalance, TransactionLog
from storagon.tool import *
from storagon.enum import *


def addTransactionLogByDate(date,balance,amount,transaction_type):
	try:
		with transaction.atomic():
			transactionLog, created = TransactionLog.objects.get_or_create(
				created_date__year=date.year,
				created_date__month=date.month,
				created_date__day=date.day,
				transaction_type=transaction_type,
				balance=balance,invoice_bill=None,
				defaults={
					'balance':balance,
					'invoice_bill':None,
					'amount': 0,
					'transaction_type': transaction_type,
					'data': json.dumps({'count':0})
				}
			);
			transactionLog.amount += amount
			data = json.loads(transactionLog.data)
			data['count']+=1;
			transactionLog.data = json.dumps(data);
			transactionLog.save();
	except Exception as e:
		logging.warning(u"Atomic transaction failed with error=%s, balance_id=%s, amount=%s" % (str(e), balance.id, amount))
		return False
	return True
