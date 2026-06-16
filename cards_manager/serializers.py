from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    used_by_username = serializers.CharField(source='used_by.username', read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'card_number', 'expiry_date', 'cvv', 'status', 
            'extra_info', 'used_count', 'created_at', 'updated_at',
            'owner', 'used_by', 'owner_username', 'used_by_username'
        ]
