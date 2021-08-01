#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  decorator
#
#
#  Created by TVA on 12/15/14.
#  Copyright (c) 2014 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse

from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt, csrf_protect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import REDIRECT_FIELD_NAME
#
# from functools import wraps
# from django.core.exceptions import PermissionDenied
# from django.utils.decorators import available_attrs
# from django.utils.encoding import force_str
import hashlib
# import urllib
from urllib.parse import urlencode, quote_plus


from storagon.enum import *


def signature_test():
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        # @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            # request=HttpRequest();
            signature = request.META.get('HTTP_SIGNATURE_AUTHORIZATION')
            if not signature:
                # print request.META;
                return HttpResponseForbidden(u"Signature is required!")

            if request.method == 'GET':
                params = request.get_full_path()
                prefix='http://'
                if request.is_secure(): prefix='https://'
                params2 = prefix + request.get_host() + request.get_full_path(); #request.build_absolute_uri(params)

            elif request.method == 'POST':
                params2 = request.body  # case 2
                dataItems = request.POST.items()
                dataItems = sorted(dataItems)
                # dataItems.sort()
                #convert unicode to fix urlencode error
                params = urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in dataItems]);
                # params = urllib.urlencode(dataItems)  # case 1
            else:
                return HttpResponseForbidden(u"Invalid Method")
            print('params==',params)
            print('params2==',params2.encode('utf-8'))
            correct_signature = hashlib.md5(str(settings.SECRET_KEY + str(params)).encode('utf-8')).hexdigest()
            if correct_signature != signature:
                # print params,'\n',params2
                correct_signature2 = hashlib.md5(str(settings.SECRET_KEY + str(params2.encode('utf-8')).encode('utf-8')).hexdigest()
                if correct_signature2 != signature:
                    return HttpResponseForbidden(u"correct_signature=%s or %s, but signature=%s" % (correct_signature, correct_signature2, signature))
                    # return HttpResponseForbidden("Invalid Signature");

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def login_required_ajax():
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user and request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse(status=401)
        return _wrapped_view
    return decorator


def banned_check(user):
    if not user or not user.is_authenticated:
        return False  # guest users are not allowed
    if user.profile.account_status == AccountStatus.banned:
        return False
    return True
