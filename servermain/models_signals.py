#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  models_signal
#  
#
#  Created by TVA on 3/30/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import base64
import hashlib
import random
import string

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from servermain.models import User, UserProfile, AccountBalance, Folder, UserFile, RealFile, ServerFile, UserApply, TransactionLog
from servermain.mongo_models import UserStorage, ServerFileStorage, Session
from servermain.controllers import FileController, EmailController, BalanceController
from storagon.enum import *
from storagon.tool import *
from storagon.PrivateAPI_SDK import SignalSDK
from system_configure.controllers import SystemConfigureController
from system_configure.models import SystemConfig
from system_configure.signals import post_verify_code
from munch import Munch

@receiver(post_verify_code, sender=SystemConfig)
def postVerifyCode(sender, **kwargs):
	code=kwargs['code'];
	data=kwargs['data'];

	if data.get('password_reset',False):
		#reset password
		try: user=User.objects.get(id=data.user_id);
		except User.DoesNotExist:
			logging.error(u"user_id=%s does not exist"%(data.user_id));
			return;

		new_password=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6));
		user.set_password(new_password);
		user.save();

		EmailController.sendNewPasswordNotifyMail(user.email, new_password);
		return;

	logging.warning(u"Unidentified code=%s"%(code));



### User
@receiver(post_save, sender=User)
def postSaveUser(sender, **kwargs):
	if kwargs.get('raw'):return;
	if kwargs['created']:

		user = kwargs['instance']
		# automaticaly create an UserProfile when a new User is saved
		newProfile = UserProfile()
		newProfile.user = user
		newProfile.id = user.id
		newProfile.full_name = user.username
		newProfile.email = user.email
		newProfile.account_status = AccountStatus.emailNotActivated
		newProfile.storage_space = settings.INITIAL_USER_STORAGE_SPACE
		newProfile.plan_expired=timezone.now();
		newProfile.eumk = base64.b64encode(hashlib.sha1(('eumk_%s' % (random.randint(0, 10**9))).encode('utf-8')).hexdigest()[:32].encode("utf-8"))  # random genereated eumk
		newProfile.save()
		# automaticaly create all type of balance for this user
		for balanceType in [BalanceType.credit,BalanceType.point,BalanceType.ppd]:
			balance = AccountBalance(user=user, balance_type=balanceType)
			balance.save()
		# automaticaly create UserStorage
		userStorage = UserStorage(pk=user.id, storage_used=0)
		userStorage.save()
		# automaticaly create recycle Folder
		recycleBinFolder = Folder(user=user, name='Recycle Bin', folder_type=FolderType.recycle)
		recycleBinFolder.save()


### UserFile
@receiver(post_save, sender=UserFile)
def postSaveUserFile(sender, **kwargs):
	if kwargs.get('raw'):return;
	userFile = kwargs['instance']
	if kwargs['created']:
		# automaticaly increase UserStorage file_count and storage_used atomicaly
		UserStorage.objects(pk=userFile.user.id).update_one(inc__file_count=1, inc__storage_used=userFile.realFile.file_size)
		original_file = FileController.autoReplaceUserFileWithSameNameInSameFolder(userFile);
		if original_file: userFile.id=original_file.id; #fix current saved file to become original_file


@receiver(post_delete, sender=UserFile)
def postDeleteUserFile(sender, **kwargs):
	userFile = kwargs['instance']
	# check for realFile deletion
	if userFile.realFile.userfile_set.count() == 0:
		logging.info(u"Create delete session for realFile_id=%s" % (userFile.realFile.id))

		# check whether a session has been created to delete this realFile exist or not, if not create one
		try:
			session, created = Session.objects.get_or_create(
				status=SessionStatus.waiting, type=SessionType.delete, fid=userFile.realFile.id, sid=userFile.realFile.serverFile.id, text=userFile.realFile.file_location, defaults={
				'status': SessionStatus.waiting, 'type': SessionType.delete, 'fid': userFile.realFile.id, 'sid': userFile.realFile.serverFile.id, 'text': userFile.realFile.file_location})
		except Session.MultipleObjectsReturned:
			created = False

		if created:  # a new delete sesion is created
			serverFile = userFile.realFile.serverFile
			storage, created = ServerFileStorage.objects.get_or_create(pk=serverFile.id, defaults={'pk': serverFile.id})
			from system_configure.controllers.SystemConfigureController import getConfigure
			initiateDeleteSessionProcessNumber = getConfigure('initiateDeleteSessionProcessNumber', 200)
			if storage.waiting_delete_session_count + 1 >= initiateDeleteSessionProcessNumber:
				storage.waiting_delete_session_count = 0
				storage.save()  # reset waiting_delete_session_count
				# send signal initiateDeleteSessionProcess to server file
				signalSDK = SignalSDK(serverFile.server_address, serverFile.id)
				result = signalSDK.initiateDeleteSessionProcess(initiateDeleteSessionProcessNumber)
				if not result:
					logging.error(u"servermain.models: postDeleteUserFile failed to send signal initiateDeleteSessionProcess")
			else:
				# automaticaly increase ServerFileStorage waiting_delete_session_count atomicaly
				ServerFileStorage.objects(pk=serverFile.id).update_one(inc__waiting_delete_session_count=1)

	# automaticaly decrease UserStorage file_count and storage_used atomicaly
	UserStorage.objects(pk=userFile.user.id).update_one(dec__file_count=1, dec__storage_used=userFile.realFile.file_size)


