from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer tra ve thong tin user, khong co password."""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'company_name', 'phone']
        read_only_fields = ['id', 'email', 'role']


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    role = serializers.ChoiceField(choices=[User.CANDIDATE, User.RECRUITER])
    company_name = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError('Email đã được sử dụng.')
        return normalized

    def validate(self, data):
        if data.get('role') == User.RECRUITER and not data.get('company_name', '').strip():
            raise serializers.ValidationError({'company_name': 'Nhà tuyển dụng phải cung cấp tên công ty.'})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email'].strip().lower()
        password = data['password']
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError({'detail': 'Email hoặc mật khẩu không đúng.'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Tài khoản đã bị khóa.'})
        data['user'] = user
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'company_name', 'phone']
