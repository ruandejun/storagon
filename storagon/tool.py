# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError, Http404

from django.conf import settings  # site setting
from django.core.cache import cache

# add logging
import logging, json, sys, os
# from django.core.exceptions import PermissionDenied as Http403
# from django.core.exceptions import SuspiciousOperation as Http400
from .browser import Browser

#/var/log/system.log
# logFilePath = getattr(settings, 'LOG_FILE_PATH', 'logging_local.log')
#
# logging.basicConfig(filename=logFilePath,
# 					filemode='a',
# 					format='%(asctime)s,%(msecs)d | %(name)s | %(levelname)s | %(filename)s->%(funcName)s: %(message)s',
# 					datefmt='%Y-%m-%d %H:%M:%S',
# 					level=logging.DEBUG)


from system_configure.controllers.Tool import *
