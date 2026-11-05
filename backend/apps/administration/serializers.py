"""Dữ liệu vào / ra của API trang quản trị hệ thống."""
from rest_framework import serializers

from apps.accounts.models import User, UserRole
from apps.employers.models import Company, VerificationStatus
from apps.jobs.models import Job, JobStatus

from .selectors import LIST_LIMIT, RECENT_LIMIT

INVALID_STATUS = 'Trạng thái không hợp lệ.'
INVALID_STATUS_MESSAGES = {'required': INVALID_STATUS, 'null': INVALID_STATUS, 'invalid_choice': INVALID_STATUS}


# ============================================================================ dữ liệu vào: query string
class AdminUserQuerySerializer(serializers.Serializer):
    role = serializers.CharField(
        required=False, allow_blank=True, default='', help_text='Lọc theo vai trò: candidate, employer, admin'
    )
    q = serializers.CharField(
        required=False, allow_blank=True, default='', help_text='Tìm theo email, họ tên hoặc số điện thoại'
    )


class AdminCompanyQuerySerializer(serializers.Serializer):
    status = serializers.CharField(
        required=False, allow_blank=True, default='', help_text='Lọc theo trạng thái xác minh: pending, verified, rejected'
    )
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tìm theo tên doanh nghiệp')


class AdminJobQuerySerializer(serializers.Serializer):
    status = serializers.CharField(
        required=False, allow_blank=True, default='', help_text='Lọc theo trạng thái tin: draft, published, paused, closed'
    )
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tìm theo tiêu đề tin')


# ============================================================================ dữ liệu vào: body
class AdminUserUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False, help_text='false: khóa tài khoản, true: mở khóa')
    role = serializers.ChoiceField(choices=UserRole.choices, required=False)


class AdminCompanyUpdateSerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(
        choices=VerificationStatus.choices, error_messages=INVALID_STATUS_MESSAGES
    )


class AdminJobUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=JobStatus.choices, error_messages=INVALID_STATUS_MESSAGES)


# ============================================================================ dữ liệu trả về
class AdminUserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at']


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'is_active', 'is_staff', 'created_at']


class AdminCompanyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'tax_code', 'verification_status', 'created_at']


class AdminCompanySerializer(serializers.ModelSerializer):
    """Mã số thuế, thông tin liên hệ chưa có (NULL) trả về chuỗi rỗng."""

    class Meta:
        model = Company
        fields = ['id', 'name', 'tax_code', 'verification_status', 'phone', 'email', 'website', 'created_at']

    def to_representation(self, company):
        data = super().to_representation(company)
        for field in ('tax_code', 'phone', 'email', 'website'):
            data[field] = data[field] or ''
        return data


class AdminCompanyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'verification_status']


class AdminJobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'company_name', 'status', 'job_type', 'level', 'created_at']


class AdminJobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'status']


class AdminOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    candidates_count = serializers.IntegerField()
    employers_count = serializers.IntegerField()
    total_companies = serializers.IntegerField()
    pending_companies = serializers.IntegerField(help_text='Doanh nghiệp chờ xác minh')
    total_jobs = serializers.IntegerField()
    published_jobs = serializers.IntegerField(help_text='Tin có trạng thái published')
    total_applications = serializers.IntegerField()
    recent_users = AdminUserBriefSerializer(many=True, help_text=f'{RECENT_LIMIT} người dùng mới nhất')
    recent_companies = AdminCompanyBriefSerializer(many=True, help_text=f'{RECENT_LIMIT} doanh nghiệp mới nhất')


class AdminUserListSerializer(serializers.Serializer):
    results = AdminUserSerializer(many=True, help_text=f'Tối đa {LIST_LIMIT} người dùng mới nhất')
    count = serializers.IntegerField(help_text='Tổng số người dùng khớp bộ lọc')


class AdminCompanyListSerializer(serializers.Serializer):
    results = AdminCompanySerializer(many=True, help_text=f'Tối đa {LIST_LIMIT} doanh nghiệp mới nhất')
    count = serializers.IntegerField(help_text='Tổng số doanh nghiệp khớp bộ lọc')


class AdminJobListSerializer(serializers.Serializer):
    results = AdminJobSerializer(many=True, help_text=f'Tối đa {LIST_LIMIT} tin mới nhất')
    count = serializers.IntegerField(help_text='Tổng số tin khớp bộ lọc')
