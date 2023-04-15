#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  DefaultSettings.py
#  
#
#
from django.conf import settings


MONEY_MAX_DIGITS = getattr(settings, 'MONEY_MAX_DIGITS', 24)
MONEY_DECIMAL_PLACES = getattr(settings, 'MONEY_DECIMAL_PLACES', 2)
XRATE_MAX_DIGITS = getattr(settings, 'XRATE_MAX_DIGITS', 15)
XRATE_DECIMAL_PLACES = getattr(settings, 'XRATE_DECIMAL_PLACES', 0)
