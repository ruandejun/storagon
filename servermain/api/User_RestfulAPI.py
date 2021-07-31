#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  User_RestfulAPI
#  
#
#  Created by TVA on 4/2/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse

from django.conf import settings;
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from servermain.controllers import AffiliateController, BalanceController
from servermain.models import User, UserProfile, AccountBalance, WebsiteAgency, UserApply, TransactionLog
from storagon.enum import *
from storagon.tool import *
from system_configure.controllers import Tool
from munch import Munch
import redis

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework import serializers, generics, mixins, permissions, exceptions, viewsets, status
from rest_framework.decorators import action
from servermain.controllers.RestfulController import IsAffiliateProfile,IsOwnerOrNotAllow,IsOwnerOrReadOnly,ServerError,IsSignatureVerified


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username', 'date_joined', 'last_login',
				'first_name', 'last_name', 'email',
				'is_active', 'is_staff', 'is_superuser',
				'groups', 'user_permissions',
				'refererList')
		# hu cau vl
		# read_only_fields=('id', 'username', 'date_joined', 'last_login',
		# 		'first_name', 'last_name', 'email',
		# 		'is_active', 'is_staff', 'is_superuser',
		# 		'groups', 'user_permissions')

	# password = serializers.CharField(min_length=6, allow_none=True)
	refererList = serializers.SlugRelatedField(slug_field='email', read_only=True, many=True);


class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ('account_type', 'account_status', 'storage_space', 'plan_id', 'plan_expired',
				'full_name', 'email', 'address' )
		read_only_fields=('account_type', 'account_status','storage_space', 'plan_id', 'plan_expired')


class CurrentUserProfileView(viewsets.GenericViewSet):
	"""A view that returns the count of active users in JSON.
	"""
	serializer_class = UserProfileSerializer

	permission_classes = (permissions.IsAuthenticated,IsSignatureVerified)

	@action(detail=False,methods=['get'],permission_classes=[permissions.IsAuthenticated, IsSignatureVerified])
	def show(self, request, *args, **kwargs):
		slz1 = UserSerializer(instance=request.user)
		slz2 = UserProfileSerializer(instance=request.user.profile)
		merged_data = {};
		merged_data.update(slz1.data);
		merged_data.update(slz2.data);
		return Response(merged_data);

	@action(detail=False,methods=['patch'],permission_classes=[permissions.IsAuthenticated, IsSignatureVerified], serializer_class=UserProfileSerializer)
	def edit(self, request, *args, **kwargs):
		serializer = UserProfileSerializer(instance=request.user.profile, data=request.data, partial=True); #partial=True is for PATCH
		if serializer.is_valid():
			profile = serializer.save();
			if profile.email != profile.user.email:
				profile.account_status = AccountStatus.emailNotActivated;
				profile.save();
			return Response(serializer.data, status=200);
		else:
			return Response(serializer.errors, status=400);


class AccountBalanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountBalance
		fields = ('id', 'user', 'balance_type', 'amount', 'account_id')
		read_only_fields=('user', 'amount')


class CurrentUserAccountBalanceView(viewsets.GenericViewSet, generics.ListCreateAPIView):
	serializer_class = AccountBalanceSerializer
	permission_classes = (permissions.IsAuthenticated, IsAffiliateProfile)

	def get_queryset(self): #getter for queryset, overide queryset
		return AccountBalance.objects.filter(user=self.request.user);

	def perform_create(self, serializer):
		balance_type = serializer.validated_data['balance_type'];
		if balance_type not in [BalanceType.paypal,BalanceType.webmoney]:
			raise ServerError(u"You are not allowed to create this balance type");

		serializer.save(user=self.request.user) #set user = currentUser

	@action(detail=True,methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAffiliateProfile, IsOwnerOrNotAllow])
	def getNonAvaiableTransaction(self, request, *args, **kwargs):
		balance = self.get_object();
		result = AffiliateController.countNotAvailableTransactionOfBalance(balance.id);
		result2 = AffiliateController.countMoneyOnWithdrawingOfBalance(balance);
		return Tool.successResponseRestful(list(result)+result2);


class WebsiteAgencySerializer(serializers.ModelSerializer):
	class Meta:
		model = WebsiteAgency
		fields = ('user', 'created_date', 'modified_date', 'website_domain')

	user = serializers.PrimaryKeyRelatedField(read_only=True)
	created_date = serializers.DateTimeField(read_only=True)
	modified_date = serializers.DateTimeField(read_only=True)
	website_domain = serializers.CharField(min_length=4);


class CurrentUserWebsiteAgencyView(viewsets.GenericViewSet, generics.ListCreateAPIView):
	permission_classes = (permissions.IsAuthenticated, IsAffiliateProfile)
	serializer_class = WebsiteAgencySerializer

	def get_queryset(self): #getter for queryset, overide queryset
		return WebsiteAgency.objects.filter(user=self.request.user);

	def perform_create(self, serializer):
		website_address = serializer.validated_data['website_domain'];
		# print website_address;
		website_agency_domain = AffiliateController.verifyWebsiteOwner(self.request.user, website_address);
		if not website_agency_domain:
			raise ServerError(u"Unable to verify you are the owner of the website: %s"%(website_address));

		AffiliateController.addWebsiteAgency(self.request.user, website_agency_domain);
		# serializer.save(user=self.request.user) #set user = currentUser


class UserApplySerializer(serializers.ModelSerializer):
	class Meta:
		model = UserApply
		fields = ('id', 'user', 'created_date', 'apply_type', 'apply_status', 'data')
		read_only_fields=('user', 'created_date', 'apply_type', 'apply_status', 'data')


