#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  User_ClientAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import random
import re
from django.http import *
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.core import serializers
from django.forms import *
from django.utils import timezone

from storagon.enum import *
from storagon.tool import *
from servermain.models import User, UserProfile, UserApply, AccountBalance
from servermain.controllers import EmailController,AffiliateController
from storagon.decorator import banned_check, login_required_ajax, signature_test
from system_configure.controllers import SystemConfigureController


@signature_test()
def custom_login(request):
	""" Login an user to Storagon using ajax POST

	request.POST ={
		username : ,
		password : ,
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = authenticate(username=username, password=password)

		if user is None:
			return errorResponse("Username or password is not valid", code=0)

		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		# automaticaly create all type of balance for this user
		for balanceType in [BalanceType.credit,BalanceType.point,BalanceType.ppd]:
			balance, created = AccountBalance.objects.get_or_create(user=user, balance_type=balanceType)

		return successResponse()
	else:
		raise Http404()


def custom_logout(request):
	""" Logout current user

	request.POST

	response = success
	"""
	if request.method == 'GET':
		logout(request)
		return successResponse()
	elif request.method == 'POST':
		logout(request)
		return successResponse()
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def getUserInfo(request):
	""" Get info of current user

	request.GET

	response = JSON {
		'user_id' : user.id,
		'username': username,
		'profiles' : user profile in String JSON format like this
			[{"fields": {"storage_space": 0, "account_type": 0, "eumk": "", "plan_expired": "2014-11-29", "website_agency": "", "full_name": "admin", "address": "", "account_status": 0, "plan_id": 0, "email": ""}, "model": "servermain.userprofile", "pk": 2}]
	}
	"""
	if request.method == 'GET':
		profile = request.user.profile
		data = serializers.serialize('json', [profile], fields=('full_name', 'email', 'address', 'account_type', 'account_status',
		'storage_space', 'plan_id', 'plan_expired'))

		return successResponse({
			'user_id': request.user.id,
			'username': request.user.username,
			'profiles': data,
		})

	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


class UpdateProfileForm(ModelForm):

	class Meta:
		model = UserProfile
		fields = ['full_name', 'email', 'address']

	full_name = CharField(required=False)
	email = CharField(required=False)
	address = CharField(required=False)

	old_password = CharField(widget=PasswordInput, label="Old password", required=False)
	password = CharField(widget=PasswordInput, label="Change password", required=False)

@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def updateUserInfo(request):
	""" Update user info

	request.POST = {
	'full_name','email','address','website_agency',
	'old_password','password',
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		form = UpdateProfileForm(request.POST, instance=request.user.profile)
		if form.is_valid():
			profile = form.save(commit=False)
			# change password requide user to provide old password
			old_password = form.cleaned_data['old_password']
			password = form.cleaned_data['password']
			if old_password and password:
				if check_password(old_password, request.user.password):
					request.user.set_password(password)
					request.user.save()
				else:
					return errorResponse("Old password doesn't match", code=18)
			if request.user.email != profile.email:
				profile.account_status = AccountStatus.emailNotActivated  # set AccountStatus to emailNotActivated when user change email.
			profile.save()  # actually save
			return successResponse()
		else:
			return HttpResponseBadRequest(form.errors)
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def getUserBalance(request):
	""" Get current user AccountBalance

	request.GET

	response = JSON list of AccountBalance format like this [
		{"fields": {"user": 0, "balance_type": 0, "amount": 0}, "model": "servermain.accountbalance", "pk": 1}
		...
	]
	"""
	if request.method == 'GET':
		data = serializers.serialize('json', request.user.accountbalance_set.all())
		return successResponse(data, encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()


@signature_test()
def signup(request):
	""" Signup a new user and login his account immediately

	request.POST = {
		'username':,
		'password':,
		'email':,
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		username, password, email, referer = getParamsOr400(request, 'username', 'password', 'email', ('referer', ''));

		if not re.match(r'^\w[a-zA-Z0-9._]{5,29}$', username):
			return errorResponse(u"Username must be 6-30 char and not contain invalid char.")

		#comment this, to disable check captcha
		if settings.IS_RUNNING_UNIT_TEST is False:
			result=checkRecaptcha(request);
			if result is not True:
				return errorResponse(u"Unable to verify recaptcha!"); # errorResponse

		#save user
		user = User(username=username, email=email);
		user.set_password(password)
		try:
			user.save()
		except Exception as e:
			logging.error(u"Unable to create new user, error=%s"%(e));
			return errorResponse(u"Username already exist!")

		if referer:
			try: refererUser = User.objects.get(username=referer);
			except User.DoesNotExist: pass;
			else:
				user.profile.referer = refererUser;

		try:
			agency_id = int(request.COOKIES.get('agency_id', 0))
		except ValueError:
			agency_id = 0

		if agency_id>0: user.profile.referer2_id=agency_id;
		if request.META['REMOTE_ADDR']: user.profile.signup_ip=request.META['REMOTE_ADDR']

		user.profile.account_status = AccountStatus.emailNotActivated

		plan0_config = SystemConfigureController.getConfigure('plan0', settings.DEFAULT_PLAN_CONFIG)
		user.profile.plan_id = 0;
		user.profile.storage_space = plan0_config['storage'];
		user.profile.save()

		# EmailController.sendWelcomeToStoragonMail(user.email);
		EmailController.sendAccountActivationMail(request, user.email, user.id);

		# login user
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		return successResponse()

	else:
		raise Http404()


@signature_test()
def createTemporaryUser(request):
	""" Create a temporary account

	request.POST = {
		password:
	}

	response = {
		username: random_username,
		user_id: user.id
	}
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		password = getParamsOr400(request, 'password')

		random_username = 'temp_user_' + str(random.randint(10**8, 10**9))
		user = User.objects.create_user(random_username, random_username + '@nomail.com', password)
		user.profile.account_status = AccountStatus.temporary
		# user.profile.eumk=eumk;
		user.profile.storage_space = SystemConfigureController.getConfigure('freeUserStorageSpace', settings.INITIAL_USER_STORAGE_SPACE)  # settings.INITIAL_USER_STORAGE_SPACE

		user.profile.save()
		return successResponse({
			'username': random_username,
			'user_id': user.id,
		})
	else:
		raise Http404()


@signature_test()
def signupTemporaryUserAccount(request):
	""" Signup for a temporary account

	request.POST ={
		username : the random username return in createTemporaryUser ,
		password : the password define by user (or random generated on client),
		new_username : a new username to replace the random one,
		new_password : a new password to replace the random one,
		email : ,
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		username, password, new_username, new_password, email = getParamsOr400(request, 'username', 'password', 'new_username', 'new_password', 'email')

		user = authenticate(username=username, password=password)
		if user is None:
			return errorResponse("Username or password is not valid", code=0)

		user.username = new_username
		user.set_password(new_password)
		user.email = email

		try:
			user.save()
		except:
			return errorResponse("new_username is already used", code=0)

		user.profile.email = email
		user.profile.account_status = AccountStatus.emailNotActivated
		user.profile.storage_space = SystemConfigureController.getConfigure('freeUserStorageSpace', settings.INITIAL_USER_STORAGE_SPACE)  # settings.INITIAL_USER_STORAGE_SPACE

		user.profile.save()

		return successResponse()
	else:
		raise Http404()

@login_required_ajax()
@signature_test()
def resendActivationEmail(request):
	""" resendActivationEmail to user

	request.POST = {
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		if request.user.profile.account_status == AccountStatus.emailNotActivated:

			EmailController.sendAccountActivationMail(request, request.user.profile.email, request.user.id);

			return successResponse()
		else:
			return errorResponse(u"User email is already activated!");
	else:
		raise Http404()



@signature_test()
def sendResetPasswordEmail(request):
	""" resendActivationEmail to user

	request.POST = {
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		if request.user and request.user.is_authenticated:
			return errorResponse(u"You must logout before reset password.");
		else:
			email = getParamsOr400(request, 'email');

			try: user=User.objects.get(email=email);
			except User.DoesNotExist:
				return errorResponse(u"User email is not exist!");

			EmailController.sendResetPasswordMail(request, email, user.id);

			return successResponse()
	else:
		raise Http404()

@login_required_ajax()
@signature_test()
def applyToBecomeAffiliate(request):
	""" User applyToBecomeAffiliate

	request.POST = {
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		profile = request.user.profile;
		if not profile.account_type == AccountType.user:
			return errorResponse(u"Your account is not an user account!");

		if profile.account_status != AccountStatus.normal:
			return errorResponse(u"You need to activate your account before become affiliate");

		userapply=getObjectOrNone(UserApply,user=request.user, apply_type=ApplyType.becomeAffiliate, apply_status=ApplyStatus.processing);
		if userapply:
			return errorResponse(u"You have already apply to become affiliate, please wait for us to processing your application");

		website_address = getParamsOr400(request, ('website_address','') );

		if website_address:
			website_agency_domain = AffiliateController.verifyWebsiteOwner(request.user, website_address);
			if not website_agency_domain:
				return errorResponse(u"Unable to verify you are the owner of the website: %s"%(website_address));
			AffiliateController.addWebsiteAgency(request.user, website_agency_domain);

		application = UserApply(user=request.user, apply_type=ApplyType.becomeAffiliate);

		#make this an option in system configure
		if SystemConfigureController.getConfigure('autoAcceptAffiliateApply', False):
			application.apply_status = ApplyStatus.accepted; #auto accept

		application.save();

		return successResponse()
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
def applyToChangeAffiliateMode(request):
	""" User applyToChangeAffiliateMode

	request.POST = {
		affiliate_mode: ppd/pps
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		affiliate_mode = getParamsOr400(request, 'affiliate_mode');
		profile = request.user.profile;

		if profile.account_type not in [AccountType.affiliate, AccountType.affiliatePPD]:
			return errorResponse(u"You need to become affiliate first.");

		if affiliate_mode== 'ppd':
			applyType = ApplyType.becomeAffiliatePPD;
			if profile.account_type == AccountType.affiliatePPD:
				return errorResponse(u"You have already set to affiliate mode PPD.");
		else:
			applyType = ApplyType.becomeAffiliatePPS;
			if profile.account_type == AccountType.affiliate:
				return errorResponse(u"You have already set to affiliate mode PPS.");

		numberOfDayWaitToSwitchAffMode = SystemConfigureController.getConfigure('numberOfDayWaitToSwitchAffMode', 7)
		try:
			userapply=UserApply.objects.get(user=request.user, apply_type__in=[ApplyType.becomeAffiliatePPD,ApplyType.becomeAffiliatePPS], created_date__gt=timezone.now() - timezone.timedelta(days=numberOfDayWaitToSwitchAffMode));
		except UserApply.DoesNotExist:userapply=None;
		except UserApply.MultipleObjectsReturned:userapply=True;
		if userapply:
			return errorResponse(u"You have already switch aff mode in the last %s days"%(numberOfDayWaitToSwitchAffMode));

		application = UserApply(user=request.user, apply_type=applyType);#website_agency_domain

		#make this an option in system configure
		if SystemConfigureController.getConfigure('autoAcceptSwitchAffiliateModeApply', True):
			application.apply_status = ApplyStatus.accepted; #auto accept

		application.save();
		return successResponse()
	else:
		raise Http404()

@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def addWebsiteAgencyDomain(request):
	""" User applyToBecomeAffiliate

	request.POST = {
	}

	response = success or error
	"""
	if request.method == 'GET':
		raise Http404()
	elif request.method == 'POST':
		userProfile = request.user.profile;
		if not userProfile.isAffiliate():
			return errorResponse(u"Your account is not an affiliate account!");

		website_address = getParamsOr400(request, 'website_address');

		website_agency_domain = AffiliateController.verifyWebsiteOwner(request.user, website_address);
		if not website_agency_domain:
			return errorResponse(u"Unable to verify you are the owner of the website: %s"%(website_address));

		AffiliateController.addWebsiteAgency(request.user, website_agency_domain);

		return successResponse()
	else:
		raise Http404()


@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def getListWebsiteAgency(request):
	""" Get current user WebsiteAgency

	request.GET

	response = JSON list of AccountBalance format  [
		...
	]
	"""
	if request.method == 'GET':
		data = serializers.serialize('json', request.user.websiteagency_set.all())
		return successResponse(data, encode=False)
	elif request.method == 'POST':
		raise Http404()
	else:
		raise Http404()