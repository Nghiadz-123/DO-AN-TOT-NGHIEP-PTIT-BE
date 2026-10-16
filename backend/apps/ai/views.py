"""API AI dành cho ứng viên: chấm điểm CV, gợi ý sửa CV, gợi ý việc làm.

Mỗi thao tác gọi Gemini mất vài giây và chạy đồng bộ trong request (chưa có Celery); frontend hiển thị trạng thái
"AI đang phân tích". Kết quả được lưu nên lần mở trang sau đọc lại từ DB, không gọi AI nữa.
"""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.candidates.permissions import CandidateAccessMixin
from apps.cvs import selectors as cv_selectors
from apps.jobs import selectors as job_selectors

from . import selectors
from .models import CVAnalysis
from .serializers import (
    CVAnalysisSerializer,
    CVSuggestRequestSerializer,
    JobRecommendationSerializer,
    RecommendationQuerySerializer,
)
from .services import cv_analysis, cv_suggestion, job_recommendation

TAG = ['Candidate - AI']
AI_ERRORS = {
    409: OpenApiResponse(description='CV chưa đọc được nội dung (code: cv_not_ready)'),
    502: OpenApiResponse(description='AI trả về kết quả không hợp lệ (code: ai_invalid_output)'),
    503: OpenApiResponse(description='AI chưa cấu hình / quá tải / hết lượt dùng (code: ai_not_configured, ai_unavailable)'),
}


class _CandidateCVAIView(CandidateAccessMixin, APIView):
    """Thao tác AI trên một CV của ứng viên đang đăng nhập (CV của người khác trả về 404).
    Giới hạn số lần gọi (throttle `ai`) để không dùng hết quota Gemini."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def get_cv(self):
        cv = cv_selectors.get_candidate_cv(self.candidate, self.kwargs['cv_id'])
        if cv is None:
            raise NotFound('Không tìm thấy CV.')
        return cv


class CVAnalysisListView(CandidateAccessMixin, generics.ListAPIView):
    """Kết quả AI đã lưu của các CV của tôi (tối đa CANDIDATE_MAX_CVS CV nên không phân trang)."""

    serializer_class = CVAnalysisSerializer
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return CVAnalysis.objects.none()
        return selectors.candidate_analyses(self.candidate)

    @extend_schema(tags=TAG, summary='Kết quả AI (điểm, gợi ý, thông tin trích xuất) của các CV của tôi')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CVScoreView(_CandidateCVAIView):
    @extend_schema(
        tags=TAG,
        summary='AI chấm điểm CV (0-100 theo 5 tiêu chí, điểm mạnh / điểm cần cải thiện)',
        description='Đồng thời AI bóc tách thông tin CV (trường `profile`) nếu chưa có. Mất vài giây.',
        request=None,
        responses={200: CVAnalysisSerializer, **AI_ERRORS},
    )
    def post(self, request, cv_id):
        return Response(CVAnalysisSerializer(cv_analysis.score_cv(self.get_cv())).data)


class CVSuggestionView(_CandidateCVAIView):
    @extend_schema(
        tags=TAG,
        summary='AI gợi ý sửa CV (theo tin mục tiêu và các tin đang tuyển gần CV nhất)',
        request=CVSuggestRequestSerializer,
        responses={200: CVAnalysisSerializer, **AI_ERRORS},
    )
    def post(self, request, cv_id):
        serializer = CVSuggestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cv = self.get_cv()
        target_job = None
        job_id = serializer.validated_data.get('job_id')
        if job_id:
            target_job = job_selectors.public_job_detail_queryset().filter(pk=job_id).first()
            if target_job is None:
                raise NotFound('Không tìm thấy tin tuyển dụng.')
        return Response(CVAnalysisSerializer(cv_suggestion.suggest_cv(cv, target_job=target_job)).data)


class RecommendedJobsView(_CandidateCVAIView):
    @extend_schema(
        tags=TAG,
        summary='Việc làm phù hợp với CV (điểm 0-100, kỹ năng đã có / còn thiếu, lý do)',
        description='Lần đầu AI bóc tách CV và tạo vector cho các tin nên mất vài giây; các lần sau dùng lại kết quả.',
        parameters=[RecommendationQuerySerializer],
        responses={200: JobRecommendationSerializer(many=True), **AI_ERRORS},
    )
    def get(self, request, cv_id):
        query = RecommendationQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        items = job_recommendation.recommend_jobs(self.get_cv(), limit=query.validated_data['limit'])
        return Response(JobRecommendationSerializer(items, many=True, context={'request': request}).data)


class JobEvaluationView(_CandidateCVAIView):
    @extend_schema(
        tags=TAG,
        summary='AI đánh giá chi tiết mức độ phù hợp của CV với một tin đang tuyển',
        request=None,
        responses={200: JobRecommendationSerializer, **AI_ERRORS},
    )
    def post(self, request, cv_id, job_id):
        cv = self.get_cv()
        job = job_selectors.public_jobs().filter(pk=job_id).first()
        if job is None:
            raise NotFound('Không tìm thấy tin tuyển dụng đang tuyển.')
        item = job_recommendation.evaluate_job(cv, job)
        return Response(JobRecommendationSerializer(item, context={'request': request}).data)
