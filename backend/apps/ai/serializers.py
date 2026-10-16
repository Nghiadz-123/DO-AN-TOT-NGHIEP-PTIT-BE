from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.jobs.serializers import PublicJobListSerializer

from .models import CVAnalysis
from .prompts.cv_analysis import SCORE_CRITERIA
from .services.job_recommendation import DEFAULT_LIMIT, MAX_LIMIT


# ------------------------------------------------------------------------------------------ phân tích CV
class ScoreCriterionSerializer(serializers.Serializer):
    key = serializers.ChoiceField(choices=list(SCORE_CRITERIA))
    label = serializers.CharField()
    score = serializers.IntegerField()
    max = serializers.IntegerField(help_text='Điểm tối đa của tiêu chí')


class CVScoreSerializer(serializers.Serializer):
    total = serializers.IntegerField(help_text='Điểm CV 0-100 (tổng các tiêu chí)')
    breakdown = ScoreCriterionSerializer(many=True)
    strengths = serializers.ListField(child=serializers.CharField())
    weaknesses = serializers.ListField(child=serializers.CharField())
    scored_at = serializers.DateTimeField()


class CVSuggestionItemSerializer(serializers.Serializer):
    section = serializers.CharField(help_text='Mục của CV, vd. "Kinh nghiệm làm việc"')
    issue = serializers.CharField()
    suggestion = serializers.CharField()
    example_before = serializers.CharField(allow_null=True)
    example_after = serializers.CharField(allow_null=True)
    priority = serializers.ChoiceField(choices=['high', 'medium', 'low'])
    job_ids = serializers.ListField(child=serializers.UUIDField(), help_text='Tin tham chiếu là căn cứ của gợi ý')


class ReferenceJobSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    company = serializers.CharField()
    score = serializers.IntegerField(
        required=False, allow_null=True, help_text='Điểm phù hợp với CV lúc gợi ý (như trang Việc làm phù hợp)'
    )
    is_target = serializers.BooleanField(help_text='Tin mục tiêu ứng viên chọn')


class CVSuggestionsSerializer(serializers.Serializer):
    items = CVSuggestionItemSerializer(many=True)
    missing_keywords = serializers.ListField(child=serializers.CharField())
    reference_jobs = ReferenceJobSerializer(many=True)
    target_job_id = serializers.UUIDField(allow_null=True)
    suggested_at = serializers.DateTimeField()


class CVProfileSerializer(serializers.Serializer):
    """Chỉ dùng cho tài liệu OpenAPI: hồ sơ cấu trúc theo prompts.cv_analysis.CV_SCHEMA."""

    full_name = serializers.CharField()
    email = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    location = serializers.CharField(allow_null=True)
    title = serializers.CharField()
    summary = serializers.CharField()
    years_of_experience = serializers.FloatField(allow_null=True)
    skills = serializers.ListField(child=serializers.CharField())
    experiences = serializers.ListField(child=serializers.DictField())
    educations = serializers.ListField(child=serializers.DictField())
    projects = serializers.ListField(child=serializers.DictField())
    certifications = serializers.ListField(child=serializers.CharField())
    languages = serializers.ListField(child=serializers.CharField())


@extend_schema_field(CVProfileSerializer(allow_null=True))
class CVProfileField(serializers.JSONField):
    """Trả nguyên JSON đã lưu nhưng mô tả cấu trúc trong Swagger."""


class CVAnalysisSerializer(serializers.ModelSerializer):
    """Kết quả AI mới nhất của một CV. Chức năng chưa chạy thì trường tương ứng là null."""

    cv_id = serializers.UUIDField(read_only=True)
    profile = CVProfileField(read_only=True, help_text='Thông tin AI bóc tách từ CV')
    score = serializers.SerializerMethodField()
    suggestions = serializers.SerializerMethodField()

    class Meta:
        model = CVAnalysis
        fields = ['cv_id', 'profile', 'score', 'suggestions', 'updated_at']

    @extend_schema_field(CVScoreSerializer(allow_null=True))
    def get_score(self, obj):
        if obj.score_total is None:
            return None
        return CVScoreSerializer({
            'total': obj.score_total,
            'breakdown': [
                {'key': key, 'label': label, 'score': obj.score_breakdown.get(key, 0), 'max': maximum}
                for key, (label, maximum, _) in SCORE_CRITERIA.items()
            ],
            'strengths': obj.strengths,
            'weaknesses': obj.weaknesses,
            'scored_at': obj.scored_at,
        }).data

    @extend_schema_field(CVSuggestionsSerializer(allow_null=True))
    def get_suggestions(self, obj):
        if obj.suggested_at is None:
            return None
        return CVSuggestionsSerializer({
            'items': obj.suggestions,
            'missing_keywords': obj.missing_keywords,
            'reference_jobs': obj.reference_jobs,
            'target_job_id': obj.target_job_id,
            'suggested_at': obj.suggested_at,
        }).data


class CVSuggestRequestSerializer(serializers.Serializer):
    job_id = serializers.UUIDField(
        required=False, allow_null=True, help_text='Tin tuyển dụng mục tiêu (không bắt buộc)'
    )


# ------------------------------------------------------------------------------------------ gợi ý việc làm
class AIEvaluationSerializer(serializers.Serializer):
    score = serializers.IntegerField(help_text='Điểm AI đánh giá 0-100')
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    reason = serializers.CharField()
    evaluated_at = serializers.DateTimeField(source='updated_at')


class JobRecommendationSerializer(serializers.Serializer):
    """Một tin được gợi ý (services.job_recommendation.JobRecommendation)."""

    job = PublicJobListSerializer()
    score = serializers.IntegerField(help_text='Điểm phù hợp 0-100')
    similarity = serializers.FloatField(help_text='Độ tương đồng nội dung CV - tin (cosine embedding), 0-1')
    skill_overlap = serializers.FloatField(help_text='Tỉ lệ kỹ năng bắt buộc của tin có trong CV, 0-1')
    matched_skills = serializers.ListField(child=serializers.CharField(), help_text='Kỹ năng của tin CV đã có')
    missing_skills = serializers.ListField(child=serializers.CharField())
    reasons = serializers.ListField(child=serializers.CharField())
    ai_evaluation = AIEvaluationSerializer(
        source='evaluation', allow_null=True, help_text='AI đánh giá chi tiết (null: chưa đánh giá)'
    )


class RecommendationQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=MAX_LIMIT, default=DEFAULT_LIMIT)
