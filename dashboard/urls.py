from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard_index, login_view, logout_view,
    register_view, forgot_password_view,
    dashboard_stats_api, dashboard_ip_info_api, DashboardUserViewSet, CardViewSet,
    BrowserProfilesViewSet, MunProxiesViewSet,
    AccountsEmailsViewSet, AccountsCreatedViewSet,
    UserHwidViewSet, NotificationViewSet, current_user_api,
    apple_sub_login, apple_sub_verify_2fa, apple_sub_purchase,
    apple_sub_accounts, tiktok_user_lookup, tiktok_sub_tiers,
    apple_sub_account_info, apple_sub_add_payment
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
    url(r'^api/ip-info/$', dashboard_ip_info_api, name='dashboard_ip_info_api'),

    # Apple Subscription API endpoints
    url(r'^api/apple-sub/login/$', apple_sub_login, name='apple_sub_login'),
    url(r'^api/apple-sub/verify-2fa/$', apple_sub_verify_2fa, name='apple_sub_verify_2fa'),
    url(r'^api/apple-sub/purchase/$', apple_sub_purchase, name='apple_sub_purchase'),
    url(r'^api/apple-sub/accounts/$', apple_sub_accounts, name='apple_sub_accounts'),
    url(r'^api/apple-sub/account-info/$', apple_sub_account_info, name='apple_sub_account_info'),
    url(r'^api/apple-sub/add-payment/$', apple_sub_add_payment, name='apple_sub_add_payment'),
    url(r'^api/apple-sub/tiktok-lookup/$', tiktok_user_lookup, name='tiktok_user_lookup'),
    url(r'^api/apple-sub/tiktok-tiers/$', tiktok_sub_tiers, name='tiktok_sub_tiers'),

    url(r'^api/', include(router.urls)),
]

