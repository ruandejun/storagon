import random
import re
import datetime
import hashlib
import string
import json
import urllib
import base64

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings  # site setting
from django.core import mail

# from Crypto.Cipher import AES
from munch import Munch

from servermain.models import User, ServerFile, RealFile, UserFile, Folder, Banlist, UserApply, WebsiteAgency, AccountBalance
from servermain.mongo_models import Session, UserStorage, ServerFileStorage
from storagon.enum import *
from servermain.controllers import PaymentController,UserController, AffiliateController
import argparse
from system_configure.controllers import SystemConfigureController


def reverseString(s):
	d = [c for c in s]
	d.reverse();
	return ''.join(d);


def urlopen(client, url, data=None, content_type=None, add_security_header=True):
	print("___request: " + str(url))
	if data is not None:
		print("___payload: " + str(data))

		if not add_security_header:
			if content_type:
				response = client.post(url, data, content_type)
			else:
				response = client.post(url, data)
		else:
			# print urllib.parse.urlencode(data);

			if content_type:
				authorizationHeader = hashlib.md5(str(settings.SECRET_KEY + data).encode('utf-8')).hexdigest()
				# print 'data=',data;
				response = client.post(url, data, content_type, HTTP_SIGNATURE_AUTHORIZATION=authorizationHeader)
			else:
				dataItems = data.items()
				dataItems = sorted(dataItems)
				authorizationHeader = hashlib.md5(str(settings.SECRET_KEY + urllib.parse.urlencode(dataItems)).encode('utf-8')).hexdigest()
				# print 'urlencode(data)=',urllib.parse.urlencode(dataItems);
				response = client.post(url, data, HTTP_SIGNATURE_AUTHORIZATION=authorizationHeader)

	else:
		if not add_security_header:
			response = client.get(url)
		else:
			authorizationHeader = hashlib.md5(str(settings.SECRET_KEY + url).encode('utf-8')).hexdigest()
			response = client.get(url, HTTP_SIGNATURE_AUTHORIZATION=authorizationHeader)

	print("___response %s: %s" % (response.status_code, response.content[:200]))
	if response.status_code != 200:
		raise Exception(str(response.status_code), response.content)
	return response.content

serverMain = 'http://127.0.0.1:8080'

# Create your tests here.


