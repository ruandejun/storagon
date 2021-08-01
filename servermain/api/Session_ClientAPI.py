#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Session_ClientAPI.py
#
#
#  Created by V.Anh Tran on 11/29/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

import urllib
import datetime

from django import shortcuts
from django.http import *
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from mongoengine import Q
import jwt

from servermain.controllers import ServerFileController,UserController
from servermain.models import UserFile, Banlist, RealFile, Folder, User
from servermain.mongo_models import Session
from storagon.tool import *
from storagon.enum import *
from storagon.decorator import banned_check, login_required_ajax, signature_test
from system_configure.controllers import SystemConfigureController


def reverseString(s):
    d = [c for c in s]
    d.reverse();
    return ''.join(d);


@login_required_ajax()
@signature_test()
@user_passes_test(banned_check)
def createUploadSession(request):
    """ Create a new upload session

    request.POST = {
        file_name: required
        file_hash: required
        file_size
        file_name
        folder_id
        erfk: base64 encoded of real file key
    }

    response = {
        session_id : id of newly created session
        upload_link : Link to upload file to server file. Resumable, target: upload_link
    }

    or if file_hash is found
    response = {
        userFile_id : id of a new UserFile created on server using RealFile that have the same file_hash
    }

    """
    if request.method == 'GET':
        raise Http404()
    elif request.method == 'POST':
        file_hash, file_name, file_size, folder_id, erfk = getParamsOr400(request, 'file_hash', 'file_name', ('file_size', 0), ('folder_id', 0), ('erfk',''))

        if erfk:
            erfk = reverseString(erfk);

        if file_size < 0 or folder_id < 0:
            return HttpResponseBadRequest(u"file_size,folder_id")

        # check file_hash in banlist
        try:
            banData = Banlist.objects.get(pk=file_hash)
        except Banlist.DoesNotExist:
            pass
        else:  # check for banData is still activate
            if banData.enable and (banData.expires_date is None or banData.expires_date > timezone.now()):
                return errorResponse(u"This file_hash has been banned!", code=0)

        resultCheck=UserController.checkUserCanUploadFile(request.user.id, file_size);
        if resultCheck is not True:
            return errorResponse(u"You're not allowed to upload due to: %s"%(resultCheck), code=0);
        created=False
        try:
            uploadSession = Session.objects.get(
                type=SessionType.upload,
                status=SessionStatus.waiting,
                uid=request.user.id,
                data__file_hash=file_hash,
                # text=file_hash,
                created__gt=timezone.now() - timezone.timedelta(seconds=settings.MONGO_SESSION_EXPIRES)
            )
        except Session.DoesNotExist:
            defaults={
                'uid': request.user.id, 'type': SessionType.upload,
                # 'text': file_hash,
            }
            uploadSession = Session(uid=request.user.id,type=SessionType.upload)
            uploadSession.save()
            created=True



        # uploadSession = Session(uid=request.user.id, type=SessionType.upload)
        if created:
            uploadSession.data['file_hash'] = file_hash
            uploadSession.data['file_size'] = file_size
            uploadSession.data['file_name'] = file_name.encode('utf-8');
            uploadSession.data['erfk'] = erfk
            encryptResumeFileKey = None;
        else:
            uploadSession.data['file_name'] = file_name.encode('utf-8');
            encryptResumeFileKey = uploadSession.data['erfk'];
            uploadSession.created = timezone.now();

        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id)
            except Folder.DoesNotExist:
                return errorResponse(u"The folder is used for this uploadSession does not exist", code=0)
            if folder.user != request.user:
                return errorResponse(u"The folder is used for this uploadSession does not belong to current user", code=0)

            uploadSession.fid = folder_id
        else:
            folder_id = None

        serverFile = ServerFileController.getAvailableServerFileForUpload()
        if not serverFile:
            return errorResponse(u"no serverFile is available for upload", code=0)
        uploadSession.sid = serverFile.id

        try:
            duplicateFile = RealFile.objects.get(file_hash=file_hash)
        except RealFile.DoesNotExist:
            duplicateFile = None  # Normal state
        except RealFile.MultipleObjectsReturned:
            logging.warning(u"Found realfile duplicated for file_hash=%s" % (file_hash))
            duplicateFile = RealFile.objects.all().filter(file_hash=file_hash).first()
            # return errorResponse("Duplicated RealFile exist",code=11);

        if duplicateFile:
            uploadSession.status = SessionStatus.working
            uploadSession.data['duplicateFile_id'] = duplicateFile.id

        if SystemConfigureController.getConfigure('enableTrackingOfUserIPAddress', True):
            uploadSession.data['ip_address'] = request.META['REMOTE_ADDR']
            try:response = settings.geo_reader.country(uploadSession.data['ip_address']);
            except:pass;
            else:uploadSession.data['iso_code']=response.country.iso_code

        uploadSession.save()

        logging.info("createUploadSession: file_name=%s,file_size=%s,file_hash=%s to serverFile:%s" % (file_name, file_size, file_hash, serverFile))

        jwToken = jwt.encode(json.loads(uploadSession.to_json()), settings.SECRET_KEY, algorithm='HS256');

        upload_link = serverFile.server_address + reverse('resumable_upload', args=[str(uploadSession.id), jwToken])

        return successResponse({
            'session_id': str(uploadSession.id),
            'duplicated': (duplicateFile is not None),
            'encryptResumeFileKey': encryptResumeFileKey,
            'upload_link': upload_link
        })
    else:
        raise Http404()


