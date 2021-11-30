#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  tasks.py
#
#
#  Created by V.Anh Tran on 01/29/15.
#  Copyright (c) 2015 Storagon. All rights reserved.
#

from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings')

app = Celery('storagon')
# app.conf.broker_url = 'redis://default:hanoi123@redis:6379/0'
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