class TestSession(TestCase):

	def setUp(self):
		self.client = Client()
		file_size = 123456
		self.serverFile = serverFile = ServerFile(name='test', ip_address='127.0.0.1:8080', server_address='http://127.0.0.1:8080', total_storage=1024 * 1024 * 1024 * 1024)
		self.serverFile.save()

		self.serverFile2 = ServerFile(name='test2', ip_address='127.0.0.1:8080', server_address='http://127.0.0.1:8080', total_storage=1024 * 1024 * 1024 * 1024, priority=2)
		self.serverFile2.save()

		self.realFile = realFile = RealFile(serverFile=serverFile, file_location='/2015/1/1/abczyx', file_size=file_size,
										file_hash=hashlib.md5(str(datetime.datetime.now()).encode('utf-8')).hexdigest())
		self.realFile.save()

		serverStorage = ServerFileStorage.objects.get(serverFile_id=serverFile.id)
		self.assertEqual(serverStorage.storage_used, file_size)

		self.user = User(username='test_session_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.save()

		self.userFile = UserFile(realFile=realFile, file_name='xyzcba.mp4', user=self.user)
		self.userFile.save()

		userStorage = UserStorage.objects.get(pk=self.user.id)
		self.assertEqual(userStorage.storage_used, file_size)

		uploadSession = Session(type=SessionType.upload, status=SessionStatus.completed, uid=self.user.id, sid=self.serverFile.id,
								data={'file_hash': self.realFile.file_hash, 'file_size': self.realFile.file_size,
									  'file_name': self.userFile.file_name, 'erfk': ''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
								}, text=str(self.realFile.id))
		uploadSession.save()

		self.client.login(username=self.user.username, password='123456')

	def test_createUploadSession(self, show_test=True):
		if show_test:
			print(u"\n test_createUploadSession:")
		url = reverse('Session_ClientAPI:createUploadSession')
		data = {
			'file_hash': hashlib.md5(str(datetime.datetime.now()).encode('utf-8')).hexdigest(),
			'file_size': random.randint(10**4, 10**6),
			'file_name': ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20)),
			'folder': 0,
			'erfk': reverseString(''.join(random.choices(string.ascii_uppercase + string.digits, k=32))),
		}
		# # folder_id wrong check
		# with self.assertRaisesMessage(Exception, '500'):
		# 	html = urlopen(self.client, url, data)
		# # except Exception as e:
		# # 	self.assertEqual(e[0], 500)

		# normal
		data['folder'] = ''
		html = urlopen(self.client, url, data)
		result = json.loads(html)

		session_id = result['session_id']
		upload_session = Session.objects.get(id=session_id)
		self.assertNotEqual(upload_session, None)

		# same file_hash check
		data['file_hash'] = self.realFile.file_hash
		html = urlopen(self.client, url, data)
		result = json.loads(html)

		session_id = result['session_id']
		upload_session2 = Session.objects.get(id=session_id)
		self.assertNotEqual(upload_session2, None)
		self.assertNotEqual(upload_session2.data.get('duplicateFile_id'), None)

		return upload_session, upload_session2

	def test_createDownloadSession(self, show_test=True):
		if show_test:
			print(u"\n test_createDownloadSession:")
		url = reverse('Session_ClientAPI:createDownloadSession')
		data = {
			'userFile_id': self.userFile.id,
		}

		html = urlopen(self.client, url, data)
		# print html;

		result = json.loads(html)

		session_id = result['session_id']
		session = Session.objects.get(id=session_id)
		self.assertNotEqual(session, None)
		return session

	def test_addFile(self, show_test=True):
		if show_test:
			print(u"\n test_addFile:")
		upload_session, upload_session2 = self.test_createUploadSession(False)
		url = reverse('File_PrivateAPI:addFile')
		file_location = '/2014/12/24/testfilelocation' + str(random.randint(10**6, 10**7))
		data = {
			'upload_session_id': str(upload_session.id),
			'file_location': file_location,
			'file_name': upload_session.data['file_name'],
			'file_size': upload_session.data['file_size'],
		}
		html = urlopen(self.client, url, data)
		result = json.loads(html)
		userFile = UserFile.objects.get(id=result['userFile_id'])
		realFile = RealFile.objects.get(file_hash=upload_session.data['file_hash'])
		self.assertEqual(userFile.realFile_id, realFile.id)

		storage = UserStorage.objects.get(pk=self.user.id)
		self.assertEqual(storage.upload_bandwidth, upload_session.data['file_size'])

		return file_location

	def test_addDuplicateFile(self, show_test=True):
		if show_test:
			print(u"\n test_addDuplicateFile:")
		upload_session, upload_session2 = self.test_createUploadSession(False)
		url = reverse('File_PrivateAPI:addDuplicateFile')

		data = {
			'upload_session_id': str(upload_session2.id),
		}

		html = urlopen(self.client, url, data)
		result = json.loads(html)
		userFile = UserFile.objects.get(id=result['userFile_id'])
		realFile = RealFile.objects.get(file_hash=upload_session2.data['file_hash'])
		self.assertEqual(userFile.realFile_id, realFile.id)
		self.assertEqual(self.realFile.id, realFile.id)

		return

	def test_getSession(self, show_test=True):
		if show_test:
			print(u"\n test_getSession:")
		download_session = self.test_createDownloadSession(False)
		url = reverse('Session_PrivateAPI:getSession') + '?session_id=%s' % (str(download_session.id))
		html = urlopen(self.client, url)
		session = Session.from_json(html)
		self.assertNotEqual(session, None)
		self.assertEqual(session.id, download_session.id)
		# print session;

		return session

	def test_listSession(self, show_test=True):
		if show_test:
			print(u"\n test_listSession:")
		download_session = self.test_createDownloadSession(False)
		url = reverse('Session_PrivateAPI:listSession') + '?type=%s&status=%s' % (SessionType.download, SessionStatus.waiting)
		html = urlopen(self.client, url)
		# print html;
		sessionList = [Session.from_json(json.dumps(sessionData)) for sessionData in json.loads(html)]
		self.assertGreater(len(sessionList), 0)
		# for session in sessionList:print session;
		self.assertEqual(sessionList[0].id, download_session.id)

		return sessionList

	def test_autoCreateDeleteSession(self, show_test=True):
		if show_test:
			print(u"\n test_autoCreateDeleteSession:")
		self.userFile.delete()

		userStorage = UserStorage.objects.get(pk=self.user.id)
		self.assertEqual(userStorage.storage_used, 0)

		realFile = RealFile(serverFile=self.serverFile, file_location='/2015/1/1/abczyx', file_size=123654)
		realFile.save()
		realFile_id = realFile.id
		realFile.delete()

		url = reverse('Session_PrivateAPI:listSession') + '?type=%s&status=%s' % (SessionType.delete, SessionStatus.waiting)
		html = urlopen(self.client, url)
		sessionList = [Session.from_json(json.dumps(sessionData)) for sessionData in json.loads(html)]
		self.assertEqual(len(sessionList), 2)

		self.assertEqual(sessionList[1].text, self.userFile.realFile.file_location)
		self.assertEqual(sessionList[1].fid, self.userFile.realFile.id)
		self.assertEqual(sessionList[0].fid, realFile_id)

		storage = ServerFileStorage.objects.get(pk=self.serverFile.id)
		# self.assertGreater(storage.waiting_delete_session_count,0);
		self.assertEqual(len(sessionList), storage.waiting_delete_session_count)

		return len(sessionList)

	def test_doneSession(self, show_test=True):
		if show_test: print(u"\n test_doneSession:")

		sessionList = self.test_listSession(False)

		data = urllib.parse.urlencode(
			[('session_id', session.id) for session in sessionList]
			+ [('status', SessionStatus.completed)]
		)
		url = reverse('Session_PrivateAPI:doneSession')
		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		# count session
		url = reverse('Session_PrivateAPI:listSession') + '?type=%s&status=%s' % (SessionType.download, SessionStatus.waiting)
		html = urlopen(self.client, url)
		sessionList = [Session.from_json(json.dumps(sessionData)) for sessionData in json.loads(html)]
		# print sessionList;
		self.assertEqual(len(sessionList), 0)

		return

	def test_moveFile(self, show_test=True):
		if show_test:
			print(u"\n test_moveFile:")
		storage0 = ServerFileStorage.objects.get(pk=self.serverFile.id)
		self.assertEqual(storage0.storage_used, self.realFile.file_size)

		url = reverse('File_PrivateAPI:moveFile')

		# data={
		# 	'file_location' : self.realFile.file_location,
		# 	'old_server_id' : self.realFile.serverFile.id,
		# 	'new_server_id' : self.serverFile2.id,
		# }

		fileLocationList = [self.realFile.file_location]
		data = urllib.parse.urlencode(
			[('file_location', file_location) for file_location in fileLocationList]
			+ [('old_server_id', self.realFile.serverFile.id), ('new_server_id', self.serverFile2.id), ]
		)
		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		realFile = RealFile.objects.get(pk=self.realFile.id)
		self.assertEqual(realFile.serverFile_id, self.serverFile2.id)

		# #check storage of old server
		# storage1=ServerFileStorage.objects.get(pk=self.serverFile.id);
		# self.assertEqual(storage1.storage_used,storage0.storage_used-self.realFile.file_size);
		# self.assertEqual(storage1.file_count,storage0.file_count-1);
		# #check storage of new server
		# storage2=ServerFileStorage.objects.get(pk=self.serverFile2.id);
		# self.assertEqual(storage2.storage_used,self.realFile.file_size);
		# self.assertEqual(storage2.file_count,1);

		return

	def test_deleteFile(self, show_test=True):
		if show_test:
			print(u"\n test_deleteFile:")
		print('___serverFile.id:',self.serverFile.id)
		storage0 = ServerFileStorage.objects.get(pk=self.serverFile.id)
		self.assertEqual(storage0.storage_used, self.realFile.file_size)

		url = reverse('File_PrivateAPI:deleteFile')
		data = {
			'file_location': self.realFile.file_location,
			'server_id': self.realFile.serverFile.id,
		}
		print('___url:',url)
		html = urlopen(self.client, url, data)

		# check storage of server
		storage1 = ServerFileStorage.objects.get(pk=self.serverFile.id)
		self.assertEqual(storage1.storage_used, storage0.storage_used - self.realFile.file_size)
		self.assertEqual(storage1.file_count, storage0.file_count - 1)

		return

	def test_banFileHash(self, show_test=True):
		if show_test:
			print(u"\n test_banFileHash:")
		file_hash = hashlib.md5(str(datetime.datetime.now()).encode('utf-8')).hexdigest()

		banHash = Banlist(pk=file_hash)
		banHash.save()

		url = reverse('Session_ClientAPI:createUploadSession')
		data = {
			'file_hash': file_hash,
			'file_size': random.randint(10**4, 10**6),
			'file_name': ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20)),
			'erfk': reverseString(''.join(random.choices(string.ascii_uppercase + string.digits, k=32))),
		}

		with self.assertRaisesMessage(Exception, '500'):
			html = urlopen(self.client, url, data)
			result = json.loads(html)
		# except Exception as e:
		# 	self.assertEqual(e[0], 500)  # status_code
		# 	self.assertIn(u"banned", e[1])  # error message

