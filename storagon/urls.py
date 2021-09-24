from django.conf.urls import include, url
from django.contrib import admin
#from django.contrib.auth.views import login, logout, logout_then_login
# from jet_django.urls import jet_urls

urlpatterns = [
	url(r'^adl/custom/', include('servermain.CustomAdmin_urls')),
	url(r'^adl/doc/', include('django.contrib.admindocs.urls')),
	url(r'^adl/', admin.site.urls),
	url(r'^sf/', include('serverfile.urls')),
	url(r'^tracker/', include('private_tracker.urls')),
	url(r'api/', include('servermain.urls')),  # pass all other url request to servermain
]


handler400 = 'storagon.tool.custom_400';
