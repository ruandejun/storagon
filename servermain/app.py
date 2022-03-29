#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  app.py
#  
#
#  Created by TVA on 3/30/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#
# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.conf import settings
from mongoengine import connect
import os, geoip2.database
import redis


class MyAppConfig(AppConfig):
    name = 'servermain'
    # verbose_name = u'Server chủ'

    def ready(self):
        import servermain.models_signals

        if settings.IS_RUNNING_UNIT_TEST:
            settings.MONGODB['NAME']='storagon_test';
            print ("Change MONGODB to test DB:%s"%(settings.MONGODB['NAME']))

            settings.CACHES = {
                'default': { #Simple Local MemCache (not work well with django-cache-machine)
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'storagon-cache',
                'PREFIX': 'storagon_',
                'TIMEOUT': None, #Keep cache forever, or for seconds
                'OPTIONS': {
                    'MAX_ENTRIES': 2000 #max number of row cached
                }
            }}
            print ("Change Cache BACKEND to LocMemCache")
        # mongodb_host = 'mongodb://'+settings.MONGODB['USER']+':'+settings.MONGODB['PASSWORD']+'@'+settings.MONGODB['HOST']+':'+str(settings.MONGODB['PORT'])+'/'+settings.MONGODB['NAME']
        # db_connection = connect(host=mongodb_host, alias='default', tz_aware=settings.USE_TZ)
        # db_connection = connect(db=settings.MONGODB['NAME'], host=settings.MONGODB['HOST'], port=settings.MONGODB['PORT'], alias='default', tz_aware=settings.USE_TZ)

         # "Create connection to mongoDB"
        #
        # if settings.IS_RUNNING_UNIT_TEST:
        #     db_connection.drop_database(settings.MONGODB['NAME'])
        #     print ("Clear MONGODB on launch")

        redis_password = None
        if settings.REDISDB['PASSWORD']: redis_password=settings.REDISDB['PASSWORD'];
        settings.REDIS_POOL = redis.ConnectionPool(host=settings.REDISDB['HOST'], port=settings.REDISDB['PORT'], db=settings.REDISDB['DB'], password=redis_password)
        #"Create connection pool to redis"

        settings.geo_reader = geoip2.database.Reader(os.path.join(settings.BASE_DIR, 'GeoLite2-Country.mmdb'));
        #"Load GeoIP2 database completed";