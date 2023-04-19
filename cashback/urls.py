
from django.conf.urls import include, url


urlpatterns = [
	url(r'^capi/', include(('cashback.api.Commission_Api_urls', 'Commission_Api'), namespace='Commission_Api')),
]