# Create your tests here.
class TestUserGuest(TestCase):

	def setUp(self):
		self.client = Client()

		self.user = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.save()

	def test_login(self, show_test=True):
		if show_test:
			print(u"\n test_login:")
		url = reverse('User_ClientAPI:custom_login')
		data = {
			'username': self.user.username,
			'password': '123456'
		}

		html = urlopen(self.client, url, data)
#		print html;
		return

	def test_signup(self, show_test=True):
		if show_test:
			print(u"\n test_signup:")
		url = reverse('User_ClientAPI:signup')
		data = {
			'username': 'testUserGuest_newuser',
			'password': '123456',
			'email': 'testUserGuest_newuser@email.com',
			'eumk': hashlib.md5(str(datetime.datetime.now()).encode('utf-8')).hexdigest(),
		}

		html = urlopen(self.client, url, data)

		self.assertEqual(self.client.login(username='testUserGuest_newuser', password='123456'), True)

		# Test new account message has been sent.
		self.assertEqual(len(mail.outbox), 1)

		return

	# def test_createTemporaryUser(self, show_test=True):
	# 	if show_test:
	# 		print u"\n test_createTemporaryUser:"
	# 	url = reverse('User_ClientAPI:createTemporaryUser')
	# 	password = '123456'
	# 	data = {
	# 		'password': password,
	# 		'eumk': hashlib.md5(str(datetime.datetime.now())).hexdigest(),
	# 	}
	#
	# 	html = urlopen(self.client, url, data)
	# 	result = json.loads(html)
	# 	username = result.get('username')
	# 	user_id = result.get('user_id')
	# 	self.assertNotEqual(username, None)
	# 	self.assertNotEqual(user_id, None)
	#
	# 	return username, password, user_id
	#
	# def test_signupTemporaryUserAccount(self, show_test=True):
	# 	if show_test:
	# 		print u"\n test_signupTemporaryUserAccount:"
	# 	url = reverse('User_ClientAPI:signupTemporaryUserAccount')
	# 	username, password, user_id = self.test_createTemporaryUser(False)
	# 	new_username = 'signup_temp_user'
	# 	data = {
	# 		'username': username,
	# 		'password': password,
	# 		'new_username': new_username,
	# 		'new_password': 'abc123654',
	# 		'email': 'temp_user@mail.com'
	# 	}
	#
	# 	html = urlopen(self.client, url, data)
	#
	# 	tempUser = User.objects.get(pk=user_id)
	# 	self.assertEqual(tempUser.username, new_username)
	# 	self.assertEqual(tempUser.email, data['email'])
	# 	self.assertEqual(tempUser.profile.account_status, AccountStatus.emailNotActivated)
	#
	# 	url = reverse('User_ClientAPI:custom_login')
	# 	data = {
	# 		'username': new_username,
	# 		'password': 'abc123654'
	# 	}
	#
	# 	html = urlopen(self.client, url, data)
	#
	# 	return


