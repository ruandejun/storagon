#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  TelegramBot_RestfulAPI



from storagon.enum import *
from rest_framework import serializers
import rest_framework_bulk as restbulk
from telegram_bot.models import AccountsSelling

class AccountsSellingSerializer(restbulk.BulkSerializerMixin,serializers.ModelSerializer):
	class Meta:
		model=AccountsSelling
		list_serializer_class=restbulk.BulkListSerializer # only necessary in DRF3

		fields=('id','created','created_by','modified','modified_by','warranty_date','warranty','customer','type','ordered','ordered_date','owner','details','note','price','selling_status')
		# read_only_fields=('id','user','created_date','modified_date')


	created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

	modified_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

	customer = serializers.SlugRelatedField(slug_field='username')

	owner = serializers.SlugRelatedField(slug_field='username')