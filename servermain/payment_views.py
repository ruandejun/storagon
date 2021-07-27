#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  payment_views
#
#
#  Created by TVA on 12/23/14.
#  Copyright (c) 2014 storagon. All rights reserved.
#

from django.contrib.auth.decorators import login_required

from servermain.controllers import PaymentController
from storagon.tool import *
from storagon.enum import *
from system_configure.controllers import SystemConfigureController
from servermain.mongo_models import Session


@login_required
def buyPremium(request, plan_id, paygate_id):
	""" Create bill session and redirect user to paygate to buy premium plan

	response = redirect to paygate

	"""
	try:
		plan_id, paygate_id = int(plan_id), int(paygate_id)
	except ValueError:
		raise Http404()
	if plan_id <= 0 or paygate_id <= 0:
		raise Http404()
	paygateIDList = SystemConfigureController.getConfigure('paygateIDList', [1])
	if paygate_id not in paygateIDList:
		logging.warning(u"paygate_id=%d not in paygateIDList=%s, len=%d" % (paygate_id, paygateIDList, len(paygateIDList)))
		raise Http404()

	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (paygate_id), settings.DEFAULT_PAYGATE_CONFIG)
	if plan_id not in paygateConfig['plan_available']:
		logging.warning(u"plan_id=%s is not available for this paygate_id=%s" % (plan_id, paygate_id))
		raise Http404()

	if request.method == 'GET':
		if settings.DEBUG is False and settings.IS_RUNNING_UNIT_TEST is False: raise Http404();
		#disable this in production, this is only for testing
		billSession = PaymentController.buyPlan(request, request.user.id, plan_id, paygate_id)

		paygate_name = paygateConfig.get('paygate_name');
		if not settings.IS_RUNNING_UNIT_TEST:
			if paygate_name == 'paypal':
				result, message = PaymentController.paypalPaygateInitiator(request, billSession);
				if result is False:
					return errorResponse(u"Unable to buyPremium: %s"%message);
				return shortcuts.redirect(result)
			if paygate_name == 'webmoney':
				result, message = PaymentController.webmoneyPaygateInitiator(request, billSession);
				if result is False:
					return errorResponse(u"Unable to buyPremium: %s"%message);
				return HttpResponse(result)
			if paygate_name == 'payza':
				result, message = PaymentController.payzaPaygateInitiator(request, billSession);
				if result is False:
					return errorResponse(u"Unable to buyPremium: %s"%message);
				return HttpResponse(result)

		return successResponse({
			'paygate_name': paygateConfig.paygate_name,
			'billSession_id': str(billSession.id)
		})
	elif request.method == 'POST':

		billSession = PaymentController.buyPlan(request, request.user.id, plan_id, paygate_id)

		paygate_name = paygateConfig.get('paygate_name');
		if paygate_name == 'ekaepay':
			result, message = PaymentController.ekaepayChinaPayGateInitiator(request, billSession);
			if result is False:
				return errorResponse(u"Unable to buyPremium: %s"%message);
			return successResponse({
				'billSession_id': str(billSession.id)
			})
		elif paygate_name == 'webmoney':
			result, message = PaymentController.webmoneyPaygateInitiator(request, billSession);
			if result is False:
				return errorResponse(u"Unable to buyPremium: %s"%message);
			return HttpResponse(result)
		elif paygate_name == 'paypal':
			result, message = PaymentController.paypalPaygateInitiator(request, billSession);
			if result is False:
				return errorResponse(u"Unable to buyPremium: %s"%message);
			return shortcuts.redirect(result)
		else:
			return errorResponse(u"Unable to determine paygate handler for paygate_name=%s"%(paygate_name));

	else:
		raise Http404()


def paygateCallBack(request, paygate_name):
	#td comment this report session logging
	if settings.DEBUG is True:
		testResult = Session();
		testResult.type = SessionType.report;
		if request.method == 'POST':
			testResult.status = SessionStatus.working;
		testResult.data = {
			'full_path': request.get_full_path(),
			'method': str(request.method),
			'body': str(request.body),
			'META': str(request.META),
			'COOKIES': str(request.COOKIES),
		}
		testResult.save();
		logging.info(u"Receiving incoming request to paygateCallBack:\n%s"%(testResult.data));

	if paygate_name == 'ekaepay':
		PaymentController.ekaepayChinaPayGateCallbackHandler(request);
		return successResponse();
	elif paygate_name == 'paypal':
		paymentSuccessUrl = reverseBase(request,'payment-success',absolute=True);
		paymentFailUrl = reverseBase(request,'payment-fail',absolute=True);
		result, message = PaymentController.paypalPayGateCallbackHandler(request);
		if result is False:
			logging.error(u"Unable to process %s order with error: %s"%(paygate_name,message))
			return shortcuts.redirect(paymentFailUrl);
		return shortcuts.redirect(paymentSuccessUrl);
	elif paygate_name == 'webmoney':
		result, message = PaymentController.webmoneyCallbackHandler(request);
		if result is False:
			logging.error(u"Unable to process %s order with error: %s"%(paygate_name,message))
			return errorResponse(u"Unable to process order: %s"%message);
		return HttpResponse(result);
	elif paygate_name == 'payza':
		result, message = PaymentController.payzaCallbackHandler(request);
		if result is False:
			logging.error(u"Unable to process %s order with error: %s"%(paygate_name,message))
			return errorResponse(u"Unable to process order: %s"%message);
		return HttpResponse(result);

	raise Http404();
