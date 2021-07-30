from django.conf.urls import url
from .server_file_views import *
from .my_upload_views import *
urlpatterns = [
	url(r'^upload/(\w+)/(.*?)/$', my_resumable, name='resumable_upload'),
	url(r'^download/(\w+)/(.*?)/(.*)$', downloadView, name='downloadView'),
	url(r'^torrent/(\w+)/(.*?)/(.*)$', downloadTorrentView, name='downloadTorrentView'),
	url(r'^initiateDeleteSessionProcess/$', initiateDeleteSessionProcess, name='initiateDeleteSessionProcess'),
	url(r'^initiateMoveSessionProcess/$', initiateMoveSessionProcess, name='initiateMoveSessionProcess'),
	url(r'^initiateClearTemporaryFolderProcess/$', initiateClearTemporaryFolderProcess, name='initiateClearTemporaryFolderProcess'),
]
