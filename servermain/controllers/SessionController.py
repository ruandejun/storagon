#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  SessionController
#
#
#  Created by TVA on 1/23/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import json
from storagon.enum import *
from servermain.models import Session

def createMoveSession(currentUser, serverFile, queryset):
	""" create move realfile sessions

	:param currentUser:
	:param serverFile:
	:param queryset:
	:return:
	"""
	count = 0

	for realFile in queryset:
		if not realFile:
			continue

		#uncomment this, to avoid move file in a same serverFile
		if realFile.serverFile_id == serverFile.id: continue

		try:
			session, created = Session.objects.get_or_create(type=SessionType.move, status=SessionStatus.waiting, fid=realFile.id, sid=realFile.serverFile.id, text=realFile.file_location				, defaults={
					'status': SessionStatus.waiting, 'type': SessionType.move,
					'uid': currentUser.id, 'fid': realFile.id, 'sid': serverFile.id,
					'text': realFile.file_location,
					'data': {
						'file_location': realFile.file_location,
						'old_server_id': realFile.serverFile.id,
						'old_server_address': realFile.serverFile.server_address,
						'new_server_id': serverFile.id,
						'new_server_address': serverFile.server_address,
					}
				}
			)
		except Session.MultipleObjectsReturned:
			pass

		if created:
			count += 1

	return count

# def createMoveSession(currentUser, serverFile, queryset):
# 	""" create move realfile sessions
#
# 	:param currentUser:
# 	:param serverFile:
# 	:param queryset:
# 	:return:
# 	"""
# 	count = 0
# 	try:
# 		ssh_info = json.loads(serverFile.ssh_info)
# 		ssh_host = ssh_info['host']
# 		ssh_port = ssh_info['port']
# 		ssh_username = ssh_info['username']
# 		ssh_password = ssh_info['password']
# 	except Exception as e:
# 		return u"ServerFile.ssh_info is mailformed: %s" % (e)
#
# 	for realFile in queryset:
# 		if not realFile:
# 			continue
# 		if realFile.serverFile_id == serverFile.id:
# 			continue
#
# 		try:
# 			session, created = Session.objects.get_or_create(type=SessionType.move, status=SessionStatus.waiting, fid=realFile.id, sid=realFile.serverFile.id, text=realFile.file_location				, defaults={
# 					'status': SessionStatus.waiting, 'type': SessionType.move,
# 					'uid': currentUser.id, 'fid': realFile.id, 'sid': realFile.serverFile.id,
# 					'text': realFile.file_location,
# 					'data': {
# 						'file_location': realFile.file_location,
# 						'old_server_id': realFile.serverFile.id,
# 						'new_server_id': serverFile.id,
# 						# SSH info of new_server to use sftp
# 						'ssh_host': ssh_host,
# 						'ssh_port': ssh_port,
# 						'ssh_username': ssh_username,
# 						'ssh_password': ssh_password,
# 						'ssh_rsa_private_key': serverFile.rsa_private_key,
# 						'media_path': serverFile.media_path,
# 					}
# 				}
# 			)
# 		except Session.MultipleObjectsReturned:
# 			pass
#
# 		if created:
# 			count += 1
#
# 	return count
