from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from django.shortcuts import render
from dashboard.ghi_views import ghi_redirect, ghi_editor
#from django.contrib.auth.views import login, logout, logout_then_login
# from jet_django.urls import jet_urls

urlpatterns = [
	url(r'^$', ghi_redirect, name='ghi_redirect_root'),
	url(r'^adl/custom/', include('servermain.CustomAdmin_urls')),
	url(r'^adl/doc/', include('django.contrib.admindocs.urls')),
	url(r'^adl/', admin.site.urls),
	url(r'^sf/', include('serverfile.urls')),
	url(r'^tracker/', include('private_tracker.urls')),
	url(r'^api/', include('cards_manager.urls')),
	url(r'^dashboard/', include('dashboard.urls')),
	url(r'^ghi/', include('dashboard.ghi_urls')),
	url(r'', include('servermain.urls')),  # pass all other url request to servermain
	url(r'^telegram/', include('telegram_bot.urls')),  # pass all other url request to servermain
	url(r'^cashback/', include('cashback.urls')),  # pass all other url request to servermain
	url(r'^(?P<note_id>[a-zA-Z0-9]+)/$', ghi_editor, name='ghi_editor_root'),
]


handler400 = 'storagon.tool.custom_400';
