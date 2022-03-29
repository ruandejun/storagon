#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  FileController
#
#
#  Created by TVA on 2/27/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import re, base64
from Crypto.Cipher import AES

from storagon.tool import *
from servermain.models import Folder, UserFile


# def autoRenameFolderToAvoidConflict(user, parent_folder_id):
# 	try:
# 		query = Folder.objects.all().filter(
# 			user=user,
# 			parent_folder_id=parent_folder_id).order_by('modified_date')
# 	except Exception as e:
# 		raise Exception(u"Bad Query,error = %s" % (e))
# 	else:
# 		folderNameList = []
# 		for folder in query:
# 			if folder.name not in folderNameList:
# 				folderNameList += [folder.name]
# 				continue
# 			else:  # name conflict
# 				m = re.search(r'_(\d+)$', folder.name)
# 				if m:
# 					index = int(m.group(1)) + 1
# 					# cut the post fix part.
# 					folder.name = folder.name[:-len(m.group(0))]
# 				else:
# 					index = 1
#
# 				for i in range(index, index + 10**6):
# 					postFix = '_%s' % (i)
# 					if folder.name + postFix not in folderNameList:
# 						break
# 				else:
# 					raise Exception(
# 						u"Unable to find suitable index for postFix")
# 				folder.name += postFix
# 				folder.save()
#
# 				folderNameList += [folder.name]
#
#
# def autoRenameUserFileToAvoidConflict(user, folder_id):
# 	try:
# 		query = UserFile.objects.all().filter(
# 			user=user,
# 			folder_id=folder_id).order_by('modified_date')
# 	except Exception as e:
# 		raise Exception(u"Bad Query,error = %s" % (e))
# 	else:
# 		fileNameList = []
# 		for userfile in query:
# 			if userfile.file_name not in fileNameList:
# 				fileNameList += [userfile.file_name]
# 				continue
# 			else:  # name conflict
# 				m = re.search(r'_(\d+)\.(\w+)$', userfile.file_name)
# 				if m:
# 					index = int(m.group(1)) + 1
# 					filetype = m.group(2)
# 					# cut the post fix + filetype part.
# 					userfile.file_name = userfile.file_name[:-len(m.group(0))]
# 				else:
# 					m = re.search(r'\.(\w+)$', userfile.file_name)
# 					if m:
# 						filetype = m.group(1)
# 					else:
# 						filetype = ''
# 					index = 1
# 					userfile.file_name = userfile.file_name[
# 						:-len(m.group(0))]  # cut the filetype part
#
# 				for i in range(index, index + 10**6):
# 					postFix = '_%s' % (i)
# 					if userfile.file_name + postFix + '.' + filetype not in fileNameList:
# 						break
# 				else:
# 					raise Exception(
# 						u"Unable to find suitable index for postFix")
# 				userfile.file_name += postFix + '.' + filetype
# 				userfile.save()
#
# 				fileNameList += [userfile.file_name]


def autoReplaceUserFileWithSameNameInSameFolder(userFile):
	try:
		query = UserFile.objects.all().filter(
			user=userFile.user,
			folder_id=userFile.folder_id,
			file_name=userFile.file_name).order_by('modified_date')
	except Exception as e:
		raise Exception(u"Bad Query,error = %s" % (e))
	else:
		index=0;
		first_file=None;
		for file in query:
			if index==0:#first file, replace realfile
				file.realFile_id=userFile.realFile_id;
				if settings.ENABLE_ENCRYPTION :file.erfk = userFile.erfk;
				file.save();
				first_file=file;
			else:#other file, remove.
				file.delete()
			index+=1;
		if index<=1:return None;
		return first_file;


def checkFolderWithSameNameInSameFolderExist(folder):
	try:
		folder = Folder.objects.get(user=folder.user, name=folder.name, parent_folder=folder.parent_folder);
	except Folder.DoesNotExist:
		return None;
	except Folder.MultipleObjectsReturned:
		return Folder.objects.filter(user=folder.user, name=folder.name, parent_folder=folder.parent_folder).first();
	return folder;


def autoReplaceFolderWithSameNameInSameFolderExist(folder):
	try:
		folder = Folder.objects.get(user=folder.user, name=folder.name, parent_folder=folder.parent_folder);
	except Folder.DoesNotExist:
		return None;
	except Folder.MultipleObjectsReturned:
		firstFolder=None
		for folder in Folder.objects.filter(user=folder.user, name=folder.name, parent_folder=folder.parent_folder).order_by('created_date'):
			if not firstFolder:
				firstFolder=folder;
			else:
				folder.delete();
		return firstFolder;
	return None;


def autoMergeFolderWithSameNameInSameFolder(folder):
	try:
		query = Folder.objects.all().filter(
			user=folder.user,
			parent_folder_id=folder.parent_folder_id,
			name=folder.name).order_by('modified_date')
	except Exception as e:
		raise Exception(u"Bad Query,error = %s" % (e))
	else:
		if query.count() <=1: return;
		#try to merge if there are 2 folder or more with same name
		firstFolder = query.first();
		if firstFolder.id != folder.id:
			mergeFolder(firstFolder, folder);
			folder.delete();


def mergeFolder(originalFolder, mergeFolder):
	logging.debug("Merge folder %s to original folder %s"%(mergeFolder, originalFolder));

	for file in mergeFolder.fileList.all():
		file.folder_id = originalFolder.id;
		file.save();
		autoReplaceUserFileWithSameNameInSameFolder(file);

	for folder in mergeFolder.subFolderList.all():
		folder.parent_folder_id = originalFolder.id;
		folder.save();
		autoMergeFolderWithSameNameInSameFolder(folder);


def backTraceFolder(folder):
	if folder.parent_folder is None: return [folder];
	return backTraceFolder(folder.parent_folder)+[folder];


def decryptERFK(userFile, eumk=None):
	if userFile.erfk:
		if not eumk: eumk = base64.b64decode(userFile.user.profile.eumk)
		try:
			cipher = AES.new(eumk, AES.MODE_ECB)
			erfk = cipher.decrypt(base64.b64decode(userFile.erfk))
		except:
			return None;
		if not re.search(r'[0-9a-f]{32}', erfk):
			return None;

		return erfk;

	return None;


def encryptERFK(erfk, user):
	eumk = base64.b64decode(user.profile.eumk)
	cipher = AES.new(eumk, AES.MODE_ECB)
	erfk = base64.b64encode(cipher.encrypt(erfk));
	return erfk;


def copyFile(userFileQuerySet, secondOwner, copyToFolder=None):
	success = 0;

	if copyToFolder is not None and copyToFolder.user!=secondOwner:
		raise Exception(u"copyToFolder=%s not belong to secondOwner=%s"%(copyToFolder, secondOwner));

	for userFile in userFileQuerySet:
		copyUserFile = UserFile(user=secondOwner);
		copyUserFile.file_name = userFile.file_name;
		copyUserFile.realFile = userFile.realFile;

		copyUserFile.folder = copyToFolder;

		if settings.ENABLE_ENCRYPTION:#recencrypt erfk
			erfk = decryptERFK(userFile);
			copyUserFile.erfk = encryptERFK(erfk, secondOwner);

		copyUserFile.save();
		success+=1;

	return success;



