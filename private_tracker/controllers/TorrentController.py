#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  TorrentController
#  
#
#  Created by TVA on 5/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse

from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required

from system_configure.controllers.Tool import *

import os, bencode, time, subprocess


def makeTorrentFile(announce_url,file_name,torrent_path,web_seed_url, file_path):
	#-p = private mktorrent
	#cmd = u"mktorrent -a %s -n '%s' -o %s -w %s %s"%(announce_url, file_name, torrent_path, web_seed_url, file_path);
	# result = os.system(cmd);
	cmd = ["mktorrent", "-a", "announce_url", "-n", file_name, "-o", torrent_path, "-w", web_seed_url, file_path];
	result = subprocess.call(cmd);
	if result!=0:
		logging.error(u"Unable to create torrent file, cmd=%s"%cmd);
	else:
		time.sleep(1);

	return result;


def editTorrentFile(torrentPath,newTorrentPath,announce_url,file_name,url_list):
	with open(torrentPath) as f:
		torrentData = bencode.bdecode(f.read());
		f.close();

	torrentData['announce']=str(announce_url);
	torrentData['info']['name']= file_name.encode('utf-8'); #str(file_name); #
	torrentData['url-list']=str(url_list);

	with open(newTorrentPath,'w+') as f:
		f.write(bencode.bencode(torrentData));
		f.close();

	time.sleep(1);