@signature_test()
def createDownloadSession(request):
    """ Create a download session

    request.POST = {
        userFile_id: id of userfile
        download_type: int
    }

    response = {
        session_id : id of newly created session
        file_size : file_size of download file
        file_name : file_name of download file
        download_link : Link to download file from server file
    }

    """
    if request.method == 'GET':
        raise Http404()
    elif request.method == 'POST':
        userFile_id, download_type = getParamsOr400(request, ('userFile_id', int), ('download_type', 2))

        userFile = shortcuts.get_object_or_404(UserFile, pk=userFile_id)

        if request.user and request.user.is_authenticated:
            resultCheck = UserController.checkUserCanDownloadFile(request.user, userFile, request.META['REMOTE_ADDR']);
            if resultCheck is not True:
                return errorResponse(u"You're not allowed to download due to: %s"%(resultCheck), code=0);

        else:
            resultCheck = UserController.checkGuestCanDownloadFile(userFile, request.META['REMOTE_ADDR']);
            if resultCheck is not True:
                return errorResponse(u"You're not allowed to download due to: %s"%(resultCheck), code=0);

        # increase download_count (not atomicaly, and not accurate, should not use this property for bonus money)

        if request.user and request.user.is_authenticated:
            downloadSession, created = Session.objects.get_or_create(
                type=SessionType.download,
                status=SessionStatus.waiting,
                fid=userFile.id,
                uid=request.user.id,
                data__ip_address=request.META['REMOTE_ADDR'],
                created__gt=timezone.now() - timezone.timedelta(seconds=settings.MONGO_SESSION_EXPIRES),
                defaults={
                'fid': userFile.id, 'type': SessionType.download,
                }
            );
        else:
            created = True;
            downloadSession = Session(fid=userFile.id, type=SessionType.download)

        if created:
            pass;
        else:
            downloadSession.created = timezone.now();

        downloadSession.sid = userFile.realFile.serverFile.id #server download from
        downloadSession.oid = userFile.user.id #owner of file
        downloadSession.data['file_location'] = userFile.realFile.file_location
        downloadSession.data['file_size'] = userFile.realFile.file_size
        downloadSession.data['file_name'] = userFile.file_name

        if SystemConfigureController.getConfigure('enableTrackingOfUserIPAddress', True):
            downloadSession.data['ip_address'] = request.META['REMOTE_ADDR']
            try: response = settings.geo_reader.country(downloadSession.data['ip_address']);
            except: downloadSession.data['iso_code']='Unknow';
            else: downloadSession.data['iso_code']=response.country.iso_code
        else:
            downloadSession.data['ip_address'] = '10.0.0.1'

        downloadSession.data['website_url'] = request.COOKIES.get('website_url', '');
        downloadSession.data['website_origin'] = request.COOKIES.get('website_origin', '');

        if request.user and request.user.is_authenticated:
            downloadSession.uid = request.user.id
            #::type: UserProfile
            profile = request.user.profile;
            plan_id = profile.getPlanID();
            if plan_id==0 and request.user == userFile.user:
                plan_id = 1;# user is owner of this file, allow him to download as a premium user
            if profile.account_type == AccountType.affiliate and plan_id >0:
                planConfig = SystemConfigureController.getConfigure('affPremium', settings.DEFAULT_AFF_PREMIUM_CONFIG)
            else:
                planConfig = SystemConfigureController.getConfigure('plan%s' % (plan_id), settings.DEFAULT_PLAN_CONFIG)

            downloadSession.data['speed_limit'] = planConfig['download_speed']
            downloadSession.data['connection_limit'] = planConfig['download_connection']

        else:
            guestLimitConfig = SystemConfigureController.getConfigure('guestLimit', settings.DEFAULT_GUEST_LIMIT_CONFIG)
            downloadSession.data['speed_limit'] = guestLimitConfig['download_speed']
            downloadSession.data['connection_limit'] = guestLimitConfig['download_connection']

        downloadSession.data['download_type'] = download_type; #save download_type of Download

        if download_type==DownloadType.torrent:
            downloadSession.data['tracker_url'] = request.build_absolute_uri(reverse('PT_announce'))+'?session_id=%s'%downloadSession.id
            downloadSession.status = SessionStatus.working
        downloadSession.save()

        logging.info(
            "createDownloadSession: download_type=%s,file_name=%s,file_size=%s,file_location=%s from serverFile:%s" % (
            download_type,
            userFile.file_name,
            userFile.realFile.file_size,
            userFile.realFile.file_location,
            userFile.realFile.serverFile
        ))

        jwToken = jwt.encode(json.loads(downloadSession.to_json()), settings.SECRET_KEY, algorithm='HS256');

        # try: file_name_quote = urllib.quote(userFile.file_name)
        # except: file_name_quote = urllib.quote(unicode(userFile.file_name).decode('utf-8')); #userFile.file_name.encode('ascii', 'ignore')
        file_name_quote = userFile.file_name #.decode('utf-8');

        if download_type==DownloadType.torrent:
            download_link = userFile.realFile.serverFile.server_address+'/sf/torrent/'+str(downloadSession.id)+'/'+jwToken+'/'+file_name_quote;
        else:
            download_link = userFile.realFile.serverFile.server_address+'/sf/download/'+str(downloadSession.id)+'/'+jwToken+'/'+file_name_quote;

        return successResponse({'session_id': str(downloadSession.id),
            'file_size': downloadSession.data['file_size'],
            'file_name': downloadSession.data['file_name'],
            'download_link': download_link
        })
    else:
        raise Http404()