class TestUserLogedIn(TestCase):

	def setUp(self):
		self.client = Client()

		self.user = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.email = self.user.username+'@google.com';
		self.user.save()

		self.user2 = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user2.set_password('123456')
		self.user2.save()

		self.client.login(username=self.user.username, password='123456')

	def test_getUserInfo(self, show_test=True):
		if show_test:
			print(u"\n test_getUserInfo:")
		url = reverse('User_ClientAPI:getUserInfo')

		html = urlopen(self.client, url)
		result = json.loads(html)

		self.assertEqual(result.get('username'), self.user.username)
		self.assertNotEqual(result.get('profiles'), None)
		profile = json.loads(result.get('profiles'))[0]
		# print profile;
		self.assertEqual(profile['fields']['full_name'], self.user.username)

		return profile


	def test_getUserBalance(self, show_test=True):
		if show_test:
			print(u"\n test_getUserBalance:")
		url = reverse('User_ClientAPI:getUserBalance')

		html = urlopen(self.client, url)
		balanceList = json.loads(html)
		for balance in balanceList:
			self.assertEqual(balance['fields']['user'], self.user.id)
		# print balanceList;

		return balance['fields']['amount']

	def test_updateUserInfo(self, show_test=True):
		if show_test:
			print(u"\n test_updateUserInfo and test_logout:")
		url = reverse('User_ClientAPI:updateUserInfo')

		address = 'test address'

		data = {
			'address': address,
			'old_password': '123456',
			'password': '123654',
		}

		html = urlopen(self.client, url, data)

		checkUser = User.objects.get(pk=self.user.id)
		self.assertEqual(checkUser.profile.address, address)

		# check currently login
		self.assertEqual(str(self.client.session.get('_auth_user_id')), str(self.user.pk))

		url = reverse('User_ClientAPI:custom_logout')
		urlopen(self.client, url)
		# check logout
		self.assertNotEqual(str(self.client.session.get('_auth_user_id')), str(self.user.pk))
		# check login
		self.assertEqual(self.client.login(username=self.user.username, password='123654'), True)

		return

	def test_userBanned(self, show_test=True):
		if show_test:
			print(u"\n test_userBanned:")
		self.user.profile.account_status = AccountStatus.banned
		self.user.profile.save()

		with self.assertRaisesMessage(Exception, '302'):
			self.test_getUserBalance(False)
		# except Exception as e:
		# 	self.assertEqual(e[0], 302)  # 302 redirect to login page, because user not pass test decorator

	def test_sendInboxMessage(self, show_test=True):
		if show_test:
			print(u"\n test_sendInboxMessage and test_getListSession:")
		url = reverse('Session_ClientAPI:sendInboxMessage')

		address = 'test address'

		message = 'Hello to you, could take a look at this file please? http://...'
		data = {
			'text': message,
			'to_username': self.user2.username,
		}

		html = urlopen(self.client, url, data)
		data = argparse.Namespace(**json.loads(html))
		session_id = data.session_id

		self.client.login(username=self.user2.username, password='123456')

		url = str(reverse('Session_ClientAPI:getListSession') + '?type=%s' % (SessionType.inbox))
		html = urlopen(self.client, url)
		data = json.loads(html)
		self.assertGreaterEqual(len(data), 1)
		inboxSession = argparse.Namespace(**data[0])
		self.assertEqual(inboxSession._id['$oid'], session_id)
		self.assertEqual(inboxSession.text, message)
		self.assertEqual(inboxSession.sid, self.user2.id)
		self.assertEqual(inboxSession.uid, self.user.id)

		return

	def test_resendActivationEmail(self, show_test=True):
		if show_test:
			print(u"\n test resendActivationEmail:")
		url = reverse('User_ClientAPI:resendActivationEmail')

		html = urlopen(self.client, url, {})

		# Test that one message has been sent.
		self.assertEqual(len(mail.outbox), 1)

		# Verify that the subject of the first message is correct.
		self.assertEqual(mail.outbox[0].subject, 'Activation email from Storagon')
		return

	def test_applyToBecomeAffiliate(self, show_test=True):
		if show_test:
			print(u"\n test applyToBecomeAffiliate:")

		self.user.profile.account_status = AccountStatus.normal
		self.user.profile.save();

		url = reverse('User_ClientAPI:applyToBecomeAffiliate')

		html = urlopen(self.client, url, {});

		# # Test that no message has been sent.
		# self.assertEqual(len(mail.outbox), 0)

		profile=self.test_getUserInfo(False);
		self.assertNotEqual(profile['fields']['account_type'], AccountType.affiliate);

		application = UserApply.objects.get(user=self.user, apply_type=ApplyType.becomeAffiliate, apply_status=ApplyStatus.processing);
		application.apply_status = ApplyStatus.accepted;
		application.save();

		profile=self.test_getUserInfo(False);
		self.assertEqual(profile['fields']['account_type'], AccountType.affiliate);

		# # Test that one message has been sent.
		# self.assertEqual(len(mail.outbox), 1)

		return

	def test_applyToChangeAffiliateMode(self, show_test=True):
		if show_test:
			print(u"\n test applyToChangeAffiliateMode:")

		self.user.profile.account_status = AccountStatus.normal
		self.user.profile.account_type = AccountType.affiliate
		self.user.profile.save();

		url = reverse('User_ClientAPI:applyToChangeAffiliateMode')

		html = urlopen(self.client, url, {'affiliate_mode': 'ppd'});

		profile=self.test_getUserInfo(False);
		self.assertEqual(profile['fields']['account_type'], AccountType.affiliatePPD);

		return

	def test_addWebsiteAgencyDomain(self, show_test=True):
		if show_test:
			print(u"\n test addWebsiteAgencyDomain:")
		self.test_applyToBecomeAffiliate(False);

		url = reverse('User_ClientAPI:addWebsiteAgencyDomain')
		html = urlopen(self.client, url, {'website_address': 'http://test.storagon.com'});

		website = WebsiteAgency.objects.get(website_domain='test.storagon.com');
		self.assertEqual(self.user, website.user);

		return

	def test_getListWebsiteAgency(self, show_test=True):
		if show_test:
			print(u"\n test getListWebsiteAgency:")
		self.test_addWebsiteAgencyDomain(False);

		url = reverse('User_ClientAPI:getListWebsiteAgency')
		html = urlopen(self.client, url);
		data=json.loads(html);

		self.assertEqual(len(data), 1);
		self.assertIn('storagon.com', data[0]['fields']['website_domain'])

		return

	def test_logout(self, show_test=True):
		if show_test: print(u"\n test_logout:")
		url = reverse('User_ClientAPI:custom_logout')
		html = urlopen(self.client, url, {})
		with self.assertRaisesMessage(Exception, '401'):
			self.test_getUserInfo(show_test=False);
		# except Exception as e:
		# 	self.assertEqual(e[0],401);
		# else:
		# 	raise Exception(u"User it still logged in");

	def test_sendResetPasswordEmail(self, show_test=True):
		if show_test: print(u"\n test_sendResetPasswordEmail:")
		self.test_logout(False);
		url = reverse('User_ClientAPI:sendResetPasswordEmail')

		html = urlopen(self.client, url, {'email':self.user.email});

		# Test that one message has been sent.
		self.assertEqual(len(mail.outbox), 1)

		# Verify that the subject of the first message is correct.
		self.assertEqual(mail.outbox[0].subject, "Reset Password Storagon Account")
		m=re.search(r'href="(http://.+)"',mail.outbox[0].body);
		self.assertNotEqual(m,None);
		return m.group(1);

	def test_clickResetPasswordEmail(self, show_test=True):
		if show_test: print(u"\n test_clickResetPasswordEmail:")
		resetLink = self.test_sendResetPasswordEmail(False);
		self.assertEqual(len(mail.outbox),1);

		with self.assertRaisesMessage(Exception, '302'):
			html = urlopen(self.client, resetLink);
		# except Exception as e:
		# 	self.assertEqual(e[0], 302);

		self.assertEqual(len(mail.outbox),2);
		self.assertEqual(mail.outbox[1].subject, "Your Storagon Account Password Has Been Reset")
		print(mail.outbox[1].body);
		m=re.search(r'password: (\w+)',mail.outbox[1].body);
		self.assertNotEqual(m,None);
		new_password = m.group(1);

		self.client.login(username=self.user.username, password=new_password)

		self.test_getUserInfo(False);

