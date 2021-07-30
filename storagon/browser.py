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
import urllib
import urllib.request as urllib2
try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar
import re
import time
#import header


class Browser:

	""" My browser, try to fake as similiar as possible with chrome on Mac OSX
	"""

	def __init__(self, cookieJar=None):
#		print "Browser Init!"
		#header.initBrowser(self, cookieJar)
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
				data = urllib.urlencode(data)
			if not self.quite:
				print("___payload: " + data)

		if isinstance(url, str) or isinstance(url, unicode):
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
			print("___response: " + html[:self.showResponseMax])

		if folowRedirect > 0:
			redirectLink = response.headers.getheader('location')

			m = re.search(r'<META HTTP-EQUIV="Refresh" CONTENT="0;URL=(\S+?)">', html, re.I)
			if(m and m.group(1).strip()):
				redirectLink = urllib.basejoin(url, m.group(1).strip())
			if redirectLink:
				if not self.quite:
					print("redirect left=%d" % (folowRedirect))
				return self.open(redirectLink, folowRedirect=folowRedirect - 1)

		return html

	def download(self, link, pathToSave):
		if not self.quite:
			print("___download: " + str(link))

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