### Folder
@receiver(post_save, sender=Folder)
def postSaveFolder(sender, **kwargs):
	if kwargs.get('raw'):return;
	folder = kwargs['instance']
	if kwargs['created']:
		# automaticaly increase UserStorage folder_count atomicaly
		UserStorage.objects(pk=folder.user.id).update_one(inc__folder_count=1)
		original_folder = FileController.autoReplaceFolderWithSameNameInSameFolderExist(folder);
		if original_folder: folder.id=original_folder.id; #fix current saved folder to become original_folder

@receiver(post_delete, sender=Folder)
def postDeleteFolder(sender, **kwargs):
	folder = kwargs['instance']
	# automaticaly decrease UserStorage folder_count atomicaly
	UserStorage.objects(pk=folder.user.id).update_one(dec__folder_count=1)


### Realfile
@receiver(post_save, sender=RealFile)
def postSaveRealFile(sender, **kwargs):
	if kwargs.get('raw'):return;
	realFile = kwargs['instance']
	if kwargs['created']:
		# automaticaly increase ServerFileStorage file_count and storage_used atomicaly
		ServerFileStorage.objects(pk=realFile.serverFile.id).update_one(inc__file_count=1, inc__storage_used=realFile.file_size)


@receiver(post_delete, sender=RealFile)
def postDeleteRealFile(sender, **kwargs):
	realFile = kwargs['instance']
	# automaticaly decrease ServerFileStorage file_count and storage_used atomicaly
	ServerFileStorage.objects(pk=realFile.serverFile.id).update_one(dec__file_count=1, dec__storage_used=realFile.file_size)
	###
	# check whether a session has been created to delete this realFile exist or not, if not create one
	try:
		session, created = Session.objects.get_or_create(
	type=SessionType.delete, fid=realFile.id, sid=realFile.serverFile.id, text=realFile.file_location		, defaults={
		'status': SessionStatus.waiting, 'type': SessionType.delete, 'fid': realFile.id, 'sid': realFile.serverFile.id, 'text': realFile.file_location})
	except Session.MultipleObjectsReturned:
		pass
	else:
		if created:
			logging.warning(u"RealFile.postDeleteRealFile: realFile_id=%s has been deleted manually" % (realFile.id))
			# automaticaly increase ServerFileStorage waiting_delete_session_count atomicaly
			ServerFileStorage.objects(pk=realFile.serverFile.id).update_one(inc__waiting_delete_session_count=1)


### ServerFile
@receiver(post_save, sender=ServerFile)
def postSaveServerFile(sender, **kwargs):
	if kwargs.get('raw'):return;
	if kwargs['created']:
		serverFile = kwargs['instance']
		# automaticaly create ServerFileStorage
		serverFileStorage = ServerFileStorage(pk=serverFile.id, storage_used=0)
		serverFileStorage.save()


### UserApply
@receiver(post_save, sender=UserApply)
def postSaveUserApply(sender, **kwargs):
	if kwargs.get('raw'):return;
	# if kwargs['created']:
	userApply = kwargs['instance']
	if userApply.apply_status == ApplyStatus.accepted:
		# ApplyType.becomeAffiliate
		if userApply.apply_type in [ApplyType.becomeAffiliate, ApplyType.becomeAffiliatePPD, ApplyType.becomeAffiliatePPS]:
			profile = userApply.user.profile;
			if profile.account_type == AccountType.user:
				try: creditBalance = userApply.user.accountbalance_set.get(balance_type=BalanceType.credit);
				except AccountBalance.DoesNotExist:pass;
				except AccountBalance.MultipleObjectsReturned:pass;
				else:
					amount = SystemConfigureController.getConfigure('affBonusCredit',500);
					if BalanceController.chargeBalance(creditBalance.id, amount):
						tl=TransactionLog(balance=creditBalance,transaction_type=TransactionType.pay,invoice_bill=None,amount=amount)
						tl.data = json.dumps({
							'detail': 'bonus when become affiliate'
						});
						tl.save();


				#change limit of this user to aff limit
				if profile.getPlanID()>0:
					affLimitConfig = SystemConfigureController.getConfigure('affPremium', settings.DEFAULT_AFF_PREMIUM_CONFIG);
				else:
					affLimitConfig = SystemConfigureController.getConfigure('affFree', settings.DEFAULT_AFF_PREMIUM_CONFIG);

				profile.storage_space = affLimitConfig['storage'];

				EmailController.sendAffiliateActivatedNotifyMail(userApply.user.email);

			if userApply.apply_type in [ApplyType.becomeAffiliate, ApplyType.becomeAffiliatePPS]:
				profile.account_type = AccountType.affiliate;
			elif userApply.apply_type==ApplyType.becomeAffiliatePPD:
				profile.account_type = AccountType.affiliatePPD;

			profile.save();

		# ApplyType.payAffiliate
		if userApply.apply_type == ApplyType.payAffiliate:
			data = Munch(json.loads(userApply.data))
			if BalanceController.transferBalance(data.withdraw_balance_id,data.deposit_balance_id,data.withdraw_amount,data.deposit_amount):
				TransactionLog(transaction_type=TransactionType.transfer,
							balance_id=data.withdraw_balance_id,
							amount=-data.withdraw_amount).save();
				TransactionLog(transaction_type=TransactionType.transfer,
							balance_id=data.deposit_balance_id,
							amount=data.deposit_amount).save();
				logging.info(u"Pay Affiliate success with withdraw_amount=%s , deposit_amount=%s" % (data.withdraw_amount,data.deposit_amount));
			else:
				logging.error(u"Pay Affiliate failed with withdraw_amount=%s , deposit_amount=%s" % (data.withdraw_amount,data.deposit_amount));