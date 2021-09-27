#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  File_RestfulAPI
#  
#
#  Created by TVA on 4/14/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#

from django import shortcuts
from django.template import RequestContext
from django.http import *
from django.urls import reverse

from django.conf import settings;
from django.utils import timezone

from servermain.controllers import AffiliateController,FileController,RestfulController
from servermain.models import User,UserFile,Folder,RealFile
from storagon.enum import *
from storagon.tool import *

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
import base64
from rest_framework import serializers,generics,mixins,permissions,exceptions,viewsets
from rest_framework import routers,views,response
from rest_framework.decorators import action
import rest_framework_bulk as restbulk


class UserFileSerializer(restbulk.BulkSerializerMixin,serializers.ModelSerializer):
	class Meta:
		model=UserFile
		list_serializer_class=restbulk.BulkListSerializer # only necessary in DRF3

		fields=('id','user','created_date','modified_date','realFile','last_download_date','download_count','file_name',
				'folder','file_mode','file_size','file_hash','string_id'#,'download_url'
		)
		read_only_fields=('id','user','realFile','last_download_date','download_count','file_size','file_hash','string_id')

	# user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
	file_name=serializers.CharField(min_length=1,required=False)
	folder=serializers.PrimaryKeyRelatedField(queryset=Folder.objects,required=False,allow_null=True)
	file_mode=serializers.ChoiceField(choices=FileMode.ChoiceList(),default=FileMode.normal,required=False)


#extra
# download_url = serializers.CharField(source='get_absolute_url', read_only=True)


# class UserFileViewSet(viewsets.ModelViewSet):
# 	""" A simple ViewSet for viewing and editing accounts.
# 	"""
# 	queryset = UserFile.objects.all()
# 	serializer_class = UserFileSerializer
# 	permission_classes = [permissions.IsAuthenticated]


class UserFileWithDownloadLinkSerialier(UserFileSerializer):
	class Meta:
		model=UserFile
		list_serializer_class=restbulk.BulkListSerializer # only necessary in DRF3

		fields=('id','user','created_date','modified_date','realFile','last_download_date','download_count','file_name',
				'folder','file_mode','file_size','file_hash','download_url','download_url2',
		)
		read_only_fields=('id','user','realFile','last_download_date','download_count','file_size','file_hash')

	# download_url=serializers.SerializerMethodField();
	download_url2=serializers.SerializerMethodField();

	# def get_download_url(self,obj):
	# 	return obj.get_absolute_url(withFileKey=True,usingDownloadViewNumber=1)

	def get_download_url2(self,obj):
		return obj.get_absolute_url(withFileKey=True,usingDownloadViewNumber=2)


class CurrentUserFileView(viewsets.GenericViewSet,
						mixins.ListModelMixin,
						restbulk.BulkUpdateAPIView,
						restbulk.BulkDestroyAPIView):
	""" LIST GET: ?file_name=words in file_name&file_id=1&file_id=2&folder_id=3
	"""
	filtered=False;
	# queryset = UserFile.objects.all()
	permission_classes=[permissions.IsAuthenticated]

	def get_queryset(self): #getter for queryset, overide queryset
		query=UserFile.objects.filter(user=self.request.user).select_related('realFile');
		file_name,fileIDList,folder_id=getParamsOrRaise400(self.request.query_params,('file_name',''),('file_id',[]),('folder_id',-1));

		if file_name: query=query.filter(file_name__icontains=file_name);
		if fileIDList:
			query=query.filter(id__in=fileIDList);
			self.filtered=True;
		if folder_id>=0:
			if folder_id==0: folder_id=None;
			query=query.filter(folder_id=folder_id);
		# cache timeout in 7 seconds, to avoid wrong cache of this
		query.timeout=7

		return query;

	# serializer_class=UserFileSerializer
	def get_serializer_class(self):
		if self.request.query_params.get('get_download_link','n')!='n':
			return UserFileWithDownloadLinkSerialier;

		return UserFileSerializer

	# renderer_classes=(JSONRenderer, )

	def allow_bulk_destroy(self,qs,filtered):
		"""
		Hook to ensure that the bulk destroy should be allowed.
		By default this checks that the destroy is only applied to
		filtered querysets.
		"""
		return self.filtered

	# def patch(self, request, *args, **kwargs):
	# 	file_mode = getParamsOrRaise400(self.request.data, ('file_mode', int));
	# 	self.get_queryset().update(file_mode=file_mode, modified_date=timezone.now())
	# 	return Response({'detail': 'success'}, status=200);


class FolderSerializer(restbulk.BulkSerializerMixin,serializers.ModelSerializer):
	class Meta:
		model=Folder
		list_serializer_class=restbulk.BulkListSerializer # only necessary in DRF3

		fields=('id','user','created_date','modified_date','name','parent_folder','folder_type')
		read_only_fields=('id','user','created_date','modified_date')

	user=serializers.PrimaryKeyRelatedField(read_only=True,default=serializers.CurrentUserDefault())
	name=serializers.CharField(min_length=1,required=False)
	parent_folder=serializers.PrimaryKeyRelatedField(queryset=Folder.objects,required=False,allow_null=True)
	folder_type=serializers.ChoiceField(choices=FolderType.ChoiceList(),default=FolderType.normal,required=False)


