#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  tests.py
#  
#
#  Created by TVA on 4/20/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django.test import TestCase, Client
from .controllers import SystemConfigureController
from django.urls import reverse


def urlopen(client, url, data=None, content_type=None, method=None):
	print("___request: " + str(url))
	if data is not None:
		print("___payload: " + str(data))
		if method=='PUT':
			response = client.put(url, data, content_type=content_type)
		elif method=='PATCH':
			response = client.patch(url, data, content_type=content_type)
		else: #POST
			response = client.post(url, data, content_type=content_type)
	else:
		if method=='HEAD':
			response = client.head(url)
		elif method=='DELETE':
			response = client.delete(url)
		elif method=='OPTIONS':
			response = client.options(url)
		else: #GET
			response = client.get(url)

	print("___response %s: %s" % (response.status_code, response.content[:200]))
	if response.status_code >= 400:
		raise Exception(response.status_code, response.content)
	return response.content


class TestSignal(TestCase):

	def setUp(self):
		self.client = Client()

	def test_verifyCode(self, show_test=True):
		if show_test: print (u"\n test_verifyCode:")
		code=SystemConfigureController.generateTemporaryCode(email=True);
		url = reverse('verifyCode')+'?code=%s'%code
		try: result=urlopen(self.client,url=url);
		except Exception as e:
			self.assertEqual(e[0],302);
