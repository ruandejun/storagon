#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  views.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse

from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required

from system_configure.controllers import SystemConfigureController
from signals import post_verify_code
from models import SystemConfig


def verifyCode(request):
	if request.method == 'GET':
		code = request.GET.get('code');
		if not code: raise Http404();
		result = SystemConfigureController.verifyTemporaryCode(code);
		if result:
			post_verify_code.send(sender=SystemConfig, code=code, data=result);
			return shortcuts.redirect(settings.ACTIVATE_CODE_SUCCESS_REDIRECT);
		else:
			return HttpResponseBadRequest(u"Invalid code or code expired");
	else:
		raise Http404()
