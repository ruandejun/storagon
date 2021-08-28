#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  UserController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#
import random
import hashlib
from typing import NamedTuple

from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.conf import settings;

from servermain.models import RealFile, User, UserFile, UserProfile
from servermain.mongo_models import UserStorage, Session
from storagon.tool import *
from storagon.enum import *
from system_configure.controllers import SystemConfigureController


def calculateUserStorage(user_id):
	"""Recalculate an user storage

	:param user_id:
	:return:
	"""
	try:
		userStorage = UserStorage.objects.get(user_id=user_id)
	except UserStorage.DoesNotExist:
		userStorage = UserStorage(user_id=user_id)
		userStorage.save()

	try:
		user = User.objects.get(id=user_id)
	except User.DoesNotExist:
		return None

	fileCount = user.userfile_set.count()
	folderCount = user.folder_set.count()
	result = user.userfile_set.aggregate(Sum('realFile__file_size'))
	storageUsed = result['realFile__file_size__sum']

	upload_bandwidth = 0
	for session in Session.objects.filter(uid=user_id, type=SessionType.upload, status=SessionStatus.completed):
		upload_bandwidth += session.data.get('file_size', 0)

	download_bandwidth = 0
	for session in Session.objects.filter(uid=user_id, type=SessionType.download, status=SessionStatus.completed):
		download_bandwidth += session.data.get('file_size', 0)

	userStorage.file_count = fileCount
	userStorage.folder_count = folderCount
	userStorage.storage_used = storageUsed
	userStorage.upload_bandwidth = upload_bandwidth
	userStorage.download_bandwidth = download_bandwidth

	userStorage.calculated_date = timezone.now()

	userStorage.save()


	return userStorage


def checkUserCanUploadFile(user_id, file_size=0):
	""" Check wherether user has used up all storage or not

	:param user_id:
	:return: True = full, False = not full, None = not found userStorage / userProfile
	:rtype: bool
	"""

	try:
		userStorage = UserStorage.objects.get(user_id=user_id)
	except UserStorage.DoesNotExist:
		logging.error(u"coundn't find UserStorage of user_id=%s"%(user_id));
		return u"Couldn't find UserStorage for your account";

	try:
		userProfile = UserProfile.objects.get(user_id=user_id)
	except User.DoesNotExist:
		logging.error(u"coundn't find user_id=%s"%(user_id));
		return u"Couldn't find your account";

	disAllowList = [AccountStatus.banned]
	if SystemConfigureController.getConfigure('allowNotActivatedUserToUpload', True) is False:
		disAllowList += [AccountStatus.emailNotActivated]

	if userProfile.account_status in disAllowList:
		logging.debug(u"user_id=%s account is not permited to upload"%(user_id));
		return u"Your account is not permited to upload";

	if userProfile.storage_space > 0 and userStorage.storage_used + file_size >= userProfile.storage_space:
		logging.debug(u"user_id=%s don't have enough free space"%(user_id));
		return u"You don't have enough free space";

	if userProfile.account_type == AccountType.affiliate:
		planConfig = SystemConfigureController.getConfigure('affPremium', settings.DEFAULT_AFF_PREMIUM_CONFIG)
	else:
		planConfig = SystemConfigureController.getConfigure('plan%s' % (userProfile.getPlanID()), settings.DEFAULT_PLAN_CONFIG)

	if planConfig['upload_bandwidth']>0 and userStorage.upload_bandwidth >= planConfig['upload_bandwidth']:
		logging.debug(u"user_id=%s have exceed upload bandwidth"%(user_id));
		return u"You have exceed your upload bandwidth";

	return True;


