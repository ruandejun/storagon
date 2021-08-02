#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  PaymentController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import datetime
import re
import hashlib
import urllib
import base64

import yaml
from django.utils import timezone

from servermain.models import Bill, User
from servermain.mongo_models import Session
from . import PremiumController, AffiliateController, BalanceController
from storagon.tool import *
from storagon.enum import *
from storagon.browser import Browser, Rqbrowser
from system_configure.controllers import SystemConfigureController
from django.template import Context, Template


def boughtPlan(bill, plan_id):
	""" Grant premium plan to user in purchased bill

	:param user_id:
	:param plan_config:
	:return: True/False
	"""
	return PremiumController.grantPremiumStatusToUser(bill.user, plan_id);


def exchangePointToPlan(request, user_id, plan_id):
	""" Grant premium plan to user exchange point

	:param request:
	:param user_id:
	:param plan_id:
	:return:
	"""
	user = getObjectOrNone(User, id=user_id)
	if not user:
		return False
	exchangePointRateDict = SystemConfigureController.getConfigure('exchangePointRate', settings.DEFAULT_EXCHANGE_POINT)
	exchangeRate = exchangePointRateDict['plan%s' % plan_id]

	try:
		balance = user.accountbalance_set.get(balance_type=BalanceType.point)
	except Exception as e:
		logging.error(u"unable to get AccountBalance with error=%s" % (e))
		return False

	if balance.amount < exchangeRate:  # insufficient
		return None

	if BalanceController.chargeBalance(balance.id, -exchangeRate) is True:
		return PremiumController.grantPremiumStatusToUser(user, plan_id);
	return False


def paygateCallBackHandler(request, bill_session_id):
	""" Grant user a premium status after a successful purchase

	:param bill_session_id:
	:return:
	"""
	try:
		billSession = Session.objects.get(id=bill_session_id, type=SessionType.bill)
	except Session.DoesNotExist:
		return errorResponse(u"Bill session does not exist", code=0)

	if billSession.type != SessionType.bill or billSession.status != SessionStatus.waiting or timezone.now() > billSession.created + datetime.timedelta(seconds=settings.MONGO_SESSION_EXPIRES):
		# todo: return with correct errorReponse for each paygate instead of this
		return errorResponse(u"Invalid bill session", code=0)

	plan_id = billSession.data.get('plan_id')
	paygate_id = billSession.data.get('paygate_id')
	# todo: verify paygate_id, plan_id to match with request came from paygate

	if not plan_id or not billSession.uid:
		return errorResponse(u"Bill session is invalid", code=0)
	# check plan_id is correct (is in plan_id_list)
	if plan_id not in SystemConfigureController.getConfigure('planIDList', [1]):
		return errorResponse(u"plan_id is incorrect", code=0)


	# grant plan
	# save bill
	bill = Bill(user_id=billSession.uid, plan_id=plan_id)
	if billSession.data['userfile_id']>0:
		bill.userFile_id = billSession.data['userfile_id']

	bill.money_charged = billSession.data.get('price', 0)
	bill.paygate_id = paygate_id
	bill.detail = billSession.to_json()  # save the whole billSession into bill.detail
	bill.save()

	if bill.user.profile.plan_id > 0:
		rebill=True;
	else:
		rebill=False;

	result = boughtPlan(bill, plan_id)
	if result:
		# complete session
		billSession.status = SessionStatus.completed
		billSession.sid = bill.id
		billSession.save()
		logging.info(u"billSesssion_id=%s has completed with a payment of bill_id=%s" % (billSession.id, bill.id))
		# process affiliate program
		result1 = AffiliateController.agencyBonus(billSession.data['agency_id'], bill, website_origin=billSession.data['website_origin'], rebill=rebill)
		result2 = AffiliateController.websiteBonus(billSession.data['website_origin'], bill , rebill=rebill)

		return True;
	else:
		# fail session
		billSession.status = SessionStatus.failed
		billSession.sid = bill.id
		billSession.save()
		logging.warning(u"billSesssion_id=%s has failed with a payment of bill_id=%s" % (billSession.id, bill.id))
		return None


