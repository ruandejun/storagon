from django.conf.urls import patterns, url

urlpatterns = patterns('serverfile',
	url(r'^upload/(\w+)/(.*?)/$', 'my_upload_views.my_resumable', name='resumable_upload'),
	url(r'^download/(\w+)/(.*?)/(.*)$', 'server_file_views.downloadView', name='downloadView'),
	url(r'^torrent/(\w+)/(.*?)/(.*)$', 'server_file_views.downloadTorrentView', name='downloadTorrentView'),

	url(r'^initiateDeleteSessionProcess/$', 'server_file_views.initiateDeleteSessionProcess', name='initiateDeleteSessionProcess'),
	url(r'^initiateMoveSessionProcess/$', 'server_file_views.initiateMoveSessionProcess', name='initiateMoveSessionProcess'),
	url(r'^initiateClearTemporaryFolderProcess/$', 'server_file_views.initiateClearTemporaryFolderProcess', name='initiateClearTemporaryFolderProcess'),
)
