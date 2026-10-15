from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.candidates.models import CandidateProfile
from apps.catalog.serializers import LocationSerializer
from apps.cvs.models import CV

from .matching import WEIGHTS


class TalentCandidateSerializer(serializers.ModelSerializer):
    """Hồ sơ ứng viên trong danh sách gợi ý. Không gồm email / số điện thoại: nhà tuyển dụng liên hệ qua
    kết bạn và nhắn tin (hoặc thông tin trên CV)."""

    user_id = serializers.UUIDField(read_only=True, help_text='Id tài khoản, dùng để gửi lời mời kết bạn')
    full_name = serializers.CharField(source='user.full_name')
    location = LocationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user_id', 'full_name', 'headline', 'summary', 'years_of_experience', 'current_level', 'location',
            'desired_position', 'is_open_to_work',
        ]


class TalentCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['id', 'title', 'original_filename', 'mime_type', 'file_size', 'parse_status', 'updated_at']


class MatchBreakdownSerializer(serializers.Serializer):
    skills = serializers.IntegerField(help_text=f'Tối đa {WEIGHTS["skills"]}')
    experience = serializers.IntegerField(help_text=f'Tối đa {WEIGHTS["experience"]}')
    level = serializers.IntegerField(help_text=f'Tối đa {WEIGHTS["level"]}')
    location = serializers.IntegerField(help_text=f'Tối đa {WEIGHTS["location"]}')


class TalentConnectionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()
    direction = serializers.CharField(help_text='sent: nhà tuyển dụng đang xem đã gửi; received: ngược lại')


class TalentMatchSerializer(serializers.Serializer):
    """Một ứng viên phù hợp (selectors.TalentMatch)."""

    candidate = TalentCandidateSerializer()
    cv = TalentCVSerializer(help_text='CV mặc định của ứng viên, dùng để so khớp')
    score = serializers.IntegerField(source='match.score', help_text='Điểm phù hợp 0-100')
    breakdown = MatchBreakdownSerializer(source='match.breakdown')
    matched_skills = serializers.ListField(source='match.matched_skills', child=serializers.CharField())
    missing_skills = serializers.ListField(source='match.missing_skills', child=serializers.CharField())
    reasons = serializers.ListField(source='match.reasons', child=serializers.CharField())
    application_id = serializers.UUIDField(allow_null=True, help_text='Hồ sơ ứng viên đã nộp vào tin này (nếu có)')
    connection = serializers.SerializerMethodField(help_text='Lời mời / kết bạn với ứng viên (null: chưa có)')

    @extend_schema_field(TalentConnectionSerializer(allow_null=True))
    def get_connection(self, obj):
        connection = obj.connection
        if connection is None:
            return None
        me = self.context['request'].user
        return {
            'id': str(connection.pk),
            'status': connection.status,
            'direction': 'sent' if connection.requester_id == me.pk else 'received',
        }


class TalentQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tìm theo tên, tiêu đề hồ sơ')
    min_score = serializers.IntegerField(required=False, min_value=0, max_value=100, default=0)
    hide_applied = serializers.BooleanField(required=False, default=False,
                                            help_text='Ẩn ứng viên đã ứng tuyển vào tin này')
