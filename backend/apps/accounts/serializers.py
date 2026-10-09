from django.contrib.auth.password_validation import validate_password
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from common.validators import phone_validator

from . import registry
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Thông tin tài khoản + `profile` theo vai trò (employer: recruiter & công ty)."""

    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'created_at', 'profile']
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_profile(self, user):
        return registry.get_profile(user, request=self.context.get('request'))


class UserBriefSerializer(serializers.Serializer):
    """Người thao tác (người đăng tin, người đổi trạng thái hồ sơ...)."""

    id = serializers.UUIDField()
    full_name = serializers.CharField()


class AccountUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, validators=[phone_validator])


class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Email hoặc mật khẩu không đúng.'}

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user, context=self.context).data
        return data


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class SessionSerializer(TokenPairSerializer):
    """Response của đăng nhập / đăng ký."""

    user = UserSerializer()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'Mật khẩu mới phải khác mật khẩu hiện tại.'})
        validate_password(attrs['new_password'], user=self.context['request'].user)
        return attrs
