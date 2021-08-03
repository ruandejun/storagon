#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Premium_ClientAPI
#  
#
#  Created by TVA on 3/12/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.core import serializers

from servermain.models import PremiumKey,AccountBalance
from servermain.controllers import PremiumController, BalanceController
from storagon.decorator import login_required_ajax, signature_test
from storagon.tool import *
from storagon.enum import *
from system_configure.controllers import SystemConfigureController
from rest_framework.decorators import api_view

@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
def getListPremiumKey(request):
	if request.method == 'GET':
		if request.user.profile.account_type != AccountType.reseller:
			raise Http403();

		offset, limit = getParamsOr400(request, ('offset', 0), ('limit', 0))

		query = PremiumKey.objects.all().filter(reseller=request.user, activated_user=None);

		if limit > 0:
			query = query[offset:offset + limit]
		else:
			query = query[offset:]

		data = serializers.serialize('json', query)

		return successResponse(data, encode=False);

	elif request.method == 'POST':
		raise Http404();
	pass;
@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
def buyPremiumKeyUsingCredit(request):
	if request.method == 'GET':
		raise Http404();
	elif request.method == 'POST':
		if request.user.profile.account_type != AccountType.reseller:
			raise Http403();

		max_num_key, plan_id = getParamsOr400(request, ('max_num_key', int), ('plan_id', int));

		if plan_id not in SystemConfigureController.getConfigure('planIDList', [settings.DEFAULT_PLAN_ID]):
			return errorResponse(u"plan_id is incorrect", code=0)

		plan_config = SystemConfigureController.getConfigure('plan%s' % (plan_id), settings.DEFAULT_PLAN_CONFIG)

		total_amount = max_num_key*plan_config['price'];

		try:
			#::type: AccountBalance
			balance = AccountBalance.objects.get(user_id=request.user, balance_type=BalanceType.credit)
		except Exception as e:
			logging.error(u"Unable to get AccountBalance with error=%s" % (e))
			return

		if balance.amount < total_amount:
			return errorResponse(u"Insufficient credit");

		if BalanceController.chargeBalance(balance.id, -total_amount) == True:
			premiumKeyList = PremiumController.generatePremiumKey(request.user.id, plan_id, max_num_key);
			logging.info(u"User=%s success buy %s PremiumKey for plan=%s, total=%s"%(request.user.username, max_num_key, plan_id, total_amount));
			if len(premiumKeyList)!=max_num_key:
				logging.warning(u"User=%s bought %s PremiumKey but received %s key"%(request.user.username,max_num_key,len(premiumKeyList)));
			data = serializers.serialize('json', premiumKeyList)
			return successResponse(data, encode=False);

		return errorResponse(u"Failed to buy PremiumKey due to transaction error.");
@api_view(['GET','POST','PUT'])
@login_required_ajax()
@signature_test()
def exchangePremiumKey(request):
	if request.method == 'GET':
		raise Http404();
	elif request.method == 'POST':
		premium_code = getParamsOr400(request, 'premium_code');

		try:
			premiumKey = PremiumKey.objects.get(code=premium_code, activated_user=None);
		except PremiumKey.DoesNotExist:
			return errorResponse(u"Premium code is invalid!");

		try:
			agency_id = int(request.COOKIES.get('agency_id', 0))
		except ValueError:
			agency_id = 0

		website_origin = request.COOKIES.get('website_origin', '')

		result = PremiumController.exchangePremiumKey(request.user, premiumKey, agency_id, website_origin);
		if result is False:
			return errorResponse(u"Failed to exchange PremiumKey=%s"%(premiumKey.code));

		return successResponse({'plan_id': premiumKey.plan_id});




