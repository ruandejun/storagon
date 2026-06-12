#!/usr/bin/python
# -*- coding: utf-8 -*-

from .Card_RestfulAPI import CardViewSet
from system_configure.controllers.Tool import FullRouter

router = FullRouter('cards')
router.register(r'', CardViewSet, basename='Card')

urlpatterns = router.urls
