#!/usr/bin/python
# -*- coding: utf-8 -*-
#



from django.conf.urls import url
from .Commission_Api import *

urlpatterns = [
	url(r'^get_commission/', get_commission, name='get_commission'),

]