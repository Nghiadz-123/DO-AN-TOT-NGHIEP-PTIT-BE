from datetime import date

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User, UserRole
from apps.catalog.models import Location
from apps.catalog.serializers import LocationSerializer
from common.validators import phone_validator

from .models import CandidateProfile

# Bộ luật Lao động 2019: người lao động từ đủ 15 tuổi
MIN_AGE = 15
MAX_AGE = 100
# Giống jobs.models.SalaryCurrency (candidates không import jobs - xem quy tắc phụ thuộc)
SALARY_CURRENCIES = ['VND', 'USD']


def _years_before(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:  # 29/02 của năm không nhuận
        return day.replace(year=day.year - years, day=28)


class CandidateProfileSerializer(serializers.ModelSerializer):
    """Hồ sơ ứng viên (gộp trường của User và CandidateProfile)."""

    full_name = serializers.CharField(source='user.full_name', max_length=150)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(
        source='user.phone', max_length=20, required=False, allow_blank=True, validators=[phone_validator]
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        source='location', queryset=Location.objects.all(), write_only=True, allow_null=True, required=False
    )
    salary_currency = serializers.ChoiceField(choices=SALARY_CURRENCIES, required=False)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'full_name', 'email', 'phone', 'headline', 'date_of_birth', 'gender', 'address', 'location',
            'location_id', 'summary', 'years_of_experience', 'current_level', 'desired_position',
            'desired_salary_min', 'desired_salary_max', 'salary_currency', 'desired_job_type', 'desired_work_mode',
            'is_open_to_work', 'is_public', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'years_of_experience': {'min_value': 0, 'max_value': 50},
            'desired_salary_min': {'min_value': 0},
            'desired_salary_max': {'min_value': 0},
        }

    def validate_date_of_birth(self, value):
        if value is None:
            return value
        today = timezone.localdate()
        if not _years_before(today, MAX_AGE) <= value <= _years_before(today, MIN_AGE):
            raise serializers.ValidationError(f'Ngày sinh không hợp lệ (ứng viên từ {MIN_AGE} đến {MAX_AGE} tuổi).')
        return value

    def validate(self, attrs):
        def current(field):
            return attrs.get(field, getattr(self.instance, field, None))

        salary_min, salary_max = current('desired_salary_min'), current('desired_salary_max')
        if salary_min is not None and salary_max is not None and salary_max < salary_min:
            raise serializers.ValidationError(
                {'desired_salary_max': 'Mức lương mong muốn tối đa phải lớn hơn hoặc bằng mức tối thiểu.'}
            )
        return attrs


class CandidateRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, validators=[phone_validator])

    def validate_email(self, value):
        value = User.objects.normalize_email_address(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email đã được sử dụng.')
        return value

    def validate(self, attrs):
        candidate_user = User(email=attrs['email'], full_name=attrs['full_name'], role=UserRole.CANDIDATE)
        try:
            validate_password(attrs['password'], user=candidate_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs


def build_candidate_profile(user, request=None) -> dict | None:
    """Phần `profile` của /auth/me/ cho role=candidate (đăng ký vào accounts.registry)."""
    profile = CandidateProfile.objects.filter(user=user).first()
    if profile is None:
        return None
    return {
        'candidate_id': str(profile.id),
        'headline': profile.headline,
        'is_open_to_work': profile.is_open_to_work,
        # Đếm qua quan hệ ngược `cvs` (chỉ dùng ORM, không import app cvs). Frontend dựa vào đây
        # để đưa ứng viên chưa có CV tới trang tải CV.
        'cv_count': profile.cvs.count(),
    }