# @login_required_ajax()
@signature_test()
def createReport(request):
    """ Create a report session

    request.POST = {
        text:, #report identifier
        fid: #report file,
        sid: #report user,
        detail: #detail report,
    }

    response = {
        session_id : id of newly created session
    }
    """
    if request.method == 'GET':
        raise Http404()
    elif request.method == 'POST':
        text, fid, sid, detail = getParamsOr400(request, 'text', ('fid', 0), ('sid', 0), ('detail', ''))
        if fid <= 0 and sid <= 0:
            raise Http400()

        report = Session(uid=request.user.id, type=SessionType.report)
        report.text = text
        if sid > 0:
            report.sid = sid  # user_id
        if fid > 0:
            report.fid = fid
            # notify uploadFile user of DMCA report
            try:
                uploadFile = UserFile.objects.get(id=fid)
            except UserFile.DoesNotExist:
                return errorResponse(u"Reported file doesn't exists!", code=0)
            else:
                report.sid = uploadFile.user.id
                report.data['file_link'] = uploadFile.get_absolute_url(withFileKey=False);

        report.data['reporter_username'] = request.user.username

        report.data['detail'] = detail
        report.save()

        return successResponse({'session_id': str(report.id)})
    else:
        raise Http404()


@login_required_ajax()
@signature_test()
def sendInboxMessage(request):
    """ Create a report session

    request.POST = {
        text: message,
        sid: to_user_id,
        to_username: username of receiver
    }

    response = {
        session_id : id of newly created session
    }
    """
    if request.method == 'GET':
        raise Http404()
    elif request.method == 'POST':
        text, to_user_id, to_username = getParamsOr400(request, 'text', ('sid', 0), ('to_username', ''))
        if to_user_id <= 0 and to_username:
            try:
                to_user = User.objects.get(username=to_username)
            except User.DoesNotExist:
                print(u"user:%s does not exist!" % (to_username))
                raise Http400(u"user:%s does not exist!" % (to_username))
            else:
                to_user_id = to_user.id
        if to_user_id <= 0:
            raise Http400(u"sid")

        inboxMessage = Session(uid=request.user.id, type=SessionType.inbox)
        inboxMessage.text = text
        inboxMessage.sid = to_user_id
        inboxMessage.data['sender_username'] = request.user.username
        inboxMessage.save()

        return successResponse({'session_id': str(inboxMessage.id)})
    else:
        raise Http404()


