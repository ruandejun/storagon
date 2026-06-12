#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework import serializers, viewsets, permissions, filters
from servermain.models import Card

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'card_number', 'expiry_date', 'cvv', 'status', 'extra_info', 'created_date', 'modified_date')
        read_only_fields = ('id', 'created_date', 'modified_date')

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['card_number', 'status']
    ordering_fields = ['created_date', 'modified_date', 'id']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Card.objects.all()
        return Card.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
