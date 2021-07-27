#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  AffiliateController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

from urlparse import urlparse
from django.utils import timezone
import json
from bunch import Bunch
import BalanceController
from servermain.mongo_models import Session
from servermain.models import AccountBalance, TransactionLog, UserProfile, UserFile, WebsiteAgency
from storagon.tool import *
from storagon.enum import *
from storagon.browser import Browser
from servermain.controllers import TransactionController
from system_configure.controllers import SystemConfigureController
from django.db import connection

def agencyBonus(agency_user_id, invoice_bill, website_origin='', rebill=False):
	try:
		agency_UserProfile = UserProfile.objects.get(user_id=agency_user_id)
	except Exception as e:
		logging.error(u"Unable to get agencyUser")
		return

	if agency_UserProfile.account_type not in [AccountType.affiliate,AccountType.affiliatePPD]:
		logging.debug(u"Do not grant bonus for non affiliate user");
		return 0;

	try:
		balance = AccountBalance.objects.get(user_id=agency_user_id, balance_type=BalanceType.credit)
	except Exception as e:
		logging.error(u"Unable to get AccountBalance with error=%s" % (e))
		return

	if rebill:
		agencyBonusPercent = SystemConfigureController.getConfigure('agencyBonusRebillPercent', 0.65)
	else:
		agencyBonusPercent = SystemConfigureController.getConfigure('agencyBonusPercent', 0.65)

	if agencyBonusPercent >= 1 or agencyBonusPercent < 0:
		logging.error(u"Invalid agencyBonusPercent")
		return
	amount = invoice_bill.money_charged * agencyBonusPercent

	if agency_UserProfile.account_type == AccountType.affiliatePPD: #bonus point when afffiliatePPD got PPS
		try:
			point_balance = AccountBalance.objects.get(user_id=agency_user_id, balance_type=BalanceType.point)
		except Exception as e:
			logging.error(u"Unable to get AccountBalance with error=%s" % (e))
			return
		if BalanceController.chargeBalance(point_balance.id, amount):
			logging.info(u"Success with amount=%s" % (amount))

		return; #dont bonus credit for affiliatePPD

	if BalanceController.chargeBalance(balance.id, amount):
		logging.info(u"Success with amount=%s" % (amount))
		if rebill: transactionLog = TransactionLog(transaction_type=TransactionType.rebill)
		else: transactionLog = TransactionLog(transaction_type=TransactionType.agency)
		transactionLog.balance = balance
		transactionLog.invoice_bill = invoice_bill
		transactionLog.amount = amount
		transactionLog.data = json.dumps({
			'userfile_id': invoice_bill.userFile_id,
			'website_origin':website_origin,
		});
		transactionLog.save()
		refererBonus(agency_user_id, invoice_bill); #referer
		return amount
	else:
		logging.error(u"Failed during transaction with agency_user_id=%s, amount=%s" % (agency_user_id, amount))


def refererBonus(agency_user_id, invoice_bill):
	if not agency_user_id:
		return
	try:
		agency_UserProfile = UserProfile.objects.get(user_id=agency_user_id)
	except Exception as e:
		logging.error(u"Unable to get agencyUser")
		return

	if not agency_UserProfile.referer:
		return
	referer_user_id = agency_UserProfile.referer_id

	if agency_UserProfile.referer.profile.account_type not in [AccountType.affiliate,AccountType.affiliatePPD]:
		logging.debug(u"Do not grant bonus for non affiliate user");
		return 0;

	try:
		balance = AccountBalance.objects.get(user_id=referer_user_id, balance_type=BalanceType.credit)
	except Exception as e:
		logging.error(u"Unable to get AccountBalance with error=%s" % (e))
		return

	refererBonusPercent = SystemConfigureController.getConfigure('refererBonusPercent', 0.05)
	if refererBonusPercent >= 1 or refererBonusPercent < 0:
		logging.error(u"Invalid refererBonusPercent")
		return
	agencyBonusPercent = SystemConfigureController.getConfigure('agencyBonusPercent', 0.65)
	# percent from the amount of agencyBonus
	amount = (invoice_bill.money_charged * agencyBonusPercent) * refererBonusPercent
	if BalanceController.chargeBalance(balance.id, amount):
		logging.info(u"Success with amount=%s" % (amount))
		transactionLog = TransactionLog(transaction_type=TransactionType.referer)
		transactionLog.balance = balance
		transactionLog.invoice_bill = invoice_bill
		transactionLog.amount = amount
		transactionLog.data = json.dumps({
			'agency_id': agency_user_id,
			'agency_username': agency_UserProfile.user.username
		});
		transactionLog.save()
		return amount
	else:
		logging.error(u"Failed during transaction with referer_user_id=%s, amount=%s" % (referer_user_id, amount))


