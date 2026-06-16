from django.conf.urls import url
from .ghi_views import (
    ghi_redirect, ghi_editor,
    ghi_get_api, ghi_save_api, ghi_verify_password
)

urlpatterns = [
    url(r'^$', ghi_redirect, name='ghi_redirect'),
    url(r'^(?P<note_id>[a-zA-Z0-9]+)/$', ghi_editor, name='ghi_editor'),
    url(r'^api/get/(?P<note_id>[a-zA-Z0-9]+)/$', ghi_get_api, name='ghi_get_api'),
    url(r'^api/save/(?P<note_id>[a-zA-Z0-9]+)/$', ghi_save_api, name='ghi_save_api'),
    url(r'^api/verify-password/(?P<note_id>[a-zA-Z0-9]+)/$', ghi_verify_password, name='ghi_verify_password'),
]