class TestUserFile(TestCase):

	def setUp(self):
		self.client = Client()

		self.user = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.save()

		self.client.login(username=self.user.username, password='123456')

		serverFile = ServerFile(name='test', ip_address='127.0.0.1:8080', server_address='http://127.0.0.1:8080', total_storage=1024 * 1024 * 1024 * 1024)
		serverFile.save()
		self.realFile = realFile = RealFile(serverFile=serverFile, file_location='/2015/1/1/abczyx', file_size=100000)
		realFile.save()

		self.userFile = UserFile(realFile=realFile, file_name='xyzcba.mp4', user=self.user)
		self.userFile.save()

		self.folder1 = Folder(user=self.user, name='Folder1')
		self.folder1.save()
		self.folder2 = Folder(user=self.user, name='Folder2')
		self.folder2.save()
		self.folder3 = Folder(user=self.user, name='Folder3', parent_folder=self.folder1)
		self.folder3.save()

		self.userFile2 = UserFile(realFile=realFile, file_name='file1.mp4', user=self.user, folder=self.folder1)
		self.userFile2.save()

		UserFile(realFile=realFile, file_name='file2a.mp4', user=self.user, folder=self.folder2).save()
		UserFile(realFile=realFile, file_name='file2b.mp4', user=self.user, folder=self.folder2).save()
		UserFile(realFile=realFile, file_name='file3i.mp4', user=self.user, folder=self.folder3).save()
		UserFile(realFile=realFile, file_name='file3ii.mp4', user=self.user, folder=self.folder3).save()
		UserFile(realFile=realFile, file_name='file3iii.mp4', user=self.user, folder=self.folder3).save()

	def test_listFileAndFolder(self, show_test=True):
		if show_test:
			print(u"\n test_listFileAndFolder:")
		getData = '?folder_id='
		# getData='?folder_id=%s'%self.folder1.id;
		# getData+='&folder_id=%s'%self.folder2.id;
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)

		html = urlopen(self.client, url)
		data = json.loads(html)
		# print data;

		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])

		self.assertEqual(len(folderList), 2 + 1)  # including recycle bin folder

		getData = '?folder_id=%s' % self.folder1.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		self.assertEqual(len(fileList), 1)
		self.assertEqual(len(folderList), 1)

		getData = '?folder_id=%s' % self.folder1.id
		getData += '&folder_id=%s' % self.folder2.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		self.assertEqual(len(fileList), 3)
		self.assertEqual(len(folderList), 1)

		# print data['fileSizeDict'];
		self.assertEqual(data['fileInfoDict'][str(fileList[0]['pk'])]['file_size'], 100000)
		# print u"len(fileList)=%s , len(folderList)=%s"%(len(fileList),len(folderList));
		return

	def test_moveFile(self, show_test=True):
		if show_test:
			print(u"\n test_moveFile:")

		newFolder4 = Folder(user=self.user, name='Folder4', parent_folder=self.folder2)
		newFolder4.save()

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba4.mp4', user=self.user)
		userFile.save()

		data = urllib.parse.urlencode([
			('file_id', self.userFile.id),
			('file_id', userFile.id),
			('folder_id', newFolder4.id),
		])

		# data={'file_id':userFile.id,
		# 	'folder_id':newFolder4.id,
		# }

		url = reverse('File_ClientAPI:moveFile')

		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		getData = '?folder_id=%s' % newFolder4.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])

		self.assertEqual(len(fileList), 2)
		self.assertEqual(len(folderList), 0)

		return

	def test_deleteFile(self, show_test=True):
		if show_test:
			print(u"\n test_deleteFile:")

		newFolder5 = Folder(user=self.user, name='Folder5', parent_folder=self.folder2)
		newFolder5.save()

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba1.mp4', user=self.user, folder=newFolder5)
		userFile.save()

		userFile2 = UserFile(realFile=self.realFile, file_name='xyzcba2.mp4', user=self.user, folder=newFolder5)
		userFile2.save()

		# check total file = 2

		getData = '?folder_id=%s' % newFolder5.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])

		self.assertEqual(len(fileList), 2)

		# delete file

		data = urllib.parse.urlencode([
			('file_id', userFile.id),
			('file_id', userFile2.id),
		])

		url = reverse('File_ClientAPI:deleteFile')

		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		# check total file = 0

		getData = '?folder_id=%s' % newFolder5.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])

		self.assertEqual(len(fileList), 0)

	def test_newFolder(self, show_test=True):
		if show_test:
			print(u"\n test_newFolder:")

		data = {'folder_name': 'test new folder',
			'folder_id': self.folder3.id,
		}

		url = reverse('File_ClientAPI:newFolder')

		html = urlopen(self.client, url, data)
		data = json.loads(html)
		new_folder_id = data['folder_id']

		# check new folder is in = folder3

		getData = '?folder_id=%s' % self.folder3.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		for folder in folderList:
			if folder['pk'] == new_folder_id:
				break
		else:
			raise "New folder not in folderList=%s" % (str(folderList))

	def test_deleteFolder(self, show_test=True):
		if show_test:
			print(u"\n test_deleteFolder:")

		newFolder6 = Folder(user=self.user, name='Folder6', parent_folder=self.folder1)
		newFolder6.save()
		newFolder7 = Folder(user=self.user, name='Folder7', parent_folder=self.folder1)
		newFolder7.save()

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba.mp4', user=self.user, folder=newFolder6)
		userFile.save()

		data = urllib.parse.urlencode([
			('folder_id', newFolder6.id),
			('folder_id', newFolder7.id),
		])

		url = reverse('File_ClientAPI:deleteFolder')

		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		# check delete file
		try:
			UserFile.objects.get(id=userFile.id)
		except UserFile.DoesNotExist:
			pass
		else:
			raise Exception("File in deleted folder is still exists")

		# check delete folder

		getData = '?folder_id=%s' % self.folder1.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		for folder in folderList:
			if folder['pk'] in [newFolder6.id, newFolder7.id]:
				raise "Deleted folder still in folderList=%s" % (str(folderList))

	def test_moveFolder(self, show_test=True):
		if show_test:
			print(u"\n test_moveFolder:")

		newFolder8 = Folder(user=self.user, name='Folder8', parent_folder=self.folder1)
		newFolder8.save()
		newFolder9 = Folder(user=self.user, name='Folder9', parent_folder=self.folder1)
		newFolder9.save()

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba.mp4', user=self.user, folder=newFolder8)
		userFile.save()

		data = urllib.parse.urlencode([
			('folder_id', newFolder8.id),
			('folder_id', newFolder9.id),
			('to_folder_id', self.folder2.id),
		])

		url = reverse('File_ClientAPI:moveFolder')

		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		# check folder

		getData = '?folder_id=%s' % self.folder1.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		for folder in folderList:
			if folder['pk'] in [newFolder8.id, newFolder9.id]:
				raise "Moved folder still in folderList=%s" % (str(folderList))

		getData = '?folder_id=%s' % self.folder2.id
		url = str(reverse('File_ClientAPI:listFileAndFolder') + getData)
		html = urlopen(self.client, url)
		data = json.loads(html)
		folderList = json.loads(data['folderList'])
		fileList = json.loads(data['fileList'])
		for folder in folderList:
			if folder['pk'] in [newFolder8.id, newFolder9.id]:
				break
		else:
			raise "Moved is not in folderList=%s" % (str(folderList))

	def test_editFolder(self, show_test=True):
		if show_test:
			print(u"\n test_editFolder:")

		folder_name = 'Folder No1'
		data = {
			'folder_id': self.folder1.id,
			'name': folder_name,
		}

		url = reverse('File_ClientAPI:editFolder')

		html = urlopen(self.client, url, data)

		# check folder
		self.folder1 = Folder.objects.get(id=self.folder1.id)
		self.assertEqual(self.folder1.name, folder_name)

	def test_editFile(self, show_test=True):
		if show_test:
			print(u"\n test_editFile:")

		file_name = 'First File.docx'
		data = {
			'file_id': self.userFile.id,
			'file_name': file_name,
		}

		url = reverse('File_ClientAPI:editFile')

		html = urlopen(self.client, url, data)

		# check folder
		self.userFile = UserFile.objects.get(id=self.userFile.id)
		self.assertEqual(self.userFile.file_name, file_name)

	def test_mergeFolder(self, show_test=True):
		if show_test: print(u"\n test_mergeFolder:")
		folderA = Folder(user=self.user, name='Folder A', parent_folder=self.folder1)
		folderA.save();

		folderB=Folder(user=self.user, name='Folder B', parent_folder=folderA);
		folderB.save();
		Folder(user=self.user, name='Folder C', parent_folder=folderA).save()
		Folder(user=self.user, name='Folder D', parent_folder=folderA).save()

		folderA2 = Folder(user=self.user, name='Folder A', parent_folder=self.folder2)
		folderA2.save();
		folderB2=Folder(user=self.user, name='Folder B', parent_folder=folderA2);
		folderB2.save()
		Folder(user=self.user, name='Folder C', parent_folder=folderA2).save()

		userFile = UserFile(realFile=self.realFile, file_name='BBBB.mp4', user=self.user, folder=folderB)
		userFile.save()

		data = urllib.parse.urlencode([
			('folder_id', folderA.id),
			('to_folder_id', self.folder2.id),
		])

		url = reverse('File_ClientAPI:moveFolder')

		html = urlopen(self.client, url, data, content_type='application/x-www-form-urlencoded; charset=UTF-8')

		self.assertEqual(folderA2.subFolderList.count(), 3);
		self.assertEqual(folderB2.fileList.count(), 1);
		self.assertEqual(folderB2.fileList.first().id, userFile.id);

	def test_getLink(self, show_test=True):
		if show_test:
			print(u"\n test_getLink:")

		url = reverse('File_ClientAPI:getLink') + '?file_id=%s&file_id=%s' % (self.userFile.id, self.userFile2.id)

		html = urlopen(self.client, str(url))
		result = json.loads(html)
		# check download link
		self.assertGreaterEqual(len(result['download_url_list']),2);
		# self.assertIn(self.userFile.get_absolute_url(), result['download_url_list'][0])
		# self.assertIn(self.userFile2.get_absolute_url(), result['download_url_list'][1])

	def test_createReport(self, show_test=True):
		if show_test:
			print(u"\n test_createReport and test_getListSession:")
		url = reverse('Session_ClientAPI:createReport')

		address = 'test address'

		data = {
			'text': 'DMCA',
			'fid': self.userFile.id,
			'detail': 'abcdxyz.com',
		}

		html = urlopen(self.client, url, data)
		data = argparse.Namespace(**json.loads(html))
		session_id = data.session_id

		url = str(reverse('Session_ClientAPI:getListSession') + '?type=%s' % (SessionType.report))
		html = urlopen(self.client, url)
		data = json.loads(html)
		self.assertGreaterEqual(len(data), 1)
		reportSession = argparse.Namespace(**data[0])
		self.assertEqual(reportSession._id['$oid'], session_id)
		self.assertEqual(reportSession.sid, self.userFile.user.id)

		return

