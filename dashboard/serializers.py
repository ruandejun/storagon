from rest_framework import serializers
from django.contrib.auth.models import User
from servermain.models import UserProfile
from telegram_bot.models import UserHwid

class DashboardUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(source='profile.address', required=False, allow_blank=True, allow_null=True)
    account_type = serializers.IntegerField(source='profile.account_type', required=False)
    account_status = serializers.IntegerField(source='profile.account_status', required=False)
    storage_space = serializers.IntegerField(source='profile.storage_space', required=False)
    plan_id = serializers.IntegerField(source='profile.plan_id', required=False)
    plan_expired = serializers.DateTimeField(source='profile.plan_expired', required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'full_name', 'address', 'account_type',
            'account_status', 'storage_space', 'plan_id', 'plan_expired'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        # Update automatically created profile
        profile = getattr(user, 'profile', None)
        if profile:
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()

        profile = getattr(instance, 'profile', None)
        if profile:
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class UserHwidSerializer(serializers.ModelSerializer):
    """Serializer for UserHwid - HWID records for MunLogin tool access control"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = UserHwid
        fields = (
            'id', 'user', 'user_id', 'username', 'user_email',
            'value', 'note', 'status', 'status_label',
            'created', 'modified'
        )
        read_only_fields = ('id', 'created', 'modified', 'username', 'user_email', 'user_id')

    def get_status_label(self, obj):
        STATUS_MAP = {0: 'Active', 1: 'Suspended', 2: 'Banned'}
        return STATUS_MAP.get(obj.status, 'Unknown')

from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'message', 'is_read', 'created_at')
