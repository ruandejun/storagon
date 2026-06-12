from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard_index, login_view, logout_view,
    dashboard_stats_api, DashboardUserViewSet, CardViewSet,
    BrowserProfilesViewSet, MunProxiesViewSet,
    AccountsEmailsViewSet, AccountsCreatedViewSet
)

router = DefaultRouter()
router.register(r'users', DashboardUserViewSet, basename='dashboard-user')
router.register(r'cards', CardViewSet, basename='dashboard-card')
router.register(r'profiles', BrowserProfilesViewSet, basename='dashboard-profile')
router.register(r'proxies', MunProxiesViewSet, basename='dashboard-proxy')
router.register(r'emails', AccountsEmailsViewSet, basename='dashboard-email')
router.register(r'accounts', AccountsCreatedViewSet, basename='dashboard-account')

urlpatterns = [
    url(r'^$', dashboard_index, name='dashboard_index'),
    url(r'^login/$', login_view, name='dashboard_login'),
    url(r'^logout/$', logout_view, name='dashboard_logout'),
    url(r'^api/stats/$', dashboard_stats_api, name='dashboard_stats_api'),
    url(r'^api/', include(router.urls)),
]
