from django.conf.urls import url
from admin_resumable.views import *
urlpatterns = ['',
    url(r'^admin_resumable/$', admin_resumable, name='admin_resumable'),
]