class CurrentUserUserApplyList(viewsets.GenericViewSet, generics.ListAPIView):
	permission_classes = [permissions.IsAuthenticated, IsSignatureVerified]
	serializer_class = UserApplySerializer

	def get_queryset(self): #getter for queryset, overide queryset
		return UserApply.objects.filter(user=self.request.user);


class RequestPayForm(serializers.Serializer):
	withdraw_balance_id = serializers.IntegerField(min_value=0)
	deposit_balance_id = serializers.IntegerField(min_value=0)
	withdraw_amount = serializers.IntegerField(min_value=0)


class CurrentUserUserApplyView(viewsets.GenericViewSet):
	permission_classes = [permissions.IsAuthenticated, IsSignatureVerified]

	@action(detail=False,methods=['post'], serializer_class=RequestPayForm)
	def requestPay(self, request, *args, **kwargs):
		""" requestPay \n\n
		withdraw_balance_id : serializers.IntegerField(min_value=0)
		deposit_balance_id = serializers.IntegerField(min_value=0)
		withdraw_amount = serializers.IntegerField(min_value=0)
		"""
		formPOST=RequestPayForm(data=request.data);
		if not formPOST.is_valid():
			return Tool.errorResponseRestful(formPOST.errors,code=status.HTTP_400_BAD_REQUEST);
		#::type: RequestPayForm
		data=Munch(formPOST.data)

		try: withdraw_balance = AccountBalance.objects.get(id=data.withdraw_balance_id);
		except AccountBalance.DoesNotExist:
			return Tool.errorResponseRestful(u"Withdraw balance does not exist",code=status.HTTP_400_BAD_REQUEST)

		if withdraw_balance.user!=self.request.user:
			return Tool.errorResponseRestful(u"Withdraw balance does not belong to you",code=status.HTTP_403_FORBIDDEN)

		if withdraw_balance.balance_type not in [BalanceType.credit,BalanceType.ppd]:
			return Tool.errorResponseRestful(u"Withdraw balance type is not valid",code=status.HTTP_403_FORBIDDEN)

		result=AffiliateController.countNotAvailableTransactionOfBalance(withdraw_balance.id);
		notAvailableAmount = result[0][1];
		if notAvailableAmount is None:
			notAvailableAmount=0;
		result2 = AffiliateController.countMoneyOnWithdrawingOfBalance(withdraw_balance);
		notAvailableAmount+=result2[0][1];

		if data.withdraw_amount > withdraw_balance.amount - notAvailableAmount:
			return Tool.errorResponseRestful(u"Withdraw balance type available money is insufficient",code=status.HTTP_403_FORBIDDEN)

		try: deposit_balance = AccountBalance.objects.get(id=data.deposit_balance_id);
		except AccountBalance.DoesNotExist:
			return Tool.errorResponseRestful(u"Deposit balance does not exist",code=status.HTTP_400_BAD_REQUEST)

		if deposit_balance.user!=self.request.user:
			return Tool.errorResponseRestful(u"Deposit balance does not belong to you",code=status.HTTP_403_FORBIDDEN)

		if deposit_balance.balance_type not in [BalanceType.paypal,BalanceType.webmoney]:
			return Tool.errorResponseRestful(u"Deposit balance type is not valid",code=status.HTTP_403_FORBIDDEN)

		if withdraw_balance.balance_type == BalanceType.ppd:
			deposit_amount = int(data.withdraw_amount / 1000); #1000 ppd = 1 cent
		else:
			deposit_amount = data.withdraw_amount

		if deposit_amount < 10*100:
			return Tool.errorResponseRestful(u"Withdraw ammount must greater or equal 10$",code=status.HTTP_403_FORBIDDEN)

		application = UserApply(user=self.request.user, apply_type=ApplyType.payAffiliate)

		data = {
			'withdraw_balance_id':withdraw_balance.id,
			'deposit_balance_id':deposit_balance.id,
			'withdraw_amount':data.withdraw_amount,
			'deposit_amount':deposit_amount
		}

		application.data = json.dumps(data);
		application.save();

		return Tool.successResponseRestful(data);


class InvokeDesktopClientForm(serializers.Serializer):
	invoke_type = serializers.ChoiceField(choices=InvokeType.ChoiceList(), required=True);
	invoke_data = serializers.DictField(child=serializers.CharField(), required=True);


class CurrentUserView(viewsets.GenericViewSet):
	permission_classes = [permissions.IsAuthenticated, IsSignatureVerified]

	@action(detail=False, methods=['post'], serializer_class=InvokeDesktopClientForm)
	def invokeDesktopClient(self, request, *args, **kwargs):
		formPOST=InvokeDesktopClientForm(data=request.data);
		if not formPOST.is_valid():
			return Tool.errorResponseRestful(formPOST.errors,code=status.HTTP_400_BAD_REQUEST);
		#::type: InvokeDesktopClientForm
		data=Munch(formPOST.data)
		data.invoke_data.update({'type':data.invoke_type});

		db = redis.StrictRedis(connection_pool=settings.REDIS_POOL);

		channel_name = self.request.user.username;
		try:result=db.publish(channel_name,json.dumps(data.invoke_data));
		except Exception as e:
			logging.error(u"Unable to publish message via redis error=%s");
			return Tool.errorResponseRestful(u"Unable to invoke desktop client",code=status.HTTP_500_INTERNAL_SERVER_ERROR);
		return Tool.successResponseRestful();