def buyPlan(request, user_id, plan_id, paygate_id):
	""" Call this before user make a payment in order to purchase a plan for more storage

	:param user_id:
	:param plan_id:
	:return: billSession.id
	"""
	try:agency_id = int(request.COOKIES.get('agency_id', 0))
	except ValueError: agency_id = 0

	try:userfile_id = int(request.COOKIES.get('userfile_id', 0))
	except ValueError: userfile_id = 0

	if plan_id not in SystemConfigureController.getConfigure('planIDList', [1]):
		raise Http400(u"plan_id is incorrect")

	if paygate_id not in SystemConfigureController.getConfigure('paygateIDList', [1]):
		raise Http400(u"paygate_id is incorrect")

	plan_config = SystemConfigureController.getConfigure('plan%s' % (plan_id), settings.DEFAULT_PLAN_CONFIG)
	# create bill session
	billSession = Session(uid=user_id)
	billSession.type = SessionType.bill
	billSession.data['plan_id'] = plan_id
	billSession.data['paygate_id'] = paygate_id
	billSession.data['agency_id'] = agency_id
	billSession.data['userfile_id'] = userfile_id
	billSession.data['website_origin'] = request.COOKIES.get('website_origin', '')
	billSession.data['website_url'] = request.COOKIES.get('website_url', '')

	billSession.data['ip_address'] = request.META['REMOTE_ADDR']
	try:response = settings.geo_reader.country(billSession.data['ip_address']);
	except:pass;
	else:billSession.data['iso_code']=response.country.iso_code

	billSession.data.update(plan_config)
	billSession.text='';
	billSession.save()

	return billSession


