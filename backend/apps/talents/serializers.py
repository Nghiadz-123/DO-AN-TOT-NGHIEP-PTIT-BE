from rest_framework import serializers

from apps.candidates.models import CandidateProfile
from apps.catalog.choices import JobLevel
from apps.catalog.serializers import LocationSerializer
from apps.cvs.models import CV
from apps.invitations.models import Invitation
from apps.invitations.serializers import InvitationJobSerializer

from .matching import WEIGHTS


class TalentCandidateSerializer(serializers.ModelSerializer):
    """Hồ sơ ứng viên nhà tuyển dụng tìm thấy. Không gồm email / số điện thoại: nhà tuyển dụng liên hệ qua
    thư mời ứng tuyển (hoặc thông tin trên CV)."""

    full_name = serializers.CharField(source='user.full_name')
    location = LocationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'full_name', 'headline', 'summary', 'years_of_experience', 'current_level', 'location',
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


class TalentInvitationSerializer(serializers.ModelSerializer):
    job = InvitationJobSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'job', 'status', 'read_at', 'created_at']


class TalentProfileSerializer(serializers.Serializer):
    """Một ứng viên công khai CV (selectors.TalentProfile)."""

    candidate = TalentCandidateSerializer()
    cv = TalentCVSerializer(help_text='CV chính ứng viên công khai')
    invitation = TalentInvitationSerializer(allow_null=True, help_text='Thư mời gần nhất công ty đã gửi (null: chưa mời)')


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
    invitation = TalentInvitationSerializer(allow_null=True, help_text='Thư mời ứng tuyển tin này (null: chưa mời)')


class TalentPoolQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False, allow_blank=True, default='',
        help_text='Tìm theo tên, tiêu đề hồ sơ, vị trí mong muốn, giới thiệu hoặc nội dung CV',
    )
    location_id = serializers.IntegerField(required=False, help_text='Tỉnh/thành của ứng viên')
    level = serializers.ChoiceField(choices=JobLevel.choices, required=False, help_text='Cấp bậc hiện tại')


class TalentQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text='Tìm theo tên, tiêu đề hồ sơ')
    min_score = serializers.IntegerField(required=False, min_value=0, max_value=100, default=0)
    hide_applied = serializers.BooleanField(required=False, default=False,
                                            help_text='Ẩn ứng viên đã ứng tuyển vào tin này')
