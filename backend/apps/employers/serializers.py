from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User, UserRole
from apps.catalog.models import Industry, Location
from apps.catalog.serializers import IndustrySerializer, LocationSerializer
from common.utils import absolute_media_url
from common.validators import MaxFileSizeValidator, phone_validator, tax_code_validator

from .models import Company, Recruiter


class CompanyBriefSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'logo_url', 'verification_status']

    def get_logo_url(self, obj) -> str | None:
        return absolute_media_url(self.context.get('request'), obj.logo)


class CompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        source='location', queryset=Location.objects.all(), write_only=True, allow_null=True, required=False
    )
    industry = IndustrySerializer(read_only=True)
    industry_id = serializers.PrimaryKeyRelatedField(
        source='industry', queryset=Industry.objects.all(), write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'tax_code', 'logo_url', 'website', 'email', 'phone', 'address',
            'location', 'location_id', 'industry', 'industry_id', 'company_size', 'founded_year',
            'description', 'verification_status', 'verified_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'verification_status', 'verified_at', 'created_at', 'updated_at']
        # Bỏ UniqueValidator tự sinh: kiểm tra trùng thủ công để tính cả công ty đã xóa mềm
        extra_kwargs = {'tax_code': {'validators': [tax_code_validator]}}

    def get_logo_url(self, obj) -> str | None:
        return absolute_media_url(self.context.get('request'), obj.logo)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Tên công ty không được để trống.')
        return value

    def validate_tax_code(self, value):
        value = (value or '').strip() or None
        if value and Company.all_objects.filter(tax_code=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('Mã số thuế đã được đăng ký bởi công ty khác.')
        return value

    def validate_founded_year(self, value):
        if value is not None and not 1800 <= value <= timezone.localdate().year:
            raise serializers.ValidationError('Năm thành lập không hợp lệ.')
        return value


class CompanyLogoSerializer(serializers.Serializer):
    logo = serializers.ImageField(
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            MaxFileSizeValidator(settings.COMPANY_LOGO_MAX_SIZE),
        ]
    )


class RecruiterProfileSerializer(serializers.ModelSerializer):
    """Hồ sơ cá nhân của nhà tuyển dụng (gộp trường của User và Recruiter)."""

    full_name = serializers.CharField(source='user.full_name', max_length=150)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(
        source='user.phone', max_length=20, required=False, allow_blank=True, validators=[phone_validator]
    )
    company = CompanyBriefSerializer(read_only=True)

    class Meta:
        model = Recruiter
        fields = ['id', 'full_name', 'email', 'phone', 'position', 'company_role', 'status', 'joined_at', 'company']
        read_only_fields = ['id', 'company_role', 'status', 'joined_at']


class EmployerRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, validators=[phone_validator])
    company_name = serializers.CharField(max_length=255)
    position = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        value = User.objects.normalize_email_address(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email đã được sử dụng.')
        return value

    def validate(self, attrs):
        candidate_user = User(email=attrs['email'], full_name=attrs['full_name'], role=UserRole.EMPLOYER)
        try:
            validate_password(attrs['password'], user=candidate_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs


def build_employer_profile(user, request=None) -> dict | None:
    """Phần `profile` của /auth/me/ cho role=employer (đăng ký vào accounts.registry)."""
    recruiter = Recruiter.objects.select_related('company').filter(user=user).first()
    if recruiter is None:
        return None
    return {
        'recruiter_id': str(recruiter.id),
        'position': recruiter.position,
        'company_role': recruiter.company_role,
        'status': recruiter.status,
        'company': CompanyBriefSerializer(recruiter.company, context={'request': request}).data,
    }