def ekaepayChinaPayGateInitiator(request, billSession):

	card_number, card_name, card_expiry, card_cvc, first_name, last_name, email, phone_number, address, country, state, city, zipcode = \
		getParamsOr400(request, 'card_number', 'card_name', 'card_expiry', 'card_cvc', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'country', 'state', 'city', 'zipcode');

	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);

	merNo = str(paygateConfig['merNo'])
	md5Key = str(paygateConfig['md5Key'])

	currencyCode = 'USD'
	currencyStr = '15'
	returnURL = reverseBase(request,'paygateCallBack',args=['ekaepay'],absolute=True) #"http://storagon.com/paygatecallback/ekaepay/"
	issuingBank = 'ccb'
	remark = 'storagon.com'

	billNo = str(billSession.id);

	customerIP = request.META['REMOTE_ADDR'] #'173.57.137.24'; # '118.70.183.108', #

	price = billSession.data['price']; #price is cent

	plan_name = str(billSession.data['plan_id']);
	plan_price = str(price / 100.); #plan_price is USD
	amount = str(price / 100.);  # amount is USD

	md5Info = hashlib.md5(merNo + billNo + amount + currencyCode + currencyStr + returnURL + email + md5Key).hexdigest().upper();

	#pre check card info
	card_number = card_number.replace(' ', '');
	visaPattern = r'^4\d{12}$|^4\d{15}$';
	mastercardPattern = r'^5\d{15}$';
	discoverPattern = r'^6011\d{12}$';
	amexPattern = r'^(34|37)\d{13}$';

	if re.match(visaPattern, card_number):
		card_type = 'visa'
	elif re.match(mastercardPattern, card_number):
		card_type = 'mastercard'
	elif re.match(discoverPattern, card_number):
		card_type = 'discover'
	elif re.match(amexPattern, card_number):
		card_type = 'amex'
	else:
		print(card_number);
		raise Http400("card_number is not correct");



	expirePattern = r'^(\d\d)\s*/\s*(\d\d)$';
	m = re.match(expirePattern, card_expiry);
	if not m:
		print("expire=%s"%(card_expiry));
		raise Http400("card_expiry is notcorrect");
	exireMonth = m.group(1);
	expireYear = '20' + m.group(2);

	card_cvc = card_cvc.replace(' ', '');
	cvcPattern = r'^\d{3,4}$'
	m = re.match(cvcPattern, card_cvc);
	if not m:
		print("CVC=%s"%(card_cvc));
		raise Http400("card_cvc is not correct");

	xmlData = u"""<?xml version="1.0" encoding="UTF-8" ?> <Order>
<MerNo>%(merNo)s</MerNo>
<BillNo>%(billNo)s</BillNo>
<GoodsList>
	<Goods>
		<GoodsName>%(plan_name)s</GoodsName>
		<Price>%(plan_price)s</Price>
		<Qty>1</Qty>
	</Goods>
</GoodsList>

<Amount>%(amount)s</Amount>
<Freight>0.00</Freight>
<CurrencyCode>%(currencyCode)s</CurrencyCode>
<BFirstName>%(bFirstName)s</BFirstName>
<BLastName>%(bLastName)s</BLastName>
<Email>%(email)s</Email>
<Phone>%(phone)s</Phone>
<BillAddress>%(bAddress)s </BillAddress>
<BillCity>%(bCity)s</BillCity>
<BillState>%(bState)s</BillState>
<BillCountry>%(bCountry)s</BillCountry>
<BillZip>%(bZipcode)s</BillZip>
<SFirstName>%(sFirstName)s</SFirstName>
<SLastName>%(sLastName)s</SLastName>
<ShipAddress>%(sAddress)s</ShipAddress>
<ShipCity>%(sCity)s</ShipCity>
<ShipState>%(sState)s</ShipState>
<ShipCountry>%(sCountry)s</ShipCountry>
<ShipZip>%(sZipcode)s</ShipZip>
<ShipEmail>%(sEmail)s</ShipEmail>
<ShipPhone>%(sPhone)s</ShipPhone>
<Language>2</Language>
<LangCode>en</LangCode>
<Currency>%(currencyStr)s</Currency>
<ReturnURL>%(returnURL)s</ReturnURL>
<Remark>%(remark)s</Remark>
<IssuingBank>%(issuingBank)s</IssuingBank>
<CardNo>%(cardNumber)s</CardNo>
<SecurityCode>%(cardCVC)s</SecurityCode>
<CardExpireMonth>%(cardExpireMonth)s</CardExpireMonth>
<CardExpireYear>%(cardExpireYear)s</CardExpireYear>
<Ip>%(customerIP)s</Ip>
<BroserType>%(browserType)s</BroserType>
<BrowserLang>%(browserLang)s</BrowserLang>
<Sessionid>%(sessionID)s</Sessionid>
<ReferUrl>%(referURL)s</ReferUrl>
<MD5info>%(md5Info)s</MD5info>
</Order>
""" % ({
		'merNo': merNo,
		'billNo': billNo,
		'plan_name': plan_name,
		'plan_price': plan_price,
		'amount': amount,

		'bFirstName': first_name,
		'bLastName': last_name,
		'email': email,
		'phone': phone_number,
		'bAddress': address,
		'bCity': city,
		'bState': state,
		'bCountry': country,
		'bZipcode': zipcode,

		'sFirstName': first_name,
		'sLastName': last_name,
		'sEmail': email,
		'sPhone': phone_number,
		'sAddress': address,
		'sCity': city,
		'sState': state,
		'sCountry': country,
		'sZipcode': zipcode,

		'currencyCode': currencyCode,
		'currencyStr': currencyStr,
		'returnURL': returnURL,
		'remark': remark,
		'issuingBank': issuingBank,
		'cardNumber': card_number,
		'cardCVC': card_cvc,
		'cardExpireMonth': exireMonth,
		'cardExpireYear': expireYear,
		'customerIP': customerIP,
		'browserType': request.META.get('HTTP_USER_AGENT', 'IE')[:20],
		'browserLang': request.META.get('HTTP_ACCEPT_LANGUAGE', 'En')[:20],
		'sessionID': str(billSession.id),
		'referURL': request.META.get('HTTP_REFERER', 'http://storagon.com'),
		'md5Info': md5Info,
	})


	logging.info("Request to Paygate ekaepay XML:\n%s"%(xmlData));

	urlencodedXML = urllib.urlencode([('', xmlData.replace('\n', ''))])[1:];
	# print urlencodedXML;
	TradeInfo = base64.b64encode(urlencodedXML);

	billSession.data['MD5info'] = md5Info;
	billSession.data['customerIP'] = customerIP;
	billSession.data['remark'] = remark;
	billSession.data['currencyCode'] = currencyCode;
	billSession.data['currencyStr'] = currencyStr;
	billSession.save();

	br = Rqbrowser();
	br.quite = True;
	# html=None;
	html = br.open('https://security.dollarcollect.com/pay/DirectProcess', {'TradeInfo': TradeInfo}, forceReferer='http://storagon.com');

	returnDataPattern = r'<TradeNo>(\w+)</TradeNo><BillNo>(\w+)</BillNo><ResultCode>(\d+)</ResultCode><ResultMsg>(.+?)</ResultMsg><Sourceamount>([\d.]+)</Sourceamount><Sourcecurrency>(\w+)</Sourcecurrency><SignInfo>(\w+)</SignInfo>';

	logging.info("Response from Paygate ekaepay of billNo=%s :\n%s"%(billNo, html));

	m = re.search(returnDataPattern, html);
	if not m:
		return False, "returnData from paygate is in wrong format:\n%s"%(html);

	TradeNo = m.group(1);
	BillNo = m.group(2);
	ResultCode = m.group(3);
	ResultMSG = m.group(4);
	SourceAmount = m.group(5);
	SourceCurrency = m.group(6);
	SignInfo = m.group(7);

	try:
		billSessionRefresh = Session.objects.get(id=BillNo);
	except Session.DoesNotExist:
		pass;
	else:
		if billSessionRefresh.text is None: billSessionRefresh.text = '';
		billSessionRefresh.text += html + '\n';
		billSessionRefresh.data['TradeNo'] = TradeNo;
		billSessionRefresh.data['SignInfo'] = SignInfo;
		billSessionRefresh.save();

	# checkSignInfo = hashlib.md5(SourceCurrency + ResultCode + SourceAmount + TradeNo + BillNo + md5Key);
	if BillNo != billNo: #or SignInfo != checkSignInfo:
		return False, "returnData from paygate contain incorrect data";

	if ResultCode == '1017': return False, "shipping info is missing";
	elif ResultCode == '2018': return False, "CC is rejected due to fault check"
	elif ResultCode == '2027': return False, "Customer IP is banned"
	elif ResultCode == '2088': return False, "CC is rejected due to high risk"
	elif ResultCode == '05':
		return False, "Failed to completed operation of payment, due to time limit between payment process"
	elif ResultCode == '00':
		return True, "Successful operation of payment, TradeNo=%s"%(TradeNo);

	return False, "Unknow error %s, msg=%s"%(ResultCode, ResultMSG);


