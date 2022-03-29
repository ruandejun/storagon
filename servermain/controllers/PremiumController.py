#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  PremiumController
#  
#
#  Created by TVA on 3/12/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#
import hashlib
import datetime

from django.utils import timezone
from django.core import serializers

from servermain.models import PremiumKey, Bill
from servermain.controllers import AffiliateController
from storagon.tool import *
from storagon.enum import *
from system_configure.controllers import SystemConfigureController


def generatePremiumKey(reseller_id, plan_id, max_num_key=10):
	resultList = [];
	totalExistKey = PremiumKey.objects.count();
	index = 0;
	while len(resultList) < max_num_key:
		index += 1;
		if index > max_num_key*10: break;
		premkey = PremiumKey(reseller_id=reseller_id,plan_id=plan_id);
		premkey.code = hashlib.sha1('premkey_{}'.format(totalExistKey+index).encode('utf-8')).hexdigest()[:10]
		try:
			premkey.save()
		except Exception as e:
			continue;
		else:
			resultList+=[premkey];

	return resultList;


def exchangePremiumKey(user, premiumKey, agency_id=0, website_origin=''):
	plan_config = SystemConfigureController.getConfigure('plan%s' % (premiumKey.plan_id), settings.DEFAULT_PLAN_CONFIG)

	if user.profile.plan_id > 0:
		rebill=True;
	else:
		rebill=False;

	if grantPremiumStatusToUser(user,premiumKey.plan_id) is False:
		return False;

	bill = Bill(user_id=user.id, plan_id=premiumKey.plan_id)
	bill.money_charged = plan_config['price']
	bill.paygate_id = 0; #0 is reserved for paygate PremiumKey
	bill.detail = serializers.serialize('json', [premiumKey])  # save the whole premumKey into bill.detail
	bill.save()

	premiumKey.activated_date = timezone.now();
	premiumKey.activated_user = user;
	premiumKey.bill = bill;
	premiumKey.save();
	# complete session
	logging.info(u"Exchange PremiumKey=%s success with bill_id=%s" % (premiumKey, bill.id));

	# process affiliate program
	result1 = AffiliateController.agencyBonus(agency_id, bill, rebill=rebill)
	result2 = AffiliateController.websiteBonus(website_origin, bill, rebill=rebill)

	return True;


def grantPremiumStatusToUser(user, plan_id):
	userProfile=user.profile;
	plan_config = SystemConfigureController.getConfigure('plan%s' % (plan_id), settings.DEFAULT_PLAN_CONFIG)

	if plan_id != userProfile.getPlanID(): #erase and set new
		userProfile.plan_id = plan_id
		userProfile.plan_expired = timezone.now() + datetime.timedelta(seconds=plan_config['expires'])
	else: #same plan_id need to extend plan_expired
		extendDuration = datetime.timedelta(seconds=plan_config['expires'])
		userProfile.plan_expired = max(userProfile.plan_expired + extendDuration, timezone.now() + extendDuration)

	if userProfile.account_type == AccountType.affiliate:
		aff_plan_config = SystemConfigureController.getConfigure('affPremium', settings.DEFAULT_AFF_PREMIUM_CONFIG)
		userProfile.storage_space = aff_plan_config['storage'];
	else:
		userProfile.storage_space = plan_config['storage'];

	try:
		userProfile.save()
	except Exception as e:
		logging.error(u"Unable to save userProfile of user:"%(user.username));
		return False
	return True
