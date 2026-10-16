from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.candidates.models import CandidateProfile
from apps.catalog.serializers import LocationSerializer
from apps.jobs import workflow as job_workflow
from apps.jobs.models import Job
from apps.jobs.serializers import PublicJobListSerializer

from .models import Invitation, InvitationStatus
from .services import MESSAGE_MAX_LENGTH


class InvitationCreateSerializer(serializers.Serializer):
    candidate_id = serializers.PrimaryKeyRelatedField(
        source='candidate',
        queryset=CandidateProfile.objects.all(),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Không tìm thấy ứng viên.'},
        help_text='Id hồ sơ ứng viên (candidate.id trong danh sách Tìm ứng viên / Ứng viên phù hợp)',
    )
    job_id = serializers.PrimaryKeyRelatedField(
        source='job',
        queryset=Job.objects.all(),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Tin tuyển dụng không tồn tại.'},
        help_text='Tin đang tuyển của công ty',
    )
    message = serializers.CharField(max_length=MESSAGE_MAX_LENGTH, help_text='Nội dung thư mời')


class InvitationSenderSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    position = serializers.CharField(help_text='Chức danh của nhà tuyển dụng')


class _InvitationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(help_text='Nhà tuyển dụng gửi thư (null: tài khoản đã bị xóa)')
    application_id = serializers.UUIDField(
        read_only=True, allow_null=True, help_text='Hồ sơ ứng viên đã nộp vào tin (khi status = accepted)'
    )

    @extend_schema_field(InvitationSenderSerializer(allow_null=True))
    def get_sender(self, obj):
        if obj.sender is None:
            return None
        recruiter = getattr(obj.sender, 'recruiter', None)
        return {'full_name': obj.sender.get_full_name(), 'position': getattr(recruiter, 'position', '')}


class InvitationJobSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(help_text='Trạng thái hiệu lực của tin (published quá hạn -> expired)')

    class Meta:
        model = Job
        fields = ['id', 'title', 'status']

    def get_status(self, obj) -> str:
        return job_workflow.effective_status(obj)


class InvitationCandidateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    location = LocationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = CandidateProfile
        fields = ['id', 'full_name', 'headline', 'current_level', 'years_of_experience', 'location']


class EmployerInvitationSerializer(_InvitationSerializer):
    """Thư công ty đã gửi."""

    job = InvitationJobSerializer(read_only=True)
    candidate = InvitationCandidateSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id', 'job', 'candidate', 'sender', 'message', 'status', 'read_at', 'responded_at', 'application_id',
            'created_at',
        ]


class CandidateInvitationSerializer(_InvitationSerializer):
    """Thư ứng viên nhận được; `job` cùng cấu trúc với danh sách việc làm công khai."""

    job = PublicJobListSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'job', 'sender', 'message', 'status', 'read_at', 'responded_at', 'application_id', 'created_at']


class CandidateInvitationQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InvitationStatus.choices, required=False)


class EmployerInvitationQuerySerializer(CandidateInvitationQuerySerializer):
    job_id = serializers.UUIDField(required=False, help_text='Chỉ thư của tin này')
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tìm theo tên ứng viên')


class InvitationSummarySerializer(serializers.Serializer):
    unread = serializers.IntegerField(help_text='Số thư đang chờ phản hồi mà ứng viên chưa mở')
