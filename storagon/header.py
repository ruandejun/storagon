# lisr of user agent header
user_agents = [
"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.9) Gecko/2009040821 Firefox/3.0.8 (de) (TL-FF) (.NET CLR 3.5.30729)",
"Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.9) Gecko/2009040821 Firefox/3.0.9",
"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.9) Gecko/2009040821 Firefox/3.0.4 (de) (TL-FF)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; GTB5; FunWebProducts; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506; InfoPath.2)",
"Mozilla/5.0 (Windows; U; Windows NT 6.0; de; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.1 (.NET CLR 3.5.30729)",
"Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.83 Safari/535.11",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.82",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
]

standard = [('User-Agent', user_agents[-1]),
('Cache-Control', 'max-age=0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8'),
]

import urllib2
import cookielib


def initBrowser(self, cookieJar=None):
#	print "Browser Init!"
	# browser setup
	if cookieJar is not None:
		self.cookieJar = cookieJar
	else:
		self.cookieJar = cookielib.CookieJar()
	self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
	self.browser.addheaders = standard

