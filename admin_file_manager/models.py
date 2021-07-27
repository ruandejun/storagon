#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  models.py
#  
#
#  Created by TVA on 6/2/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

import datetime, os
from django.db import models
from django.conf import settings  # site setting

# Create your models here.
from django.contrib.auth.models import User


def get_upload_path(instance, fileName):
	relative_folder_path = instance.folder_path.replace(settings.MEDIA_ROOT+'/','')
	if instance.folder_name:
		correctName = instance.folder_name.strip()+'/'+fileName
	else:
		correctName = fileName
	try:os.remove(os.path.join(instance.folder_path,correctName))
	except:pass;
	return os.path.join(relative_folder_path,correctName)


class File(models.Model):
	created_date = models.DateTimeField(auto_now_add=True, db_index=True);
	modified_date = models.DateTimeField(auto_now=True, db_index=True);
	folder_path = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT,settings.FILE_MANAGER_ROOT_FOLDER), allow_folders=True, allow_files=False, recursive=True, max_length=255)
	folder_name = models.CharField(blank=True,null=True,max_length=255);
	file = models.FileField(upload_to=get_upload_path); # height_field='height', width_field='width'

	def __unicode__(self):
		return self.file.url