def ekaepayChinaPayGateCallbackHandler(request):

	BillNo, TradeNo, Currency, CurrencyCode, Amount, Succeed, BankID, Result, MD5info, Remark = \
		getParamsOr400(request, 'BillNo', ('TradeNo', ''), ('Currency', ''), ('CurrencyCode', ''), 'Amount', 'Succeed', ('BankID', ''), 'Result', 'MD5info', 'Remark');

	try:
		billSession = Session.objects.get(id=BillNo);
	except Session.DoesNotExist:
		logging.error("Paygate ekaepay callback for a non exist BillNo=%s"%(BillNo));
		return;

	if billSession.text is None: billSession.text = '';
	billSession.text += 'CallBack POST:' + request.body + '\n' + yaml.dump(request.META) + '\n';
	billSession.save();
	if Succeed == '1':
		logging.info("Paygate ekaepay completed payment process for BillNo=%s, Result=%s"%(BillNo, Result));
		paygateCallBackHandler(request, BillNo);
		return;

	logging.info("Paygate ekaepay failed payment process for BillNo=%s, Succeed=%s, Result=%s"%(BillNo, Succeed, Result));
	return;


def paypalPaygateInitiator(request, billSession):
	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);

	PP_USER = paygateConfig.PP_USER
	PP_PASSWORD = paygateConfig.PP_PASSWORD
	PP_SIGNATURE = paygateConfig.PP_SIGNATURE
	PP_CHECKOUT_URL = paygateConfig.PP_CHECKOUT_URL
	PP_NVP_ENDPOINT = paygateConfig.PP_NVP_ENDPOINT

	API_VERSION = 122;
	currencyCode = 'USD'
	returnURL = reverseBase(request,'paygateCallBack',args=['paypal'],absolute=True)+"?BillNo=%s"%(billSession.id)

	paymentSuccessUrl = reverseBase(request,'payment-success',absolute=True);
	paymentFailUrl = reverseBase(request,'payment-fail',absolute=True);

	remark = 'storagon.com'

	billNo = str(billSession.id);

	customerIP = request.META['REMOTE_ADDR'] #'173.57.137.24'; # '118.70.183.108', #

	price = billSession.data['price']; #price is cent

	plan_name = str(billSession.data['plan_id']);

	paymentAction = 'Sale';

	amount = str(price / 100.);  # amount is USD

	br = Rqbrowser();
	br.quite = True;
	param = {
		'USER' : PP_USER,
		'PWD': PP_PASSWORD,
		'SIGNATURE': PP_SIGNATURE,
		'VERSION': API_VERSION,
		'METHOD' : 'SetExpressCheckout',
		'PAYMENTREQUEST_0_AMT' : amount,# payment amount
		'PAYMENTREQUEST_0_PAYMENTACTION' : paymentAction, # type of transaction
		'PAYMENTREQUEST_0_CURRENCYCODE' : currencyCode, # payment currency code
		'returnUrl' : returnURL, # redirect URL for use if the customer authorizes payment
		'cancelUrl' : paymentFailUrl,
	}
	html = br.open(PP_NVP_ENDPOINT+'?'+urllib.urlencode(param));
	result={};
	# try:
	for param in html.split('&'):
		name,value = param.split('=')
		result[name] = value;
	# except: return False, html;

	billSession.text += 'Paypal SetExpressCheckout: ' + yaml.dump(result,default_flow_style=False, default_style='') + '\n';
	billSession.save();

	if result['ACK'] != 'Success':
		return False, u"Failed to initiate paypal express checkout!"

	TOKEN = result['TOKEN'];
	TIMESTAMP = result['TIMESTAMP'];
	CORRELATIONID = result['CORRELATIONID'];
	VERSION=result['VERSION']
	BUILD=result['BUILD']

	return PP_CHECKOUT_URL+'?token=%s&useraction=commit'%(TOKEN), None;


