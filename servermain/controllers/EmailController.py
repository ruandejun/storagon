#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  EmailController
#  
#
#  Created by TVA on 3/16/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.urls import reverse
from django.core.mail import send_mail
from django.template import Context, Template

from system_configure.controllers import SystemConfigureController
from storagon.tool import *
from . import UserController


def sendWelcomeToStoragonMail(toAddress):
	senderAddress = settings.STORAGON_MAIN_EMAIL_ADDRESS
	header = SystemConfigureController.getHTML('welcomeToStoragonMailHeader', default=u"Welcome to Storagon");

	html_body = SystemConfigureController.getHTML('welcomeToStoragonMailBody', default=u"Your account has been activated!");

	try:
		send_mail(header, html_body, senderAddress, [toAddress], html_message=html_body);
	except Exception as e:
		logging.error("send email from %s to %s error=%s"%(senderAddress, toAddress, e));
		return False;
	else:
		logging.info("send email success to: %s"%(toAddress));
	return True;


def sendAccountActivationMail(request, toAddress, user_id):
	senderAddress = settings.STORAGON_MAIN_EMAIL_ADDRESS
	header = SystemConfigureController.getHTML('accountActivationMaillHeader',default=u"Activation email from Storagon");

	activation_code = UserController.generateAccountActivationCode(user_id, toAddress);
	activate_link = request.build_absolute_uri(reverse('activateAccount')+'?activation_code=%s'%(activation_code));

	html_body = SystemConfigureController.getHTML('accountActivationMaillBody',
		default=u'Please follow this link to activate storagon: <a href="{{activate_link}}">{{activate_link}}</a>',
		activate_link=activate_link,
		);

	html_body += SystemConfigureController.getHTML('userTOSNotifyMaillBody',
		default=u'As an user of our website you are agree to these term of service below:<br/>'
				u'<a href="{{tos_link}}">Click this to read Term Of Service</a>',
		tos_link=request.build_absolute_uri('/#/tos'),
		);

	try:
		send_mail(header, html_body, senderAddress, [toAddress], html_message=html_body);
	except Exception as e:
		logging.error("send email from %s to %s error=%s"%(senderAddress, toAddress, e));
		return False;
	else:
		logging.info("send email success to: %s"%(toAddress));
	return True;


def sendAffiliateActivatedNotifyMail(toAddress):
	senderAddress = settings.STORAGON_MAIN_EMAIL_ADDRESS
	header = SystemConfigureController.getHTML('affiliateActivatedNotifyHeader', default=u"Affiliate account activated notify");

	html_body = SystemConfigureController.getHTML('affiliateActivatedNotifyBody', default=u"Your account affiliate status has been activated successfully!");
	html_body += SystemConfigureController.getHTML('affiliateTOSNotifyMaillBody',
		default=u"""As an affiliate of our website you are agree to these term of service below:<br/>
You are legally responsible for all of your uploaded data on our server
<br/>
We reserve the right to delete your files without the need to consult if we receive any feedback that your file copyright infringement or violation of law in your country and in the world
<br/>
We may also delete your files automatically if there are no downloads arising from that file within 45 days. For uploader who purchased premium plans, the limitation is 90 days
<br/>
We will not pay for your bills if you have actions that violate the rules seriously when using our services joining the affiliate program
		"""
		);

	try:
		send_mail(header, html_body, senderAddress, [toAddress], html_message=html_body);
	except Exception as e:
		logging.error("send email from %s to %s error=%s"%(senderAddress, toAddress, e));
		return False;
	else:
		logging.info("send email success to: %s"%(toAddress));
	return True;


def sendResetPasswordMail(request, toAddress, user_id):
	senderAddress = settings.STORAGON_MAIN_EMAIL_ADDRESS
	header = SystemConfigureController.getHTML('resetPasswordMailHeader', default=u"Reset Password Storagon Account");

	code = SystemConfigureController.generateTemporaryCode(user_id=user_id, password_reset=True);
	reset_link = request.build_absolute_uri(reverse('verifyCode')+'?code=%s'%(code));

	html_body = SystemConfigureController.getHTML('resetPasswordMailBody',
		default=u'Please follow this link to reset your storagon account password: <a href="{{link}}">{{link}}</a>',
		link=reset_link,
	)

	try:
		send_mail(header, html_body, senderAddress, [toAddress], html_message=html_body);
	except Exception as e:
		logging.error("send email from %s to %s error=%s"%(senderAddress, toAddress, e));
		return False;
	else:
		logging.info("send email success to: %s"%(toAddress));
	return True;


def sendNewPasswordNotifyMail(toAddress, new_password):
	senderAddress = settings.STORAGON_MAIN_EMAIL_ADDRESS
	header = SystemConfigureController.getHTML('notifyNewPasswordMailHeader', default=u"Your Storagon Account Password Has Been Reset");

	html_body = SystemConfigureController.getHTML('notifyNewPasswordMailBody',
		default=u'Your new storagon account password: {{password}}',
		password=new_password,
	)

	try:
		send_mail(header, html_body, senderAddress, [toAddress], html_message=html_body);
	except Exception as e:
		logging.error("send email from %s to %s error=%s"%(senderAddress, toAddress, e));
		return False;
	else:
		logging.info("send email success to: %s"%(toAddress));
	return True;