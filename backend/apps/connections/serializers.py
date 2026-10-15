from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.accounts.models import User, UserRole
from apps.jobs.models import Job
from common.utils import absolute_media_url

from .models import Connection
from .services import MESSAGE_MAX_LENGTH


def _related(user, name):
    """Hồ sơ theo vai trò qua quan hệ ngược one-to-one (None nếu chưa có)."""
    try:
        return getattr(user, name)
    except ObjectDoesNotExist:
        return None


class ParticipantCompanySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    logo_url = serializers.CharField(allow_null=True)


class ParticipantSerializer(serializers.Serializer):
    """Tài khoản bên kia của lời mời / hội thoại. Không gồm email, số điện thoại."""

    id = serializers.UUIDField()
    full_name = serializers.SerializerMethodField()
    role = serializers.CharField()
    headline = serializers.SerializerMethodField(help_text='Ứng viên: tiêu đề hồ sơ; nhà tuyển dụng: chức danh')
    candidate_id = serializers.SerializerMethodField(help_text='Id hồ sơ ứng viên (chỉ có với ứng viên)')
    company = serializers.SerializerMethodField(help_text='Công ty của nhà tuyển dụng (ứng viên: null)')

    def get_full_name(self, user) -> str:
        return user.get_full_name()

    def get_headline(self, user) -> str:
        if user.role == UserRole.CANDIDATE:
            return getattr(_related(user, 'candidate_profile'), 'headline', '')
        return getattr(_related(user, 'recruiter'), 'position', '')

    def get_candidate_id(self, user) -> str | None:
        profile = _related(user, 'candidate_profile') if user.role == UserRole.CANDIDATE else None
        return str(profile.pk) if profile else None

    @extend_schema_field(ParticipantCompanySerializer(allow_null=True))
    def get_company(self, user):
        recruiter = _related(user, 'recruiter') if user.role == UserRole.EMPLOYER else None
        if recruiter is None:
            return None
        company = recruiter.company
        return {
            'id': str(company.pk),
            'name': company.name,
            'logo_url': absolute_media_url(self.context.get('request'), company.logo),
        }


class ConnectionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title']


class ConnectionSerializer(serializers.ModelSerializer):
    """Lời mời / quan hệ bạn bè nhìn từ phía người đang đăng nhập."""

    direction = serializers.SerializerMethodField(help_text='sent: mình gửi; received: mình nhận')
    user = serializers.SerializerMethodField(help_text='Tài khoản bên kia')
    job = ConnectionJobSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Connection
        fields = ['id', 'status', 'direction', 'user', 'message', 'job', 'created_at', 'responded_at']

    def _me(self):
        return self.context['request'].user

    def get_direction(self, obj) -> str:
        return 'sent' if obj.requester_id == self._me().pk else 'received'

    @extend_schema_field(ParticipantSerializer)
    def get_user(self, obj):
        return ParticipantSerializer(obj.other(self._me()), context=self.context).data


class ConnectionRequestSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='addressee',
        queryset=User.objects.filter(role=UserRole.CANDIDATE, is_active=True, deleted_at__isnull=True),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Không tìm thấy ứng viên.'},
        help_text='Id tài khoản ứng viên (candidate.user_id trong danh sách ứng viên phù hợp)',
    )
    job_id = serializers.UUIDField(required=False, allow_null=True, help_text='Tin tuyển dụng liên quan (tùy chọn)')
    message = serializers.CharField(required=False, allow_blank=True, max_length=MESSAGE_MAX_LENGTH, default='')

    def validate(self, attrs):
        job_id = attrs.pop('job_id', None)
        attrs['job'] = None
        if job_id:
            attrs['job'] = Job.objects.filter(pk=job_id, company=self.context['company']).first()
            if attrs['job'] is None:
                raise serializers.ValidationError({'job_id': 'Tin tuyển dụng không tồn tại.'})
        return attrs