def paypalPayGateCallbackHandler(request):
	BillNo, token, PayerID = getParamsOr400(request,'BillNo', 'token', 'PayerID')

	try:
		billSession = Session.objects.get(id=BillNo);
	except Session.DoesNotExist:
		msg = u"Paygate paypal callback for a not exist BillNo=%s"%(BillNo);
		logging.error(msg);
		return False, msg;

	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);

	PP_USER = paygateConfig.PP_USER
	PP_PASSWORD = paygateConfig.PP_PASSWORD
	PP_SIGNATURE = paygateConfig.PP_SIGNATURE
	PP_CHECKOUT_URL = paygateConfig.PP_CHECKOUT_URL
	PP_NVP_ENDPOINT = paygateConfig.PP_NVP_ENDPOINT

	API_VERSION = 122; #109.0

	param = {
		'USER' : PP_USER,
		'PWD': PP_PASSWORD,
		'SIGNATURE': PP_SIGNATURE,
		'VERSION': API_VERSION,
		'METHOD' : 'GetExpressCheckoutDetails',
		'TOKEN' : token,
	}
	br = Rqbrowser();
	br.quite = True;
	html = br.open(PP_NVP_ENDPOINT+'?'+urllib.urlencode(param));
	result={};
	try:
		for param in html.split('&'):
			name,value = param.split('=')
			result[name] = value;
	except:
		logging.error(u"Unexpected response format from paypal:"+html)
		return False, u"Unexpected response format from paypal!"

	if billSession.text is None: billSession.text = '';
	billSession.text += 'Paypal GetExpressCheckoutDetails: ' + yaml.dump(result,default_flow_style=False, default_style='') + '\n';


	if result['ACK'] != 'Success':
		return False, u"Failed to complete order from paypal!"

	price = billSession.data['price']; #price is cent
	plan_name = str(billSession.data['plan_id']);

	amount = str(price / 100.);  # amount is USD
	currencyCode = 'USD'
	paymentAction = 'Sale'

	param = {
		'USER' : PP_USER,
		'PWD': PP_PASSWORD,
		'SIGNATURE': PP_SIGNATURE,
		'VERSION': API_VERSION,
		'METHOD' : 'DoExpressCheckoutPayment',
		'TOKEN' : token,
		'PAYERID': PayerID,
		'PAYMENTREQUEST_0_AMT' : amount, # payment amount
		'PAYMENTREQUEST_0_PAYMENTACTION': paymentAction,
		'PAYMENTREQUEST_0_CURRENCYCODE' : currencyCode, # payment currency code
	}
	br = Rqbrowser();
	br.quite = True;
	html = br.open(PP_NVP_ENDPOINT+'?'+urllib.urlencode(param));
	result={};
	try:
		for param in html.split('&'):
			name,value = param.split('=')
			result[name] = value;
	except:
		logging.error(u"Unexpected response format from paypal:"+html)
		return False, u"Unexpected response format from paypal!"

	if result['ACK'] != 'Success':
		logging.warning("Paygate paypal failed payment process for BillNo=%s, result=%s"%(BillNo, result));
		return False, u"Failed to final confirm order from paypal!"

	billSession.text += 'Paypal DoExpressCheckoutPayment: ' + yaml.dump(result,default_flow_style=False, default_style='') + '\n';
	billSession.save();

	logging.info("Paygate paypal completed payment process for BillNo=%s, result=%s"%(BillNo, result));
	paygateCallBackHandler(request, BillNo);

	return True, None;