def websiteBonus(website_origin, invoice_bill, rebill=False):
	if not website_origin:
		return
	try:
		website=WebsiteAgency.objects.get(website_domain=website_origin);
		website_userProfile = website.user.profile;
		# website_userProfile = UserProfile.objects.get(website_agency=website_origin)
	except Exception as e:
		logging.error(u"Unable to get UserProfile for website_origin=%s with error=%s" % (website_origin, e))
		return

	if website_userProfile.account_type not in [AccountType.affiliate,AccountType.affiliatePPD]:
		logging.debug(u"Do not grant bonus for non affiliate user");
		return 0;

	try:
		balance = AccountBalance.objects.get(user_id=website_userProfile.user_id, balance_type=BalanceType.credit)
	except Exception as e:
		logging.error(u"Unable to get AccountBalance with error=%s" % (e))
		return

	websiteBonusPercent = SystemConfigureController.getConfigure('websiteBonusPercent', 0.05)
	if websiteBonusPercent >= 1 or websiteBonusPercent < 0:
		logging.error(u"Invalid websiteBonusPercent")
		return

	amount = invoice_bill.money_charged * websiteBonusPercent
	if BalanceController.chargeBalance(balance.id, amount) == True:
		logging.info(u"Success with amount=%s" % (amount))
		transactionLog = TransactionLog(transaction_type=TransactionType.website)
		transactionLog.balance = balance
		transactionLog.invoice_bill = invoice_bill
		transactionLog.amount = amount
		transactionLog.data = json.dumps({
			'website_origin': website_origin
		});
		transactionLog.save()
		return amount
	else:
		logging.error(u"Failed during transaction with website_user_id=%s, amount=%s" % (website_userProfile.user_id, amount))


def payPerDownloadBonus(downloadSession):
	download_user_id, userFile_id, iso_code = downloadSession.uid, downloadSession.fid, downloadSession.data.get('iso_code')

	if download_user_id is not None:
		downloadSessionCount = Session.objects.filter(type=SessionType.download, status=SessionStatus.completed, uid=download_user_id, fid=userFile_id).count()
	else:
		downloadSessionCount = Session.objects.filter(type=SessionType.download, status=SessionStatus.completed, uid=None, fid=userFile_id,
													  data__ip_address=downloadSession.data.get('ip_address','')).count()
	if downloadSessionCount > 0:  # only bonus once per user per file (if user download the same file over and over, owner of this file will be bonused only one time)
		logging.debug(u"Only grant bonus once for userFile_id=%s due to downloadSessionCount already=%s" % (userFile_id, downloadSessionCount));
		return 0

	if download_user_id is not None:
		try:
			downloadUserProfile = UserProfile.objects.get(id=download_user_id)
		except UserFile.DoesNotExist:
			logging.error(u"download_user_id=%s DoesNotExist" % (download_user_id))
			return 0
		else:
			if downloadUserProfile.getPlanID() > 0:
				logging.debug(u"Do not grant bonus for premium user download_user_id=%s" % (download_user_id));
				return 0


	try:
		userFile = UserFile.objects.get(id=userFile_id)
	except UserFile.DoesNotExist:
		logging.error(u"UserFile_id=%s DoesNotExist" % (userFile_id))
		return 0

	if userFile.user.profile.account_type not in [AccountType.affiliate,AccountType.affiliatePPD]:
		logging.debug(u"Do not grant bonus for non affiliate user");
		return 0;

	if userFile.user.id == download_user_id:
		logging.debug(u"Do not grant bonus for him self for userFile_id=%s" % (userFile_id));
		return 0 # do not grant bonus for him self

	balance, created = AccountBalance.objects.get_or_create(user=userFile.user,balance_type=BalanceType.ppd,defaults={
		'user':userFile.user,
		'balance_type':BalanceType.ppd
	})

	countryGroup={
		'A': ['BE','US','SA','PL','NL','GB','FR','ES','DE','CA'],
		'B': ['JP','KW','MC','NO','NZ','PT','QA','RU','SE','SG','ZA','IT','IM','AD','AE','AT','AU','CH','CY','CZ','DK','FI','IE','IL'],
		'C': ['LU','LV','MU','MY','OM','SI','TR','UA','LT','KR','AR','BG','BR','DO','EE','GR','HK','HU']
	}

	for groupID,countryISOcodeList in countryGroup.items():
		if iso_code in countryISOcodeList:break;
	else:
		groupID='D';

	pointPerDownloadDict = SystemConfigureController.getConfigure('pointPerDownloadForGroup%s'%(groupID), {
		0: 50, #file_size : ppd point
		10*1024*1024: 200,
		100*1024*1024: 500
	})
	pointPerDownload = max([ppdPoint for fileSize,ppdPoint in pointPerDownloadDict.items() if downloadSession.data.get('file_size',0)>fileSize])

	amount = pointPerDownload
	if userFile.user.profile.account_type == AccountType.affiliate:
		try:
			point_balance = AccountBalance.objects.get(user_id=userFile.user.id, balance_type=BalanceType.point)
		except Exception as e:
			logging.error(u"Unable to get AccountBalance with error=%s" % (e))
			return 0;
		bonus_point_amount = max(1,int(amount/1000)); #1000 ppd point = 1 credit
		if BalanceController.chargeBalance(point_balance.id, bonus_point_amount):
			logging.info(u"Success with amount=%s" % (bonus_point_amount))
		return 0;

	if BalanceController.chargeBalance(balance.id, amount) is True:
		logging.info(u"Success with amount=%s" % (amount))
		TransactionController.addTransactionLogByDate(timezone.now(),balance,amount,TransactionType.ppd)
		payPerDownloadRefererBonus(userFile.user.profile,amount,downloadSession)
		return amount
	else:
		logging.error(u"Failed during transaction with download_user_id=%s, userFile_id=%s, amount=%s" % (download_user_id, userFile_id, amount))

	return 0;


