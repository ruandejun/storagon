#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  BalanceController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from django.db import IntegrityError, transaction
from servermain.models import AccountBalance, TransactionLog
from storagon.tool import *
from storagon.enum import *


def chargeBalance(balance_id, amount):
	""" Increase of decrease balance
	Remember to do this in a SQL transaction
	"""
	try:
		with transaction.atomic():
			balance = AccountBalance.objects.get(pk=balance_id)
			balance.amount += amount
			if balance.amount < 0:
				raise Exception(u"Insufficient during transaction")
			else:
				balance.save()
	except Exception as e:
		logging.warning(u"BalanceController.chargeBalance: failed with error=%s, balance_id=%s, amount=%s" % (str(e), balance_id, amount))
		return False
	return True


def transferBalance(from_balance_id, to_balance_id, withdraw_amount, deposit_amount):
	""" Transfer money from one balance to another
	Remember to do this in a SQL transaction
	"""
	try:
		with transaction.atomic():
			if withdraw_amount <= 0:
				raise Exception(u"BalanceController.transferBalance: amount must >0")
			from_balance = AccountBalance.objects.get(pk=from_balance_id)
			to_balance = AccountBalance.objects.get(pk=to_balance_id)

			from_balance.amount -= withdraw_amount
			if from_balance.amount < 0:
				raise Exception(u"Insufficient during transaction")
			else:
				from_balance.save()

			to_balance.amount += deposit_amount
			to_balance.save()

	except Exception as e:
		logging.warning(u"BalanceController.transferBalance: failed with error=%s, from_balance_id=%s, to_balance_id=%s" % (str(e), from_balance_id, to_balance_id))
		return False

	return True


def revertTransaction(transactionList,detail=None):
	count=0;
	for transactionLog in transactionList:
		if transactionLog.transaction_status == TransactionStatus.auto and transactionLog.balance and transactionLog.amount != 0:
			if chargeBalance(transactionLog.balance.id, -transactionLog.amount):
				revertTransactionLog = TransactionLog();
				revertTransactionLog.transaction_type = transactionLog.transaction_type
				revertTransactionLog.balance = transactionLog.balance
				revertTransactionLog.invoice_bill = transactionLog.invoice_bill
				revertTransactionLog.amount = -transactionLog.amount
				revertTransactionLog.transaction_status = TransactionStatus.revert
				if detail:
					revertTransactionLog.data = json.dumps({
						'detail': detail
					});
				revertTransactionLog.save();
				count+=1;
	return count