def webmoneyPaygateInitiator(request,billSession):

	html=u"""<html>
<head><title>Webmoney Pay</title></head>
<script type="text/javascript">
	//auto submit
	function submitForm(){
		var form = document.getElementById('pay');
		form.submit();
	}
</script>
<body onload="submitForm()">
	<form id=pay name=pay method="POST" action="https://merchant.wmtransfer.com/lmi/payment.asp">
		<p>
			<input type="hidden" name="LMI_PAYMENT_AMOUNT" value="{{ LMI_PAYMENT_AMOUNT }}">
			<input type="hidden" name="LMI_PAYMENT_DESC" value="Payment Storagon.com">
			<input type="hidden" name="LMI_PAYMENT_NO" value="{{ LMI_PAYMENT_NO }}">
			<input type="hidden" name="LMI_PAYEE_PURSE" value="{{ LMI_PAYEE_PURSE }}">
			<input type="hidden" name="BillNo" value="{{ BillNo }}">
			<input type="hidden" name="LMI_SIM_MODE" value="0">
		</p>
		<p>
			<input type="submit" value="submit">
		</p>
		</form>
</body>
</html>
"""
	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);

	LMI_PAYEE_PURSE = paygateConfig.LMI_PAYEE_PURSE

	billNo = str(billSession.id);
	plan_name = str(billSession.data['plan_id']);
	price = billSession.data['price']; #price is cent
	amount = str(price / 100.);  # amount is USD

	context = Context({
		'LMI_PAYMENT_AMOUNT':amount,
		'LMI_PAYMENT_NO': int(billNo[-4:],16),
		'LMI_PAYEE_PURSE':LMI_PAYEE_PURSE,
		'BillNo': billNo,
	});

	return Template(html).render(context), None


