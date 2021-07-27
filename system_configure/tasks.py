#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  tasks.py
#  
#
#  Created by TVA on 4/26/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import subprocess,logging

from celery import shared_task


@shared_task
def runCMD(cmd,inputText=None):
	""" Run CMD
	:param cmd: CMD
	:param inputText: input pass to CMD as from stdin
	:return:
	"""
	# result=os.system(cmd);
	p = subprocess.Popen(cmd, shell=True,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)

	out, err = p.communicate(input=inputText)

	logging.info(u"Out=%s cmd=%s"%(out,cmd));
	if err: logging.error(u"Error=%s inputText=%s cmd=%s"%(err,inputText,cmd))

	return out;