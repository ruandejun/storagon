from django.conf import settings;
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
# from . import api
from .api import Session_ClientAPI_urls, User_ClientAPI_urls, File_ClientAPI_urls, UserStatistics_ClientAPI_urls, Premium_ClientAPI_urls, File_PrivateAPI_urls, Session_PrivateAPI_urls
# from .api import User_RestfulAPI_urls, File_RestfulAPI_urls
import system_configure.urls
from . import restful_urls, storagon_urls, junshare_urls
from .payment_views import *

urlpatterns = [
	url(r'^clapi/session/', Session_ClientAPI_urls),
	url(r'^clapi/user/', User_ClientAPI_urls),
	url(r'^clapi/file/', File_ClientAPI_urls),
	url(r'^clapi/userstats/', UserStatistics_ClientAPI_urls),
	url(r'^clapi/premium/', Premium_ClientAPI_urls),
	url(r'^prapi/file/', File_PrivateAPI_urls),
	url(r'^prapi/session/', Session_PrivateAPI_urls),

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