class TestUserStorage(TestCase):

	def setUp(self):
		self.client = Client()

		self.user = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.save()

		self.client.login(username=self.user.username, password='123456')

		serverFile = ServerFile(name='test', ip_address='127.0.0.1:8080', server_address='http://127.0.0.1:8080', total_storage=1024 * 1024 * 1024 * 1024)
		serverFile.save()
		self.realFile = realFile = RealFile(serverFile=serverFile, file_location='/2015/1/1/abczyx', file_size=100000)
		realFile.save()

	def test_getUserStorage(self, show_test=True):
		if show_test:
			print(u"\n test_getUserStorage:")

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba.mp4', user=self.user)
		userFile.save()

		session = Session(type=SessionType.download, status=SessionStatus.waiting, uid=self.user.id, fid=userFile.id)
		session.data['file_location'] = userFile.realFile.file_location
		session.data['file_size'] = userFile.realFile.file_size
		session.data['file_name'] = userFile.file_name
		session.save()

		data = {
			'session_id': session.id,
			'status': SessionStatus.completed,
			'type': SessionType.download
		}

		url = reverse('Session_PrivateAPI:doneSession')
		html = urlopen(self.client, url, data)
		# session.status=SessionStatus.completed;
		# session.save();

		url = reverse('UserStatistics_ClientAPI:getUserStorage')

		html = urlopen(self.client, url)

		userStorage = UserStorage.from_json(html)

		self.assertEqual(userStorage.storage_used, 100000)
		self.assertEqual(userStorage.download_bandwidth, 100000)

	def test_calculateUserStorage(self, show_test=True):
		if show_test:
			print(u"\n test_calculateUserStorage:")

		userFile = UserFile(realFile=self.realFile, file_name='xyzcba.mp4', user=self.user)
		userFile.save()

		session = Session(type=SessionType.download, status=SessionStatus.completed, uid=self.user.id, fid=userFile.id)
		session.data['file_location'] = userFile.realFile.file_location
		session.data['file_size'] = userFile.realFile.file_size
		session.data['file_name'] = userFile.file_name
		session.save()

		session = Session(type=SessionType.upload, status=SessionStatus.completed, uid=self.user.id, sid=self.realFile.serverFile_id)
		session.data['file_size'] = userFile.realFile.file_size
		session.data['file_name'] = userFile.file_name
		session.save()

		userStorage = UserStorage.objects.get(user_id=self.user.id)
		self.assertEqual(userStorage.storage_used, 100000)

		userStorage.storage_used = -9999
		userStorage.download_bandwidth = 0
		userStorage.upload_bandwidth = 0
		userStorage.save()

		self.assertNotEqual(userStorage.storage_used, 100000)

		userStorage = UserController.calculateUserStorage(self.user.id)

		self.assertNotEqual(userStorage, None)

		self.assertEqual(userStorage.storage_used, 100000)
		self.assertGreater(userStorage.download_bandwidth, 100000)
		self.assertGreater(userStorage.upload_bandwidth, 100000)


