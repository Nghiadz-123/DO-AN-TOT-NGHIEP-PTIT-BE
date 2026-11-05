"""API hồ sơ ứng tuyển.

- EmployerApplicationViewSet    nhà tuyển dụng xử lý hồ sơ nộp vào các tin của công ty
- EmployerDashboardView         trang tổng quan của nhà tuyển dụng
- CandidateApplicationViewSet   ứng viên nộp, theo dõi, rút hồ sơ
"""
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidates.permissions import CandidateAccessMixin
from apps.employers.permissions import EmployerAccessMixin
from common.views import DOWNLOAD_PARAMETER, FILE_RESPONSE, file_response, validated_body

from . import selectors, services
from .filters import CandidateApplicationFilter, EmployerApplicationFilter
from .models import Application
from .serializers import (
    ApplicationRatingSerializer,
    ApplicationStatusChangeSerializer,
    CandidateApplicationDetailSerializer,
    CandidateApplicationListSerializer,
    CandidateApplySerializer,
    CandidateWithdrawSerializer,
    EmployerApplicationDetailSerializer,
    EmployerApplicationListSerializer,
    EmployerDashboardSerializer,
)

TAG = ['Employer - Ứng viên']
CANDIDATE_TAG = ['Candidate - Ứng tuyển']


class EmployerApplicationViewSet(
    EmployerAccessMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Hồ sơ nộp vào các tin của công ty. Hồ sơ của công ty khác trả về 404."""

    filterset_class = EmployerApplicationFilter
    ordering_fields = ['applied_at', 'status_changed_at', 'recruiter_rating']
    ordering = ['-applied_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Application.objects.none()
        if self.action == 'list':
            return selectors.employer_applications(self.company)
        return selectors.employer_application_detail_queryset(self.company)

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve
        return EmployerApplicationListSerializer if self.action == 'list' else EmployerApplicationDetailSerializer

    # GET /api/v1/employer/applications/?job=&status=applied,screening&q=&ordering=&page=
    @extend_schema(tags=TAG, summary='Danh sách hồ sơ ứng tuyển (lọc theo tin, trạng thái, từ khóa)',
                   responses=EmployerApplicationListSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/employer/applications/{id}/
    @extend_schema(tags=TAG, summary='Chi tiết hồ sơ: ứng viên, CV, thư giới thiệu, lịch sử trạng thái',
                   responses=EmployerApplicationDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # PATCH /api/v1/employer/applications/{id}/
    @extend_schema(tags=TAG, summary='Đánh giá hồ sơ (1-5 sao, null để bỏ)',
                   request=ApplicationRatingSerializer, responses=EmployerApplicationDetailSerializer)
    def partial_update(self, request, pk=None):
        body = validated_body(request, ApplicationRatingSerializer)
        services.rate_application(self.get_object(), rating=body['recruiter_rating'])
        return Response(self._detail_data(pk))

    # POST /api/v1/employer/applications/{id}/status/
    @extend_schema(tags=TAG, summary='Chuyển trạng thái hồ sơ theo pipeline',
                   request=ApplicationStatusChangeSerializer, responses=EmployerApplicationDetailSerializer)
    @action(detail=True, methods=['post'], url_path='status')
    def change_status(self, request, pk=None):
        body = validated_body(request, ApplicationStatusChangeSerializer)
        services.change_status(
            self.get_object(),
            to_status=body['status'],
            by=request.user,
            note=body['note'],
            rejection_reason=body['rejection_reason'],
        )
        return Response(self._detail_data(pk))

    # GET /api/v1/employer/applications/{id}/cv/?download=1
    @extend_schema(tags=TAG, summary='Xem / tải file CV ứng viên đã nộp', parameters=[DOWNLOAD_PARAMETER],
                   responses=FILE_RESPONSE)
    @action(detail=True, methods=['get'], url_path='cv')
    def cv(self, request, pk=None):
        cv = self.get_object().cv
        return file_response(request, cv.file, filename=cv.original_filename, content_type=cv.mime_type,
                             not_found_message='Không tìm thấy file CV.')

    def _detail_data(self, pk) -> dict:
        """Đọc lại hồ sơ sau khi sửa, trả dữ liệu dạng EmployerApplicationDetailSerializer."""
        fresh = self.get_queryset().get(pk=pk)
        return EmployerApplicationDetailSerializer(fresh, context=self.get_serializer_context()).data


class EmployerDashboardView(EmployerAccessMixin, APIView):
    # GET /api/v1/employer/dashboard/
    @extend_schema(tags=['Employer - Tổng quan'], summary='Thống kê tin & hồ sơ, hồ sơ mới nhận',
                   responses=EmployerDashboardSerializer)
    def get(self, request):
        data = selectors.employer_dashboard(self.company)
        return Response(EmployerDashboardSerializer(data, context={'request': request}).data)


class CandidateApplicationViewSet(
    CandidateAccessMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Hồ sơ ứng tuyển của ứng viên đang đăng nhập. Hồ sơ của người khác trả về 404."""

    filterset_class = CandidateApplicationFilter
    ordering_fields = ['applied_at', 'status_changed_at']
    ordering = ['-applied_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Application.objects.none()
        if self.action == 'list':
            return selectors.candidate_applications(self.candidate)
        return selectors.candidate_application_detail_queryset(self.candidate)

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve (và form của create trên Swagger)
        if self.action == 'list':
            return CandidateApplicationListSerializer
        if self.action == 'create':
            return CandidateApplySerializer
        return CandidateApplicationDetailSerializer

    # GET /api/v1/candidate/applications/?status=applied,screening&q=&ordering=&page=
    @extend_schema(tags=CANDIDATE_TAG, summary='Hồ sơ tôi đã nộp (lọc theo trạng thái, từ khóa)',
                   responses=CandidateApplicationListSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/candidate/applications/{id}/
    @extend_schema(tags=CANDIDATE_TAG, summary='Chi tiết hồ sơ đã nộp: tin, CV, thư giới thiệu, lịch sử',
                   responses=CandidateApplicationDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # POST /api/v1/candidate/applications/
    @extend_schema(tags=CANDIDATE_TAG, summary='Ứng tuyển vào một tin bằng CV đã tải lên',
                   request=CandidateApplySerializer, responses={201: CandidateApplicationDetailSerializer})
    def create(self, request, *args, **kwargs):
        body = validated_body(request, CandidateApplySerializer, context={'candidate': self.candidate})
        application = services.submit_application(
            candidate=self.candidate, job=body['job'], cv=body['cv'], cover_letter=body['cover_letter']
        )
        return Response(self._detail_data(application.pk), status=status.HTTP_201_CREATED)

    # POST /api/v1/candidate/applications/{id}/withdraw/
    @extend_schema(tags=CANDIDATE_TAG, summary='Rút hồ sơ (khi chưa có kết quả)',
                   request=CandidateWithdrawSerializer, responses=CandidateApplicationDetailSerializer)
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        body = validated_body(request, CandidateWithdrawSerializer)
        services.withdraw_application(self.get_object(), by=request.user, reason=body['reason'])
        return Response(self._detail_data(pk))

    def _detail_data(self, pk) -> dict:
        """Đọc lại hồ sơ sau khi sửa, trả dữ liệu dạng CandidateApplicationDetailSerializer."""
        fresh = selectors.candidate_application_detail_queryset(self.candidate).get(pk=pk)
        return CandidateApplicationDetailSerializer(fresh, context=self.get_serializer_context()).data