def webmoneyCallbackHandler(request):
	if request.META['REMOTE_ADDR'] not in ['91.227.52.97']:
		logging.warning("Paygate webmoney failed payment process due to invalid ip=%s"%(request.META['REMOTE_ADDR']));
		return False, u"Request come from unexpected ip";

	LMI_PREREQUEST = request.POST.get('LMI_PREREQUEST')

	LMI_MODE = request.POST['LMI_MODE']
	LMI_PAYMENT_AMOUNT = request.POST['LMI_PAYMENT_AMOUNT']
	LMI_PAYEE_PURSE = request.POST['LMI_PAYEE_PURSE']
	LMI_PAYMENT_NO = request.POST['LMI_PAYMENT_NO'] #this could be replace by BillNo
	LMI_PAYER_WM = request.POST['LMI_PAYER_WM']
	LMI_PAYER_PURSE = request.POST['LMI_PAYER_PURSE']
	LMI_PAYER_COUNTRYID = request.POST['LMI_PAYER_COUNTRYID']
	LMI_PAYER_IP = request.POST['LMI_PAYER_IP']
	LMI_PAYMENT_DESC = request.POST['LMI_PAYMENT_DESC']
	LMI_LANG = request.POST['LMI_LANG']
	LMI_DBLCHK = request.POST['LMI_DBLCHK']
	BillNo = request.POST['BillNo']

	try:
		billSession = Session.objects.get(id=BillNo);
	except Session.DoesNotExist:
		msg = u"Paygate webmoney callback for a not exist BillNo=%s"%(BillNo);
		logging.error(msg);
		return False, msg;

	billSession.text += 'Webmoney POST: ' +request.body+ '\n';
	billSession.save();

	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);


	price = billSession.data['price']; #price is cent
	amount = str(price / 100.);  # amount is USD

	if paygateConfig.LMI_PAYEE_PURSE != LMI_PAYEE_PURSE:
		logging.warning("Paygate webmoney failed payment process for BillNo=%s, due to invalid LMI_PAYEE_PURSE=%s"%(BillNo, LMI_PAYEE_PURSE));
		return False, u"Failed to final confirm order from webmoney!"

	if LMI_PAYMENT_AMOUNT != amount:
		logging.warning("Paygate webmoney failed payment process for BillNo=%s, due to invalid LMI_PAYMENT_AMOUNT=%s"%(BillNo, LMI_PAYMENT_AMOUNT));
		return False, u"Failed to final confirm order from webmoney!"

	if LMI_PREREQUEST=="1":
		return "Yes", None;

	# LMI_SECRET_KEY = paygateConfig.get('LMI_SECRET_KEY');
	# LMI_SYS_INVS_NO = request.POST['LMI_SYS_INVS_NO']
	# LMI_SYS_TRANS_NO = request.POST['LMI_SYS_TRANS_NO']
	# LMI_SYS_TRANS_DATE = request.POST['LMI_SYS_TRANS_DATE']
	# LMI_HASH = request.POST['LMI_HASH']
	# md5Info = hashlib.md5(LMI_PAYEE_PURSE + LMI_PAYMENT_AMOUNT + LMI_PAYMENT_NO + LMI_MODE + LMI_SYS_INVS_NO + LMI_SYS_TRANS_NO + LMI_SYS_TRANS_DATE + LMI_SECRET_KEY + LMI_PAYER_WM).hexdigest().upper();
	# if LMI_HASH != md5Info:
	# 	logging.warning("Paygate webmoney failed payment process for BillNo=%s, due to invalid LMI_HASH=%s, correct=%s"%(BillNo, LMI_HASH, md5Info));
	# 	return False, u"Failed to final confirm order from webmoney!"

	logging.info("Paygate webmoney completed payment process for BillNo=%s, result=%s"%(BillNo, request.body));
	paygateCallBackHandler(request, BillNo);

	return "Success", None;


