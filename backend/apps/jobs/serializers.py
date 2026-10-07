from datetime import timedelta

from rest_framework import serializers

from apps.accounts.serializers import UserBriefSerializer
from apps.catalog.models import Industry, Location
from apps.catalog.serializers import IndustrySerializer, LocationSerializer
from apps.employers.serializers import CompanyBriefSerializer

from . import workflow
from .models import Job, JobSkill, JobStatus

MAX_SKILLS = 30
MAX_DEADLINE_DAYS = 365


class JobSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='skill.id')
    name = serializers.CharField(source='skill.name')
    slug = serializers.CharField(source='skill.slug')

    class Meta:
        model = JobSkill
        fields = ['id', 'name', 'slug', 'is_required', 'weight', 'min_years']


class JobSkillInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    is_required = serializers.BooleanField(default=True)
    weight = serializers.IntegerField(min_value=1, max_value=5, default=3)
    min_years = serializers.DecimalField(max_digits=4, decimal_places=1, min_value=0, required=False, allow_null=True)


class _JobReadSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(help_text='Trạng thái hiệu lực (published quá hạn -> expired)')
    location = LocationSerializer(read_only=True)
    skills = JobSkillSerializer(source='job_skills', many=True, read_only=True)

    def get_status(self, obj) -> str:
        return workflow.effective_status(obj)


class EmployerJobListSerializer(_JobReadSerializer):
    applicant_count = serializers.IntegerField(read_only=True)
    new_applicant_count = serializers.IntegerField(read_only=True, help_text='Số hồ sơ mới chưa xử lý')
    allowed_actions = serializers.SerializerMethodField(help_text='Các thao tác hợp lệ: publish, pause, close, delete')

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'job_type', 'work_mode', 'level', 'salary_min', 'salary_max',
            'salary_currency', 'is_salary_negotiable', 'location', 'deadline', 'status', 'published_at',
            'closed_at', 'view_count', 'applicant_count', 'new_applicant_count', 'skills', 'allowed_actions',
            'created_at', 'updated_at',
        ]

    def get_allowed_actions(self, obj) -> list[str]:
        count = getattr(obj, 'applicant_count', None)
        has_applications = obj.applications.exists() if count is None else count > 0
        return workflow.allowed_actions(obj, has_applications=has_applications)


class EmployerJobDetailSerializer(EmployerJobListSerializer):
    industry = IndustrySerializer(read_only=True)
    company = CompanyBriefSerializer(read_only=True)
    created_by = UserBriefSerializer(read_only=True, allow_null=True)

    class Meta(EmployerJobListSerializer.Meta):
        fields = EmployerJobListSerializer.Meta.fields + [
            'description', 'requirements', 'benefits', 'min_years_experience', 'headcount', 'address',
            'industry', 'company', 'created_by',
        ]


class EmployerJobWriteSerializer(serializers.ModelSerializer):
    location_id = serializers.PrimaryKeyRelatedField(
        source='location', queryset=Location.objects.all(), allow_null=True, required=False
    )
    industry_id = serializers.PrimaryKeyRelatedField(
        source='industry', queryset=Industry.objects.all(), allow_null=True, required=False
    )
    skills = JobSkillInputSerializer(many=True, required=False)
    status = serializers.ChoiceField(
        choices=[JobStatus.DRAFT, JobStatus.PUBLISHED],
        required=False,
        help_text='Chỉ dùng khi tạo: draft (mặc định, lưu nháp) hoặc published (đăng ngay). '
        'Đổi trạng thái sau đó dùng /publish/, /pause/, /close/.',
    )

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'benefits', 'job_type', 'work_mode', 'level',
            'min_years_experience', 'salary_min', 'salary_max', 'salary_currency', 'is_salary_negotiable',
            'headcount', 'location_id', 'address', 'industry_id', 'deadline', 'skills', 'status',
        ]
        extra_kwargs = {
            'salary_min': {'min_value': 0},
            'salary_max': {'min_value': 0},
            'headcount': {'min_value': 1, 'max_value': 1000},
            'min_years_experience': {'min_value': 0, 'max_value': 50},
        }

    def _required_text(self, value, message):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(message)
        return value

    def validate_title(self, value):
        return self._required_text(value, 'Tiêu đề không được để trống.')

    def validate_description(self, value):
        return self._required_text(value, 'Mô tả công việc không được để trống.')

    def validate_requirements(self, value):
        return self._required_text(value, 'Yêu cầu ứng viên không được để trống.')

    def validate_deadline(self, value):
        if value is None or (self.instance is not None and value == self.instance.deadline):
            return value  # không đổi hạn nộp thì không kiểm tra lại (vd. sửa nội dung tin đã đóng)
        today = workflow.today()
        if value < today:
            raise serializers.ValidationError('Hạn nộp hồ sơ phải từ hôm nay trở đi.')
        if value > today + timedelta(days=MAX_DEADLINE_DAYS):
            raise serializers.ValidationError('Hạn nộp hồ sơ không được quá 1 năm kể từ hôm nay.')
        return value

    def validate_skills(self, value):
        if len(value) > MAX_SKILLS:
            raise serializers.ValidationError(f'Tối đa {MAX_SKILLS} kỹ năng.')
        return value

    def validate_status(self, value):
        if self.instance is not None:
            raise serializers.ValidationError('Dùng các API publish / pause / close để đổi trạng thái tin.')
        return value

    def validate(self, attrs):
        def current(field):
            return attrs.get(field, getattr(self.instance, field, None))

        salary_min, salary_max = current('salary_min'), current('salary_max')
        if salary_min is not None and salary_max is not None and salary_max < salary_min:
            raise serializers.ValidationError({'salary_max': 'Lương tối đa phải lớn hơn hoặc bằng lương tối thiểu.'})
        return attrs


class PublicJobListSerializer(_JobReadSerializer):
    company = CompanyBriefSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'location', 'job_type', 'work_mode', 'level', 'salary_min',
            'salary_max', 'salary_currency', 'is_salary_negotiable', 'deadline', 'skills', 'status',
            'published_at', 'created_at',
        ]


class PublicJobDetailSerializer(PublicJobListSerializer):
    industry = IndustrySerializer(read_only=True)

    class Meta(PublicJobListSerializer.Meta):
        fields = PublicJobListSerializer.Meta.fields + [
            'description', 'requirements', 'benefits', 'min_years_experience', 'headcount', 'address',
            'industry', 'application_count', 'view_count',
        ]
