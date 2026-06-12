from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet

router = DefaultRouter()
router.register(r'cards', CardViewSet, basename='card')

urlpatterns = [
    url(r'^', include(router.urls)),
]