class FolderWithSubFolderAndFileSerializer(FolderSerializer):
	class Meta:
		model=Folder
		list_serializer_class=restbulk.BulkListSerializer # only necessary in DRF3

		fields=(
		'id','user','created_date','modified_date','name','parent_folder','folder_type','fileList','subFolderList')
		read_only_fields=('id','user','created_date','modified_date')

	fileList=UserFileSerializer(many=True,read_only=True)
	subFolderList=FolderSerializer(many=True,read_only=True)


class CurrentUserFolderView(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.ListModelMixin,
							restbulk.BulkCreateAPIView,restbulk.BulkUpdateAPIView,
							restbulk.BulkDestroyAPIView): #restbulk.ListBulkCreateUpdateDestroyAPIView
	filtered=False;
	# queryset = Folder.objects.all()
	permission_classes=[permissions.IsAuthenticated]

	def get_queryset(self): #getter for queryset, overide queryset
		query=Folder.objects.filter(user=self.request.user)
		name,folderIDList,parent_folder_id=getParamsOrRaise400(self.request.query_params,('name',''),('folder_id',[]),
															   ('parent_folder_id',-1));

		if name: query=query.filter(name__icontains=name);
		if folderIDList:
			query=query.filter(id__in=folderIDList);
			self.filtered=True;
		if parent_folder_id>=0:
			if parent_folder_id==0: parent_folder_id=None;
			query=query.filter(parent_folder_id=parent_folder_id);

		if self.request.query_params.get('get_list_dir','n')!='n':
			query=query.prefetch_related('fileList__realFile'); #improve performance

		# cache timeout in 7 seconds, to avoid wrong cache of this
		query.timeout=7

		return query;

	# serializer_class=FolderSerializer
	def get_serializer_class(self):
		if self.request.query_params.get('get_list_dir','n')!='n':
			return FolderWithSubFolderAndFileSerializer;
		return FolderSerializer

	# renderer_classes=(JSONRenderer, )

	def allow_bulk_destroy(self,qs,filtered):
		"""
		Hook to ensure that the bulk destroy should be allowed.
		By default this checks that the destroy is only applied to
		filtered querysets.
		"""
		return self.filtered

	def bulk_update(self,request,*args,**kwargs):
		reponse=super(CurrentUserFolderView,self).bulk_update(request,*args,**kwargs);

		for folderData in reponse.data:
			folderData['user_id']=folderData.pop('user');
			folderData['parent_folder_id']=folderData.pop('parent_folder');
			folder=Folder(**folderData);
			FileController.autoMergeFolderWithSameNameInSameFolder(folder);

		return reponse

	# def list(self, request, *args, **kwargs):
	# 	response = super(CurrentUserFolderView, self).list(request, *args, **kwargs);
	# 	# return response;
	# 	data=[];
	# 	for folderData in response.data:
	# 		folderData = Folder(**folderData);
	# 		data+=[folderData.id];
	#
	# 	return Response(data, status=status.HTTP_200_OK)

	@action(detail=True,methods=['get'],permission_classes=[permissions.IsAuthenticated])
	def backTrace(self,request,pk=None):
		folder=getObjectOr404(Folder,id=pk);

		if folder.user!=self.request.user:
			return errorResponseRestful(u"You are not the owner",code=status.HTTP_403_FORBIDDEN);
		backTrace=FileController.backTraceFolder(folder);
		seriliazer=FolderSerializer(instance=backTrace,many=True);
		return successResponseRestful(seriliazer.data)


class BackTraceFolderSerializer(serializers.Serializer):
	folder_id=serializers.PrimaryKeyRelatedField(queryset=Folder.objects,required=True,allow_null=False)


class FolderAPI(viewsets.ViewSet):
	"""
	Back trace a folder back to root folder

	**POST:**

	``folder_id``
		An id of instance of :model:`servermain.Folder`.

	**Response:**

	``200:``
		[folder1, folder2, folder3, folder4]
		that folder 1 is parent of folder2, folder 2 is parrent of folder 3 and so on so on

	*JSON*
	"""
	permission_classes=(permissions.IsAuthenticated)
	serializer_class=BackTraceFolderSerializer

	@action(detail=False,methods=['post'],permission_classes=[permissions.IsAuthenticated])
	def backTrace(self,request,*args,**kwargs):
		# folder_id = getParamsOrRaise400(request.data, 'folder_id');

		formPOST=BackTraceFolderSerializer(data=request.data);
		if not formPOST.is_valid():
			return errorResponseRestful(formPOST.errors,code=status.HTTP_400_BAD_REQUEST);

		folder=getObjectOr404(Folder,id=formPOST.data['folder_id']);

		if folder.user!=self.request.user:
			return errorResponseRestful(u"You are not the owner",code=status.HTTP_403_FORBIDDEN);
		backTrace=FileController.backTraceFolder(folder);
		seriliazer=FolderSerializer(instance=backTrace,many=True);
		return successResponseRestful(seriliazer.data)