def checkUserCanDownloadFile(user, userFile, REMOTE_ADDR=None):
	user_id = user.id;
	try:
		userStorage = UserStorage.objects.get(user_id=user_id)
	except UserStorage.DoesNotExist:
		logging.error(u"coundn't find UserStorage of user_id=%s"%(user_id));
		return u"Coundn't find UserStorage for your account"

	userProfile = user.profile;

	if userProfile.account_status == AccountStatus.banned:
		logging.debug(u"user_id=%s account is not permited to download"%(user_id));
		return u"Your account is not permited to download";

	if userFile.user == user: #if user is the owner of this file, then ignore these rule below
		return True;

	if userProfile.getPlanID() == 0 and userFile.file_mode == FileMode.premiumOnly:
		logging.debug(u"user_id=%s need to has premium status to download this file"%(user_id));
		return u"You need to has premium status to download this file";

	if userProfile.account_type == AccountType.affiliate:
		planConfig = SystemConfigureController.getConfigure('affPremium', settings.DEFAULT_AFF_PREMIUM_CONFIG)
	else:
		planConfig = SystemConfigureController.getConfigure('plan%s' % (userProfile.getPlanID()), settings.DEFAULT_PLAN_CONFIG)

	if planConfig['download_bandwidth'] >0 and userStorage.download_bandwidth >= planConfig['download_bandwidth']:
		logging.debug(u"user_id=%s have exceed download bandwidth"%(user_id));
		return u"You have exceed your download bandwidth. Buy premium please."

	if planConfig['download_concurrent'] > 0:
		countDownloadingSession = Session.objects.filter(
			type=SessionType.download,
			uid=user_id,
			status=SessionStatus.waiting,
			# data__ip_address=REMOTE_ADDR, used uid as mean of check
			created__gt=timezone.now() - timezone.timedelta(seconds=settings.MONGO_SESSION_EXPIRES)
		).count();
		if countDownloadingSession>=planConfig['download_concurrent']:
			logging.debug(u"user_id=%s have exceed number of concurent download %s>=%s "%(user_id, countDownloadingSession, planConfig['download_concurrent']));
			return u"You have exceed number of concurent download for today. Buy premium please."

	#check Free User Limit Per Day
	if userProfile.getPlanID() == 0:
		freeUserLimitPerDayConfig = SystemConfigureController.getConfigure('freeUserLimitPerDay', settings.DEFAULT_FREE_LIMIT_PER_DAY_CONFIG);

		completedSessionInPass24HourList = Session.objects.filter(
			type=SessionType.download,
			uid=user_id,
			status=SessionStatus.completed,
			created__gt=timezone.now()+timezone.timedelta() - timezone.timedelta(days=1)
		);

		count=0;
		for downloadSession in completedSessionInPass24HourList:
			if downloadSession.data['file_size'] >= freeUserLimitPerDayConfig['big_file_size']:
				count+=1;
				if count > freeUserLimitPerDayConfig['max_big_file_download']:
					return u"You have exceed number of big file download for today. Buy premium please."

	return True;


def checkGuestCanDownloadFile(userFile, REMOTE_ADDR=None):
	if not SystemConfigureController.getConfigure('allowGuestUserToDownload', True):
		return False;

	guestLimitConfig = SystemConfigureController.getConfigure('guestLimit', settings.DEFAULT_GUEST_LIMIT_CONFIG);
	if guestLimitConfig['download_concurrent'] > 0 and REMOTE_ADDR:
		countDownloadingSession =Session.objects.filter(
			type=SessionType.download,
			status=SessionStatus.waiting,
			data__ip_address=REMOTE_ADDR,
			created__gt=timezone.now() - timezone.timedelta(seconds=settings.MONGO_SESSION_EXPIRES)
		).count();
		if countDownloadingSession>=guestLimitConfig['download_concurrent']:
			logging.debug(u"guest user with ip=%s have exceed number of concurent download"%(REMOTE_ADDR));
			return u"You have exceed number of concurent download for today. Buy premium please."

	if userFile.file_mode == FileMode.premiumOnly:
		logging.debug(u"Guest user does't has premium status to download this file");
		return u"You need to has premium status to download this file";

	return True;


def generateAccountActivationCode(user_id, email):
	activation_code = hashlib.sha1(('storagon_activation_code_%s'%(random.randint(0, 1000000))).encode('utf-8')).hexdigest()[:8].upper()
	timeout = settings.ACCOUNT_ACTIVATION_EXPIRES;
	cache.set(activation_code, (user_id, email), timeout);
	return activation_code;


def verifyAccountActivation(activation_code):
	activate_info = cache.get(activation_code);
	if not activate_info:
		return False;
	user_id, email = activate_info;
	try:
		user=User.objects.get(id=user_id);
	except User.DoesNotExist:
		return False;
	else:
		user.is_active = True;
		user.email = email;
		user.save();
		user.profile.account_status = AccountStatus.normal;
		user.profile.email = email
		user.profile.save();
	cache.delete(activation_code);
	return True