def payzaPaygateInitiator(request, billSession):
	html=u"""<form method="post" action="{{checkOutURL}}" >
	<input type="hidden" name="ap_merchant" value="{{ap_merchant}}"/>
	<input type="hidden" name="ap_purchasetype" value="item-goods"/>
	<input type="hidden" name="ap_itemname" value="{{ap_itemname}}"/>
	<input type="hidden" name="ap_amount" value="{{ap_amount}}"/>
	<input type="hidden" name="ap_currency" value="{{ap_currency}}"/>

	<input type="hidden" name="ap_quantity" value="1"/>
	<input type="hidden" name="ap_itemcode" value="{{ap_itemcode}}"/>
	<input type="hidden" name="ap_description" value="{{ap_description}}"/>
	<input type="hidden" name="ap_returnurl" value="{{ap_returnurl}}"/>
	<input type="hidden" name="ap_cancelurl" value="{{ap_cancelurl}}"/>

	<input type="image" src="https://www.payza.com/images/payza-buy-now.png"/>
</form>
"""
	paymentSuccessUrl = reverseBase(request,'payment-success',absolute=True);
	paymentFailUrl = reverseBase(request,'payment-fail',absolute=True);

	paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);

	ap_merchant = paygateConfig.ap_merchant

	billNo = str(billSession.id);
	plan_name = 'plan '+str(billSession.data['plan_id']);
	price = billSession.data['price']; #price is cent
	amount = str(price / 100.);  # amount is USD

	context = Context({
		'checkOutURL' : 'https://sandbox.Payza.com/sandbox/payprocess.aspx',
		'ap_merchant' : 'seller_1_tranvietanh1991@gmail.com',
		'ap_itemname' : plan_name,
		'ap_amount' : amount,
		'ap_currency' : 'USD',
		'ap_itemcode' : billNo,
		'ap_description' : plan_name,
		'ap_returnurl' : paymentSuccessUrl,
		'ap_cancelurl' : paymentFailUrl
	});

	return Template(html).render(context), None


def payzaCallbackHandler(request):
	if request.META['REMOTE_ADDR'] not in ['174.142.185.134']:
		logging.warning("Paygate payza failed payment process due to invalid ip=%s"%(request.META['REMOTE_ADDR']));
		return False, u"Request come from unexpected ip";

	IPN_V2_Handler_URL = 'https://sandbox.Payza.com/sandbox/IPN2.ashx'

	br = Rqbrowser();
	br.quite = True;
	if 'token=' in request.body: #send confirmation
		html = br.open(IPN_V2_Handler_URL,data=request.body);
	else:
		ap_totalamount = request.POST.get('ap_totalamount')
		BillNo = request.POST.get('ap_itemcode')
		try:
			billSession = Session.objects.get(id=BillNo);
		except Session.DoesNotExist:
			msg = u"Paygate payza callback for a not exist BillNo=%s"%(BillNo);
			logging.error(msg);
			return False, msg;

		billSession.text += 'Payza POST: ' +request.body+ '\n';
		billSession.save();

		paygateConfig = SystemConfigureController.getConfigure('paygate%s' % (billSession.data['paygate_id']), settings.DEFAULT_PAYGATE_CONFIG);
		price = billSession.data['price']; #price is cent
		amount = str(price / 100.);  # amount is USD
		if ap_totalamount!=amount:
			logging.warning("Paygate payza failed payment process for BillNo=%s, due to invalid ap_totalamount=%s"%(BillNo, ap_totalamount));
			return False, u"Failed to final confirm order from payza!"

		logging.info("Paygate payza completed payment process for BillNo=%s, result=%s"%(BillNo, request.body));
		paygateCallBackHandler(request, BillNo);