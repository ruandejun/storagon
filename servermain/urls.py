from django.conf import settings;
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from .api import Session_ClientAPI_urls, User_ClientAPI_urls, File_ClientAPI_urls, UserStatistics_ClientAPI_urls, Premium_ClientAPI_urls, File_PrivateAPI_urls, Session_PrivateAPI_urls
# from .api import User_RestfulAPI_urls, File_RestfulAPI_urls
import system_configure.urls
from . import restful_urls, storagon_urls, junshare_urls
from .payment_views import *

urlpatterns = [
	url(r'^clapi/session/', include(Session_ClientAPI_urls, namespace='Session_ClientAPI')),
	url(r'^clapi/user/', include(User_ClientAPI_urls, namespace='User_ClientAPI')),
	url(r'^clapi/file/', include(File_ClientAPI_urls, namespace='File_ClientAPI')),
	url(r'^clapi/userstats/', include(UserStatistics_ClientAPI_urls, namespace='UserStatistics_ClientAPI')),
	url(r'^clapi/premium/', include(Premium_ClientAPI_urls, namespace='Premium_ClientAPI')),

	url(r'^prapi/file/', include(File_PrivateAPI_urls, namespace='File_PrivateAPI')),
	url(r'^prapi/session/', include(Session_PrivateAPI_urls, namespace='Session_PrivateAPI')),

	# url(r'^restful/user/', include(User_RestfulAPI_urls, namespace='User_RestfulAPI')),
	# url(r'^restful/file/', include(File_RestfulAPI_urls, namespace='File_RestfulAPI')),
	url(r'^api/', include(restful_urls, namespace='API') ),

	url(r'^buypremium/(\d+)/(\d+)/', buyPremium, name='buyPremium'),
	url(r'^paygatecallback/(\w+)/', paygateCallBack, name='paygateCallBack'),

	url(r'^sys/', include(system_configure.urls)),


]

if settings.DOMAIN == 'storagon.com':
	urlpatterns += [url(r'', include(storagon_urls)),]
elif settings.DOMAIN == 'junshare.com':
	urlpatterns += [url(r'', include(junshare_urls)),]