@login_required_ajax()
@signature_test()
def getListSession(request):
    """ Get list session

    request.GET = {
        type: filter_type allow only these type SessionType.upload,SessionType.download,SessionType.report,SessionType.inbox
        status: filter_status #not required
        from_date: %Y-%m-%d #not required
        to_date: %Y-%m-%d #not required
    }

    response = bson JSON [{
        _id: {"$oid": "54881833df3a1a268573fb18"},
        type : Enum SessionType,
        uid : user id,
        fid : file_id UserFile and RealFile or folder_id
        sid : server_id
        status : Enum SessionStatus
        data : Dict contain session data
        text : Message
        created : DateTime
    }]
    """
    if request.method == 'GET':
        type, fid, oid, status, from_date_string, to_date_string = getParamsOr400(request, ('type', int), ('fid', 0), ('oid', 0), ('status', -1), ('from_date', ''), ('to_date', ''))

        from_date = timezone.now() - timezone.timedelta(days=30)
        if from_date_string:
            try:from_date = datetime.datetime.strptime(from_date_string, "%Y-%m-%d")
            except ValueError:pass;



        if type not in [SessionType.upload, SessionType.download, SessionType.report, SessionType.inbox]:
            return errorResponse(u"SessionType=%s is not allowed" % (type))

        getIPCountry=False
        query = Session.objects.all()
        query = query.filter(type=type).filter(created__gt=from_date)
        if status >= 0:
            query = query.filter(status=status)

        if fid > 0:
            userFile = getObjectOrNone(UserFile, id=fid);
            if not userFile:
                return errorResponse(u"UserFile with id=%s is not exist" % (fid))
            if userFile.user != request.user:
                return errorResponse(u"UserFile with id=%s is not belong to you" % (fid))
            query = query.filter(fid=fid)
        elif oid >0:
            if oid != request.user.id:
                return errorResponse(u"You can't get DownloadSession file of other user")
            query = query.filter(oid=oid)
            getIPCountry=True;
        else:
            if type == SessionType.report or type == SessionType.inbox:
                query = query.filter(Q(uid=request.user.id) | Q(sid=request.user.id))
            else:
                query = query.filter(uid=request.user.id)

        if to_date_string:
            today = timezone.now()
            try: to_date = datetime.datetime.strptime(to_date_string, "%Y-%m-%d")
            except ValueError: to_date=today;
            if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
                to_date = today  # in case client send to_date=today
            query = query.filter(created__lt=to_date)

        query = query.order_by('-created')

        if getIPCountry:
            for session in query:
                if not session.data.get('iso_code'):
                    try: response = settings.geo_reader.country(session.data['ip_address']);
                    except: session.data['iso_code']='Unknow';
                    else: session.data['iso_code']=response.country.iso_code
                    session.save();

        return successResponse(query.to_json(), encode=False)
    elif request.method == 'POST':
        raise Http404()
    else:
        raise Http404()