class TestPaymentFlow(TestCase):

	def setUp(self):
		self.client = Client()

		self.user = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.user.set_password('123456')
		self.user.save()

		self.client.login(username=self.user.username, password='123456')

		serverFile = ServerFile(name='test', ip_address='127.0.0.1:8080', server_address='http://127.0.0.1:8080', total_storage=1024 * 1024 * 1024 * 1024)
		serverFile.save()
		self.realFile = realFile = RealFile(serverFile=serverFile, file_location='/2015/1/1/abczyx', file_size=1000000)
		realFile.save()

		self.agencyUser = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.agencyUser.set_password('123456')
		self.agencyUser.save()
		self.agencyUser.profile.account_type = AccountType.affiliate
		self.agencyUser.profile.save()

		self.userFile = UserFile(realFile=self.realFile, file_name='xyzcba.mp4', user=self.agencyUser)
		self.userFile.save()

		self.refererUser = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.refererUser.set_password('123456')
		self.refererUser.save()
		self.refererUser.profile.account_type = AccountType.affiliate
		self.refererUser.profile.save()

		self.agencyUser.profile.referer = self.refererUser
		self.agencyUser.profile.save()

		self.websiteAgencyUser = User(username='testUserGuest_user' + str(random.randint(10**4, 10**5)))
		self.websiteAgencyUser.set_password('123456')
		self.websiteAgencyUser.save()
		self.websiteAgencyUser.profile.account_type = AccountType.affiliate
		self.websiteAgencyUser.profile.save()

		# test controller
		website = WebsiteAgency(user=self.agencyUser, website_domain='haivl.com');
		website.save();
		AffiliateController.addWebsiteAgency(self.websiteAgencyUser, 'haivl.com');

		self.websiteAgencyUser.profile.save()

	def test_buyPremiumFlow(self, show_test=True):
		if show_test:
			print(u"\n test_buyPremium:")

		# precheck
		self.assertEqual(self.user.profile.plan_id, 0)

		plan_id = 1
		paygate_id = 1
		url = reverse('buyPremium', args=(plan_id, paygate_id))  # test buy plan 1 using paygate 1

		self.client.cookies['userfile_id'] = str(self.userFile.id)
		self.client.cookies['agency_id'] = str(self.agencyUser.id)
		self.client.cookies['website_origin'] = 'haivl.com'

		html = urlopen(self.client, url)
		data = json.loads(html)
		billSession_id = data['billSession_id']
		print(billSession_id);
		response=PaymentController.paygateCallBackHandler(None, billSession_id)
		if getattr(response, 'status_code', None) == 500:
			raise Exception(response.content);


		# check result payment
		self.user = User.objects.get(id=self.user.id)

		self.assertEqual(self.user.profile.getPlanID(), plan_id)
		self.assertNotEqual(self.user.profile.plan_expired, None)

		balance = self.agencyUser.accountbalance_set.get(balance_type=BalanceType.credit)

		agencyBonusPercent = SystemConfigureController.getConfigure('agencyBonusPercent', 0.65)
		refererBonusPercent = SystemConfigureController.getConfigure('refererBonusPercent', 0.05)
		websiteBonusPercent = SystemConfigureController.getConfigure('websiteBonusPercent', 0.05)

		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent))

		balance = self.refererUser.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent * refererBonusPercent))

		balance = self.websiteAgencyUser.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * websiteBonusPercent))

		# check invoice_bill
		url = reverse('UserStatistics_ClientAPI:listBill')

		html = urlopen(self.client, url)
		data = json.loads(html)

		self.assertGreater(len(data), 0)
		self.assertEqual(data[0]['fields']['money_charged'], settings.DEFAULT_PLAN_CONFIG['price'])
		self.assertEqual(data[0]['fields']['plan_id'], plan_id)
		self.assertEqual(data[0]['fields']['paygate_id'], paygate_id)
		invoice_bill_id = data[0]['pk']

		# check agencyUser transaction
		self.client.login(username=self.agencyUser.username, password='123456')
		getParam = '?transaction_type=%s' % (TransactionType.agency)
		url = reverse('UserStatistics_ClientAPI:listTransaction') + getParam
		html = urlopen(self.client, str(url))
		dataJson = json.loads(html)
		data = json.loads(dataJson['transactionList'])

		self.assertGreater(len(data), 0)
		self.assertEqual(data[0]['fields']['amount'], int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent))
		self.assertEqual(data[0]['fields']['invoice_bill'], invoice_bill_id)
		self.assertEqual(json.loads(data[0]['fields']['data'])['userfile_id'], self.userFile.id)

		# check refererUser transaction
		self.client.login(username=self.refererUser.username, password='123456')
		getParam = '?transaction_type=%s' % (TransactionType.referer)
		url = reverse('UserStatistics_ClientAPI:listTransaction') + getParam
		html = urlopen(self.client, str(url))
		dataJson = json.loads(html)
		data = json.loads(dataJson['transactionList'])

		self.assertGreater(len(data), 0)
		self.assertEqual(data[0]['fields']['amount'], int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent * refererBonusPercent))
		self.assertEqual(data[0]['fields']['invoice_bill'], invoice_bill_id)
		self.assertEqual(json.loads(data[0]['fields']['data'])['agency_username'], self.agencyUser.username)

		# check websiteAgencyUser transaction
		self.client.login(username=self.websiteAgencyUser.username, password='123456')
		getParam = '?transaction_type=%s' % (TransactionType.website)
		url = reverse('UserStatistics_ClientAPI:listTransaction') + getParam
		html = urlopen(self.client, str(url))
		dataJson = json.loads(html)
		data = json.loads(dataJson['transactionList'])

		self.assertGreater(len(data), 0)
		self.assertEqual(data[0]['fields']['amount'], int(settings.DEFAULT_PLAN_CONFIG['price'] * websiteBonusPercent))
		self.assertEqual(data[0]['fields']['invoice_bill'], invoice_bill_id)
		self.assertEqual(json.loads(data[0]['fields']['data'])['website_origin'], 'haivl.com')

	def test_withdrawMoney(self,show_test=True):
		if show_test: print(u"\n test_withdrawMoney:")
		self.test_buyPremiumFlow(False);
		self.client.login(username=self.agencyUser.username, password='123456')
		credit_balance=AccountBalance.objects.get(user=self.agencyUser,balance_type=BalanceType.credit);
		credit_balance.amount+=1000;
		credit_balance.save();
		paypal_balance = AccountBalance(user=self.agencyUser,balance_type=BalanceType.paypal,account_id='test1991');
		paypal_balance.save();
		self.assertEqual(paypal_balance.amount,0)
		UserApply(user=self.agencyUser,apply_type=ApplyType.payAffiliate,apply_status=ApplyStatus.accepted,data=json.dumps({
				"withdraw_balance_id": credit_balance.id,
				"withdraw_amount": 1000,
				"deposit_balance_id": paypal_balance.id,
				"deposit_amount": 1000
			})
		).save();

		paypal_balance = AccountBalance.objects.get(user=self.agencyUser,balance_type=BalanceType.paypal);
		self.assertEqual(paypal_balance.amount,1000)


	def test_pointPerDownload(self, show_test=True):
		if show_test:
			print(u"\n test_pointPerDownload:")
		self.agencyUser.profile.account_type = AccountType.affiliatePPD
		self.agencyUser.profile.save()

		session = Session(type=SessionType.download, status=SessionStatus.waiting, uid=self.user.id, fid=self.userFile.id)
		session.data['file_location'] = self.userFile.realFile.file_location
		session.data['file_size'] = self.userFile.realFile.file_size
		session.data['file_name'] = self.userFile.file_name
		session.data['iso_code'] = 'VN'
		session.data['download_type'] = DownloadType.direct
		session.status=SessionStatus.working
		session.save()

		data = {
			'session_id': str(session.id),
			'status': SessionStatus.completed,
			'type': SessionType.download
		}

		url = reverse('Session_PrivateAPI:doneSession')

		html = urlopen(self.client, url, data)

		balance = self.agencyUser.accountbalance_set.get(balance_type=BalanceType.ppd)
		self.assertGreater(balance.amount, 0)

		referer_balance = self.refererUser.accountbalance_set.get(balance_type=BalanceType.ppd)
		self.assertEqual(referer_balance.amount, int(balance.amount*SystemConfigureController.getConfigure('ppdRefererBonusPercent', 0.05)))

	def test_pointPerDownload2(self, show_test=True):
		if show_test:
			print(u"\n test_pointPerDownload2:")
		self.agencyUser.profile.account_type = AccountType.affiliate
		self.agencyUser.profile.save()

		userFile = UserFile(realFile=self.realFile, file_name='123654.mp4', user=self.agencyUser)
		userFile.save()

		session = Session(type=SessionType.download, status=SessionStatus.waiting, uid=self.user.id, fid=userFile.id)
		session.data['file_location'] = userFile.realFile.file_location
		session.data['file_size'] = userFile.realFile.file_size
		session.data['file_name'] = userFile.file_name
		session.data['iso_code'] = 'VN'
		session.data['download_type'] = DownloadType.direct
		session.status=SessionStatus.working
		session.save()

		data = {
			'session_id': str(session.id),
			'status': SessionStatus.completed,
			'type': SessionType.download
		}

		url = reverse('Session_PrivateAPI:doneSession')

		html = urlopen(self.client, url, data)

		balance = self.agencyUser.accountbalance_set.get(balance_type=BalanceType.point)
		self.assertGreater(balance.amount, 0)

	def test_exchangePoint(self, show_test=True):
		if show_test:
			print(u"\n test_exchangePoint:")
		balance = self.user.accountbalance_set.get(balance_type=BalanceType.point)
		balance.amount = 10000
		balance.save()

		url = reverse('UserStatistics_ClientAPI:exchangePoint')
		data = {
			'pack': 'plan1'
		}

		html = urlopen(self.client, url, data)

		balance = self.user.accountbalance_set.get(balance_type=BalanceType.point)

		self.assertGreater(10000, balance.amount)

	def test_buyPremiumKey(self, show_test=True):
		if show_test: print(u"\n test_buyPremiumKey:")
		self.user.profile.account_type = AccountType.reseller;
		self.user.profile.save();

		balance = self.user.accountbalance_set.get(balance_type=BalanceType.credit)
		balance.amount = 10000
		balance.save()

		url = reverse('Premium_ClientAPI:buyPremiumKeyUsingCredit')
		data = {
			'plan_id': 1,
			'max_num_key': 10,
		}

		html = urlopen(self.client, url, data)

		balance = self.user.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertGreater(10000, balance.amount);

		url = reverse('Premium_ClientAPI:getListPremiumKey')
		html = urlopen(self.client, url);
		data = Munch.fromDict(json.loads(html));

		self.assertEqual(len(data), 10);

		resultCode=[];
		for premiumKey in data:
			self.assertEqual(premiumKey.fields.reseller, self.user.id);
			resultCode+=[premiumKey.fields.code];

		return resultCode;

	def test_exchangePremiumKey(self, show_test=True):
		resultCode = self.test_buyPremiumKey(False);

		self.client.cookies['agency_id'] = str(self.agencyUser.id)
		self.client.cookies['website_origin'] = 'haivl.com'

		url = reverse('Premium_ClientAPI:exchangePremiumKey')
		data = {
			'premium_code': resultCode[0],
		}

		html = urlopen(self.client, url, data);

		# check result payment
		self.user = User.objects.get(id=self.user.id)

		self.assertEqual(self.user.profile.plan_id, 1)
		self.assertNotEqual(self.user.profile.plan_expired, None)

		agencyBonusPercent = SystemConfigureController.getConfigure('agencyBonusPercent', 0.65)
		refererBonusPercent = SystemConfigureController.getConfigure('refererBonusPercent', 0.05)
		websiteBonusPercent = SystemConfigureController.getConfigure('websiteBonusPercent', 0.05)

		balance = self.agencyUser.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent))

		balance = self.refererUser.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * agencyBonusPercent * refererBonusPercent))

		balance = self.websiteAgencyUser.accountbalance_set.get(balance_type=BalanceType.credit)
		self.assertEqual(balance.amount, int(settings.DEFAULT_PLAN_CONFIG['price'] * websiteBonusPercent))
