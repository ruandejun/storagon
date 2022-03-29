#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  browser.py
#  Xcode-IPython
#
#  Created by V.Anh Tran on 11/22/12.
#  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
#

import sys
import urllib.request as urllib2
try:
	import cookielib
except:
	import http.cookiejar
	cookielib = http.cookiejar
from urllib.parse import urlencode
from . import header
from urllib.parse import urljoin
import re, random
import requests
import time
from bs4 import BeautifulSoup
from urllib3.util import connection
import os, dns

class Rqbrowser:
	""" Test reg forum
	"""

	def __init__(self,agent='',agent_mobile=False, cookieJar=None, quite=False):
		self.quite = quite
		##Agent
		THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
		my_file = os.path.join(THIS_FOLDER, 'headerpc.txt')
		print(my_file)
		list_agent_open = open(my_file)
		list_agent_win = list_agent_open.read().split('\n')
		list_agent_open.close()
		list_agent_mobile = [
			'Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+',
			'Mozilla/5.0 (BlackBerry; U; BlackBerry 9860; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.0.0.254 Mobile Safari/534.11+',
			'Mozilla/5.0 (iPad; U; CPU OS 4_3_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5',
			'Mozilla/5.0 (iPad; U; CPU OS 4_3 like Mac OS X; en-US) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8F191 Safari/6533.18.5',
			'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A405 Safari/7534.48.3',
			'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
			'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A405 Safari/7534.48.3',
			'Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
			'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25',
		]
		self.agent = agent
		extra_info = str(random.randint(99999, 9999999))
		while not self.agent:
			if not agent_mobile:
				self.agent = list_agent_win[random.randint(0, len(list_agent_win) - 1)].strip()+'/'+extra_info
			else:
				self.agent = list_agent_mobile[random.randint(0, len(list_agent_mobile) - 1)].strip()+'/'+extra_info


		##cookies
		self.all_cookies = {}
		if not cookieJar:
			self.cookies_jar = cookielib.MozillaCookieJar()
		else:
			self.cookies_jar = self.cookieJar
		self.browser = requests.session()

		self.browser.cookies = self.cookies_jar

		self.sock5 = False
		self.proxy = False
		self.proxies = ''
		self.link_host = ''
		self.link_origin = ''

		self.header = {'User-Agent': self.agent,
				   'Connection': 'keep-alive',
				   'Accept-Language': 'en-US',
				   'Cache-Control': 'no-cache',
				   'Access-Control-Allow-Origin': '*',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.5,/;q=0.5'};

	# self.cookie = cookielib.MozillaCookieJar()
	def load_cookies(self,cookies_file):

		self.cookies_jar.load(cookies_file)
		# Load existing cookies (file might not yet exist)
		self.browser.cookies = self.cookies_jar

	def save_cookies(self,cookies_file):
		self.cookies_jar.save(cookies_file)
	def get_cookies(self):
		return self.browser.cookies.get_dict()
	def add_header(self, link_refer='', XMLHttpRequest=None, extraHeader={}):
		self.header = {
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive',
		'Accept-Language': 'en-US',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.5,/;q=0.5'
		}
		if self.agent:
			self.header.update({'User-Agent': self.agent})
		if link_refer:
			self.header.update({'Referer':link_refer})
		# if self.link_host:
		#     self.header.update({'Host':self.link_host})
		# if self.link_origin:
		self.header.update({'Access-Control-Allow-Origin': '*'})
		if extraHeader:
			self.header.update(extraHeader)
		if XMLHttpRequest:
			self.header.update({'X-Requested-With': 'XMLHttpRequest'})

	def set_proxies(self, sock5='', proxy=''):
		if sock5:
			self.sock5 = sock5
		elif proxy:
			self.proxy = proxy

		_orig_create_connection = connection.create_connection

		# my_resolver.nameservers = ['8.8.8.8']
		def myResolver(host):
			r = dns.resolver.Resolver()
			r.nameservers = ['8.8.8.8']
			answers = r.query(host, 'A')
			for rdata in answers:
				return str(rdata)

		# myResolver('24.14.49.175','24.14.49.175')
		def patched_create_connection(address, *args, **kwargs):
			"""Wrap urllib3's create_connection to resolve the name elsewhere"""
			# resolve hostname to an ip address; use your own
			# resolver here, as otherwise the system resolver will be used.
			host, port = address
			hostname = myResolver(host)

			return _orig_create_connection((hostname, port), *args, **kwargs)

		connection.create_connection = patched_create_connection

	def open(self, url, data='',put_data='', json_data='',params='', agent='', timeout=30, allow_redirects=True,add_cookies={}, method='',extraHeader={}):

		if self.sock5:
			self.proxies = {'http': 'socks5://' + self.sock5, 'https': 'socks5://' + self.sock5}
		elif self.proxy:
			self.proxies = {'http': self.proxy, 'https': self.proxy}

		if extraHeader:
			self.header.update(extraHeader)
		if self.header:
			self.browser.headers = self.header
		if self.proxies:
			self.browser.proxies.update(self.proxies)

		#
		if add_cookies:
			self.all_cookies.update(add_cookies)
		if data:
			self.result = self.browser.post(url, data=data, timeout=timeout,proxies=self.proxies,allow_redirects=allow_redirects)
		elif json_data:
			# json_data = json.loads(json_data)
			self.result = self.browser.post(url, json=json_data, timeout=timeout,proxies=self.proxies,allow_redirects=allow_redirects)
		elif put_data:

			self.result = self.browser.put(url, json=put_data, timeout=timeout,proxies=self.proxies,allow_redirects=allow_redirects)
		else:

			self.result = self.browser.get(url,proxies=self.proxies,allow_redirects=allow_redirects, timeout=timeout)

		self.all_cookies.update(requests.utils.dict_from_cookiejar(self.browser.cookies))
		return self.result.text
	def download(self, link, pathToSave):
		if not self.quite:
			print("___download: ", str(link))
		fileNamePattern = r'[\w\-.\[\]\(\)]+\.?\w+$'
		if not re.search(fileNamePattern, pathToSave):
			m = re.search(fileNamePattern, link)
			if m: filePath = pathToSave + '/' + m.group(0)
			else:
				filePath = pathToSave+'/'+link.split('/')[-1];
		else:
			filePath = pathToSave
		r = requests.get(link, stream=True)
		r.raise_for_status()
		# try:
		# 	response = self.browser.open(link);
		# except urllib2.HTTPError as e:
		# 	print(e.getcode(), e.read())
		# 	raise e
		CHUNK = 8 * 1024
		with open(filePath, 'wb') as f:
			for chunk in r.iter_content(chunk_size=CHUNK):
				# If you have chunk encoded response uncomment if
				# and set chunk_size parameter to None.
				# if chunk:
				f.write(chunk)
		r.close()
		f.close()

	def setAddHeader(self, headerKey, headerValue):
		self.header.update({headerKey:headerValue})

	def close(self):
		del self.browser
	def read(self):
		return
	def get_url(self):
		return
	def fixHTML(self, html):
		return html.replace("'", '"');

	def selectForm(self, html,nr=0):
		forms_post = None
		# print(html)
		soup = BeautifulSoup(html,features="html5lib")
		forms = soup.find_all('form')
		listForms = []
		for form in forms:
			# print(form)
			print(form['action'])
			fields = form.findAll('input')
			formdata = dict( (field.get('name'), field.get('value')) for field in fields)
			# print(formdata)
			listForms.append(formdata)
		return listForms
		# print(formdata)
		# print(fields)



class Browser:

	""" My browser, try to fake as similiar as possible with chrome on Mac OSX
	"""

	def __init__(self, cookieJar=None):
#		print "Browser Init!"
		header.initBrowser(self, cookieJar)
		self.br = self.browser
		# browser setup
		self.quite = False
		self.showResponseMax = 1200  # max char
		self.lastResponse = None
		self.delayTimeBeforeRequest = 0

	def open(self, url, data=None, getResponse=False, folowRedirect=5, extraHeader=None, forceReferer=None):
		""" Make a GET/POST request to url
		:param url:
		:param data: dict contain data form fields
		:param getResponse: return response object instead of html
		:param folowRedirect: folow all kind of redirect
		:param extraHeader:  dict contain extra header to be added to request
		:param forceReferer: force set referer header
		:return: html of response
		"""
		if data is not None:
			if isinstance(data, str) == False:
				data = urlencode(data)
			if not self.quite:
				print("___payload: " + data)

		if isinstance(url, str) or isinstance(url, bytes):
			if extraHeader:
				req = urllib2.Request(url, data, extraHeader)
			else:
				req = urllib2.Request(url, data)
		else:
			req = url

		url = req.get_full_url()
		if not self.quite:
			print("___request: " + str(url))

		if self.delayTimeBeforeRequest > 0:
			if not self.quite:
				print("requesting...")
			time.sleep(self.delayTimeBeforeRequest)

		if forceReferer:
			self.setAddHeader('Referer', forceReferer)

		try:
			response = self.br.open(req)
		except urllib2.HTTPError as e:
			print(e.getcode(), e.read())
			raise e

		self.setAddHeader('Host', url.split('/')[2])
		self.setAddHeader('Referer', url)

		if getResponse:
			return response
		else:
			self.lastResponse = response

		html = response.read()
		response.close()
		if not self.quite:
			print("___response: ", html[:self.showResponseMax])

		if folowRedirect > 0:
			redirectLink = response.headers.get_content_charset('location')
			print('___redirectLink:', redirectLink)
			m = re.search(r'<META HTTP-EQUIV="Refresh" CONTENT="0;URL=(\S+?)">', html.decode('utf-8'), re.I)
			if(m and m.group(1).strip()):
				redirectLink = urljoin(url, m.group(1).strip())
			if redirectLink:
				if not self.quite:
					print("redirect left=%d" % (folowRedirect))
					print("redirect link=",redirectLink)
				return self.open(redirectLink.decode('utf-8'), folowRedirect=folowRedirect - 1)

		return html

	def download(self, link, pathToSave):
		if not self.quite:
			print("___download: ", str(link))

		try:
			response = self.br.open(link);
		except urllib2.HTTPError as e:
			print(e.getcode(), e.read())
			raise e

		fileNamePattern = r'[\w\-.\[\]\(\)]+\.?\w+$'
		if not re.search(fileNamePattern, pathToSave):
			m = re.search(fileNamePattern, link)
			if m: filePath = pathToSave + '/' + m.group(0)
			else:
				filePath = pathToSave+'/'+link.split('/')[-1];
		else:
			filePath = pathToSave

		CHUNK = 8 * 1024
		with open(filePath, 'wb') as f:
			while True:
				chunk = response.read(CHUNK)
				if not chunk:
					break
				f.write(chunk)

	def setAddHeader(self, headerKey, headerValue):
		for header in self.br.addheaders[:]:
			key, val = header
			if key == headerKey:
				self.br.addheaders.remove(header)
		self.br.addheaders += [(headerKey, headerValue)]


class BrowserTest:

	def __init__(self):
		self.browser = Browser()

	def testDownload(self):
		self.browser.download('http://msft.digitalrivercontent.net/win/X17-59186.iso', '/Users/TVA/Downloads/')

	def getCapchaIMG(self):
		res = self.browser.open('http://chonso.vinaphone.com.vn/numstore/jcaptcha', getResponse=True)
		f = open('captcha.img', 'wb+')
		f.write(res.read())
		f.close()
		res.close()

	def openHomePage(self):
		print(self.browser.open('http://chonso.vinaphone.com.vn/numstore/index.htm'))
		print('*' * 20)
		self.getCapchaIMG()
		capcha = raw_input('Capcha:')

		data = {
			'j_captcha_response': capcha,
		}

		print(self.browser.open('http://chonso.vinaphone.com.vn/numstore/jcaptchaValid', data))
		print('*' * 20)

		print(self.browser.open('http://chonso.vinaphone.com.vn/numstore/check.jsp'))
		print('*' * 20)

		data = {
			'j_username': 'neo',
			'j_password': 'neo',
		}

		print(self.browser.open('http://chonso.vinaphone.com.vn/numstore/j_security_check', data))
		print('*' * 20)

		pass


def main():
	br = BrowserTest()
	br.testDownload()
	pass

if __name__ == "__main__":
	sys.exit(main())
