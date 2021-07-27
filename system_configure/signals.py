#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  signals.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.dispatch import Signal

post_verify_code = Signal(providing_args=['code','data']);