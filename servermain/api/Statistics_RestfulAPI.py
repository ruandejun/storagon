#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  Statistics_RestfulAPI.py
#  
#
#  Created by TVA on 6/9/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from system_configure.controllers.Tool import *
from system_configure.controllers import SystemConfigureController
from servermain.models import AccountBalance
from servermain.controllers import StatisticsController, AffiliateController, RestfulController
from storagon.enum import *
from django.utils import timezone
from munch import Munch
from rest_framework.response import Response
from rest_framework import status

from rest_framework import serializers, generics, mixins, permissions, exceptions, viewsets
from rest_framework.decorators import action


class BlankForm(serializers.Serializer):pass;


class TransactionStatisticsFilterForm(serializers.Serializer):
	# user_id = serializers.IntegerField(min_value=0);
	from_date = serializers.DateField();
	to_date = serializers.DateField(default=timezone.datetime.today());


class AffiliateStatisticsAPI(viewsets.GenericViewSet):

	@action(detail=False,methods=['get'], serializer_class=TransactionStatisticsFilterForm, permission_classes=[permissions.IsAuthenticated, RestfulController.IsSignatureVerified])
	def transactionStatistics(self, request, *args, **kwargs):
		formPOST=TransactionStatisticsFilterForm(data=request.query_params);
		if not formPOST.is_valid():
			return errorResponseRestful(formPOST.errors,code=status.HTTP_400_BAD_REQUEST);
		#::type: TransactionStatisticsFilterForm
		data=Munch(formPOST.data)

		from_date = timezone.datetime.strptime(data.from_date, "%Y-%m-%d")
		to_date = timezone.datetime.strptime(data.to_date, "%Y-%m-%d")
		today = timezone.now()
		if to_date.year == today.year and to_date.month == today.month and to_date.day == today.day:
			to_date = today

		downloadRaw = StatisticsController.countSessionByDayOfFileOwnerUser(self.request.user.id, SessionType.download,SessionStatus.completed,from_date,to_date)

		ppdRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.ppd,from_date,to_date)
		billRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.agency,from_date,to_date)
		rebillRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.rebill,from_date,to_date)
		websiteRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.website,from_date,to_date)
		refererRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.referer,from_date,to_date)
		refererPPDRaw = StatisticsController.countAndSumTransactionByDayOfUser(self.request.user.id,TransactionType.refererPPD,from_date,to_date)
		return successResponseRestful({
			'downloadRaw': downloadRaw,
			'ppd': ppdRaw,
			'bill': billRaw,
			'rebill': rebillRaw,
			'website': websiteRaw,
			'referer': refererRaw,
			'refererPPD': refererPPDRaw,
		})