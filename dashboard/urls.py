from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard_index, login_view, logout_view,
    register_view, forgot_password_view,
    dashboard_stats_api, DashboardUserViewSet, CardViewSet,
    BrowserProfilesViewSet, MunProxiesViewSet,
    AccountsEmailsViewSet, AccountsCreatedViewSet,
    UserHwidViewSet, NotificationViewSet, current_user_api
)

router = DefaultRouter()
router.register(r'users', DashboardUserViewSet, basename='dashboard-user')
router.register(r'cards', CardViewSet, basename='dashboard-card')
router.register(r'profiles', BrowserProfilesViewSet, basename='dashboard-profile')
router.register(r'proxies', MunProxiesViewSet, basename='dashboard-proxy')
router.register(r'emails', AccountsEmailsViewSet, basename='dashboard-email')
router.register(r'accounts', AccountsCreatedViewSet, basename='dashboard-account')
router.register(r'hwids', UserHwidViewSet, basename='dashboard-hwid')
router.register(r'notifications', NotificationViewSet, basename='dashboard-notification')

urlpatterns = [
    url(r'^$', dashboard_index, name='dashboard_index'),
    url(r'^login/$', login_view, name='dashboard_login'),
    url(r'^logout/$', logout_view, name='dashboard_logout'),
    url(r'^register/$', register_view, name='dashboard_register'),
    url(r'^forgot-password/$', forgot_password_view, name='dashboard_forgot_password'),
    url(r'^api/me/$', current_user_api, name='current_user_api'),
    url(r'^api/stats/$', dashboard_stats_api, name='dashboard_stats_api'),
    url(r'^api/', include(router.urls)),
]
