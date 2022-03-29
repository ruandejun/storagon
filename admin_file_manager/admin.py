#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  admin.py
#  
#
#  Created by TVA on 6/2/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.contrib import admin
# Register your models here.
from .models import File

admin.site.register(File)
