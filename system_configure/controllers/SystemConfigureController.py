#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  SystemConfigureController.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import random, hashlib, json, yaml

from django.utils import timezone
from django.core.cache import cache
from django.conf import settings;
from munch import Munch
from django.template import Context, Template
from system_configure.models import SystemConfig,TemplateHTML


def getConfigure(key, default='', JSON=False, YAML=False, BUNCH=False):
	overideEncode = getattr(settings,'SYSTEM_CONFIG_ENCODE_OVERIDE');
	if overideEncode is not None:
		JSON=overideEncode.get('JSON',JSON);
		YAML=overideEncode.get('YAML',YAML);
		BUNCH=overideEncode.get('BUNCH',BUNCH);

	data_default=default;
	if JSON: data_default=json.dumps(default);
	elif YAML: data_default=yaml.dump(default, default_flow_style=False, default_style='')

	config, created = SystemConfig.objects.get_or_create(pk=key, defaults={'key': key, 'value': data_default})
	result = config.value;

	if JSON:
		result = json.loads(config.value);
	elif YAML:
		result = yaml.safe_load(config.value);

	if BUNCH and isinstance(result,dict):
		result = Munch.fromDict(result)

	return result


# def setConfigure(key, value, JSON=False, YAML=False, updateDict=False):
# 	config, created = SystemConfig.objects.get_or_create(pk=key, defaults={'key': key, 'value': value})
#
# 	if not created:
# 		if JSON:
# 			if updateDict and isinstance(value, dict):  # update value with current data first
# 				value.update(json.loads(config.value))
# 			# save new value
# 			config.value = json.dumps(value)
# 		else:
# 			config.value = value
# 		config.save()
#
# 	if JSON:
# 		return json.loads(config.value)
# 	return config.value


def getHTML(key, **kwargs):
	default=kwargs.pop('default')
	templateHTML, created = TemplateHTML.objects.get_or_create(pk=key, defaults={'key': key, 'body': default})

	# changed = False;
	# if len(kwargs)>0:
	# 	for context_name in kwargs:
	# 		context_insert = '{{%s}}'%context_name;
	# 		if context_insert not in templateHTML.description:
	# 			templateHTML+=' '+context_insert;
	# 			changed=True;
	# if changed:
	# 	templateHTML.save();

	context = Context(kwargs);
	return Template(templateHTML.body).render(context);


def setHTML(key, body):
	templateHTML, created = TemplateHTML.objects.get_or_create(pk=key, defaults={'key': key, 'body': body})
	if not created:
		templateHTML.body = body
		templateHTML.save()
	return templateHTML.body;


def generateTemporaryCode(**kwargs):
	temp_code = hashlib.sha1(('temporary_code_%s'%(random.randint(0, 10**9))).encode()).hexdigest()[:10].upper()
	timeout = settings.TEMPORARY_CODE_EXPIRES;
	cache.set(temp_code, kwargs, timeout);
	return temp_code;


def verifyTemporaryCode(temp_code):
	data = cache.get(temp_code);
	cache.delete(temp_code);
	if not data:return None;
	return Munch.fromDict(data);




