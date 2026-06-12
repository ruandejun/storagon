from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'card_number', 'expiry_date', 'cvv', 'status', 'extra_info', 'used_count', 'created_at', 'updated_at']
