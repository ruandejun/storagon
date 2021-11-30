
from django.conf.urls import include, url


urlpatterns = [
	url(r'^bapi/', include(('telegram_bot.api.Bot_ClientAPI_urls', 'Bot_ClientAPI'), namespace='Bot_ClientAPI')),
]