def payPerDownloadRefererBonus(ppd_userProfile,pointPerDownload,downloadSession):
	if not ppd_userProfile.referer or pointPerDownload<=0:
		return
	referer_user_id = ppd_userProfile.referer_id
	if ppd_userProfile.referer.profile.account_type not in [AccountType.affiliate,AccountType.affiliatePPD]:
		logging.debug(u"Do not grant bonus for non affiliate user");
		return 0;

	try:
		balance = AccountBalance.objects.get(user_id=referer_user_id, balance_type=BalanceType.ppd)
	except Exception as e:
		logging.error(u"Unable to get AccountBalance with error=%s" % (e))
		return

	refererBonusPercent = SystemConfigureController.getConfigure('ppdRefererBonusPercent', 0.05)
	if refererBonusPercent >= 1 or refererBonusPercent < 0:
		logging.error(u"Invalid refererBonusPercent")
		return
	# percent from the amount of agencyBonus
	amount = pointPerDownload * refererBonusPercent
	if BalanceController.chargeBalance(balance.id, amount):
		logging.info(u"Success with amount=%s" % (amount))
		TransactionController.addTransactionLogByDate(timezone.now(),balance,amount,TransactionType.refererPPD)
		return amount
	else:
		logging.error(u"Failed during transaction with referer_user_id=%s, amount=%s" % (referer_user_id, amount))


def verifyWebsiteOwner(affiliate_user, website_address):
	parseURL = urlparse(website_address);
	domain = parseURL.hostname;

	url = parseURL.scheme+'://'+parseURL.netloc+'/storagon.txt'

	if settings.IS_RUNNING_UNIT_TEST:
		return domain;

	br=Browser();

	for ti in range(3):
		try: text = br.open(url);
		except: continue;
		else: break;
	else:
		return False;

	if affiliate_user.username in text:
		return domain;

	return False;


def addWebsiteAgency(affiliate_user, website_domain):
	website, created = WebsiteAgency.objects.get_or_create(website_domain=website_domain, defaults={
		'user': affiliate_user, 'website_domain': website_domain
	})

	if not created:
		#todo: send mail to notify previous owner of this transfer website ownership
		website.user = affiliate_user;
		website.save();

	return website;


def countNotAvailableTransactionOfBalance(balance_id):
	cursor = connection.cursor();
	numOfDay = SystemConfigureController.getConfigure('numberOfDayBeforeTransactionBecomeAvailable', 21);
	markedDay = timezone.datetime.now()-timezone.timedelta(days=numOfDay);
	try:
		cursor.execute("""
			SELECT COUNT(tlog.id) as count_id, SUM(tlog.amount) as sum_amount FROM servermain_transactionlog as tlog
			JOIN servermain_accountbalance as balance ON balance.id = tlog.balance_id
			WHERE tlog.created_date > %s AND balance.id = %s AND tlog.transaction_type != %s
			;""", [markedDay,balance_id, TransactionType.transfer])
		raw_result = cursor.fetchall();
	except:
		raw_result = []
	finally:
		cursor.close()

	return raw_result


def countMoneyOnWithdrawingOfBalance(balance):
	querySet = balance.user.application.all().filter(apply_type=ApplyType.payAffiliate,apply_status__in=[ApplyStatus.processing,ApplyStatus.rejected]);
	sum_money = 0;
	count_application = 0;
	for application in querySet:
		data = Bunch(json.loads(application.data))
		if balance.id != data.withdraw_balance_id:continue;
		sum_money+=data.withdraw_amount
		count_application+=1
	return [[count_application,sum_money]]