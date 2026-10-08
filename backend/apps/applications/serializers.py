from django.urls import reverse
from rest_framework import serializers

from apps.accounts.serializers import UserBriefSerializer
from apps.candidates.models import CandidateProfile
from apps.catalog.serializers import LocationSerializer
from apps.cvs import selectors as cv_selectors
from apps.cvs.models import CV
from apps.employers.serializers import CompanyBriefSerializer
from apps.jobs import workflow as job_workflow
from apps.jobs.models import Job, JobStatus

from . import workflow
from .models import Application, ApplicationStatus, ApplicationStatusHistory


class CandidateBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    location = LocationSerializer(read_only=True)

    class Meta:
        model = CandidateProfile
        fields = ['id', 'full_name', 'email', 'phone', 'headline', 'years_of_experience', 'current_level', 'location']


class CandidateDetailSerializer(CandidateBriefSerializer):
    class Meta(CandidateBriefSerializer.Meta):
        fields = CandidateBriefSerializer.Meta.fields + [
            'summary', 'date_of_birth', 'gender', 'address', 'desired_position', 'is_open_to_work',
        ]


class CVBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['id', 'title', 'original_filename', 'mime_type', 'file_size', 'created_at']


class JobRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title']


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserBriefSerializer(read_only=True, allow_null=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ['id', 'from_status', 'to_status', 'note', 'changed_by', 'created_at']


class EmployerApplicationListSerializer(serializers.ModelSerializer):
    job = JobRefSerializer(read_only=True)
    candidate = CandidateBriefSerializer(read_only=True)
    cv = CVBriefSerializer(read_only=True)
    applied_at = serializers.DateTimeField(source='created_at', read_only=True)
    allowed_transitions = serializers.SerializerMethodField(help_text='Các trạng thái có thể chuyển tới')

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'candidate', 'cv', 'status', 'recruiter_rating', 'applied_at', 'status_changed_at',
            'allowed_transitions',
        ]

    def get_allowed_transitions(self, obj) -> list[str]:
        return workflow.allowed_transitions(obj.status)


class EmployerApplicationDetailSerializer(EmployerApplicationListSerializer):
    candidate = CandidateDetailSerializer(read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    cv_download_url = serializers.SerializerMethodField()

    class Meta(EmployerApplicationListSerializer.Meta):
        fields = EmployerApplicationListSerializer.Meta.fields + [
            'cover_letter', 'rejection_reason', 'status_history', 'cv_download_url',
        ]

    def get_cv_download_url(self, obj) -> str:
        url = reverse('employer-application-cv', args=[obj.pk])
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


class ApplicationStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(s, ApplicationStatus(s).label) for s in workflow.EMPLOYER_TARGET_STATUSES])
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000, default='')
    rejection_reason = serializers.CharField(required=False, allow_blank=True, max_length=2000, default='')


class ApplicationRatingSerializer(serializers.Serializer):
    recruiter_rating = serializers.IntegerField(min_value=1, max_value=5, allow_null=True)


class JobStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    draft = serializers.IntegerField()
    published = serializers.IntegerField()
    paused = serializers.IntegerField()
    closed = serializers.IntegerField()
    expired = serializers.IntegerField()


class ApplicationStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    new_last_7_days = serializers.IntegerField()
    applied = serializers.IntegerField()
    screening = serializers.IntegerField()
    interview = serializers.IntegerField()
    offer = serializers.IntegerField()
    hired = serializers.IntegerField()
    rejected = serializers.IntegerField()
    withdrawn = serializers.IntegerField()


class EmployerDashboardSerializer(serializers.Serializer):
    jobs = JobStatsSerializer()
    applications = ApplicationStatsSerializer()
    recent_applications = EmployerApplicationListSerializer(many=True)


# ============================================================================ phía ứng viên
class CandidateJobBriefSerializer(serializers.ModelSerializer):
    """Tin đã ứng tuyển, nhìn từ phía ứng viên."""

    company = CompanyBriefSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    status = serializers.SerializerMethodField(help_text='Trạng thái hiệu lực của tin (published quá hạn -> expired)')

    class Meta:
        model = Job
        fields = ['id', 'title', 'slug', 'company', 'location', 'status', 'deadline']

    def get_status(self, obj) -> str:
        return job_workflow.effective_status(obj)


class CandidateStatusHistorySerializer(serializers.ModelSerializer):
    """Lịch sử trạng thái cho ứng viên: không gồm ghi chú nội bộ và người thao tác phía NTD."""

    class Meta:
        model = ApplicationStatusHistory
        fields = ['from_status', 'to_status', 'created_at']


class CandidateApplicationListSerializer(serializers.ModelSerializer):
    """Hồ sơ đã nộp. Không trả đánh giá, lý do từ chối, ghi chú nội bộ của nhà tuyển dụng."""

    job = CandidateJobBriefSerializer(read_only=True)
    cv = CVBriefSerializer(read_only=True)
    applied_at = serializers.DateTimeField(source='created_at', read_only=True)
    can_withdraw = serializers.SerializerMethodField(help_text='Ứng viên còn được rút hồ sơ này không')

    class Meta:
        model = Application
        fields = ['id', 'job', 'cv', 'status', 'applied_at', 'status_changed_at', 'can_withdraw']

    def get_can_withdraw(self, obj) -> bool:
        return workflow.can_withdraw(obj.status)


class CandidateApplicationDetailSerializer(CandidateApplicationListSerializer):
    status_history = CandidateStatusHistorySerializer(many=True, read_only=True)

    class Meta(CandidateApplicationListSerializer.Meta):
        fields = CandidateApplicationListSerializer.Meta.fields + ['cover_letter', 'status_history']


class CandidateApplySerializer(serializers.Serializer):
    # Bản nháp / tin của công ty đã xóa coi như không tồn tại; tin đã đóng, hết hạn do service báo lỗi
    job_id = serializers.PrimaryKeyRelatedField(
        source='job',
        queryset=Job.objects.exclude(status=JobStatus.DRAFT).filter(company__deleted_at__isnull=True),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Tin tuyển dụng không tồn tại.'},
    )
    cv_id = serializers.UUIDField(required=False, allow_null=True, help_text='Bỏ trống: dùng CV mặc định')
    cover_letter = serializers.CharField(required=False, allow_blank=True, max_length=5000, default='')

    def validate(self, attrs):
        candidate = self.context['candidate']
        cv_id = attrs.pop('cv_id', None)
        if cv_id:
            cv = cv_selectors.get_candidate_cv(candidate, cv_id)
            if cv is None:
                raise serializers.ValidationError({'cv_id': 'CV không tồn tại.'})
        else:
            cv = cv_selectors.get_default_cv(candidate)
            if cv is None:
                raise serializers.ValidationError({'cv_id': 'Bạn chưa có CV. Vui lòng tải lên CV trước khi ứng tuyển.'})
        attrs['cv'] = cv
        return attrs


class CandidateWithdrawSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False, allow_blank=True, max_length=2000, default='', help_text='Lý do rút (nhà tuyển dụng xem được)'
    )
