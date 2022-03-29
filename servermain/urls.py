from django.conf import settings;
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView

# from .api import Session_ClientAPI_urls, User_ClientAPI_urls, File_ClientAPI_urls, UserStatistics_ClientAPI_urls, Premium_ClientAPI_urls, File_PrivateAPI_urls, Session_PrivateAPI_urls
# # from .api import User_RestfulAPI_urls, File_RestfulAPI_urls
# import system_configure.urls
from . import restful_urls
from .payment_views import *

from .download_views import DownloadView, DownloadView2, activateAccount

urlpatterns = [
	url(r'^clapi/session/', include(('servermain.api.Session_ClientAPI_urls', 'Session_ClientAPI'), namespace='Session_ClientAPI')),
	url(r'^clapi/user/', include(('servermain.api.User_ClientAPI_urls', 'User_ClientAPI'), namespace='User_ClientAPI')),
	url(r'^clapi/file/', include(('servermain.api.File_ClientAPI_urls', 'File_ClientAPI'), namespace='File_ClientAPI')),
	url(r'^clapi/userstats/', include(('servermain.api.UserStatistics_ClientAPI_urls', 'UserStatistics_ClientAPI'), namespace='UserStatistics_ClientAPI')),
	url(r'^clapi/premium/', include(('servermain.api.Premium_ClientAPI_urls', 'Premium_ClientAPI'), namespace='Premium_ClientAPI')),
	url(r'^prapi/file/', include(('servermain.api.File_PrivateAPI_urls', 'File_PrivateAPI'), namespace='File_PrivateAPI')),
	url(r'^prapi/session/', include(('servermain.api.Session_PrivateAPI_urls', 'Session_PrivateAPI'), namespace='Session_PrivateAPI')),

	# url(r'^restful/user/', include(User_RestfulAPI_urls, namespace='User_RestfulAPI')),
	# url(r'^restful/file/', include(File_RestfulAPI_urls, namespace='File_RestfulAPI')),
	url(r'^api/', include((restful_urls, 'MainAPI'), namespace='API') ),

	url(r'^buypremium/(\d+)/(\d+)/', buyPremium, name='buyPremium'),
	url(r'^paygatecallback/(\w+)/', paygateCallBack, name='paygateCallBack'),

	url(r'^sys/', include('system_configure.urls')),

	url(r'^dl/(\d+)/(.+)$', DownloadView.as_view(), name='download'),
	url(r'^dl/(\d+)s(.+)$', DownloadView2.as_view(), name='download2'),
	url(r'^activateAccount/$', activateAccount, name='activateAccount'),
]
