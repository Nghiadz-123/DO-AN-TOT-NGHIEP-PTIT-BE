from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidates.permissions import CandidateAccessMixin
from apps.employers.permissions import EmployerAccessMixin

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


@extend_schema_view(
    list=extend_schema(tags=TAG, summary='Danh sách hồ sơ ứng tuyển (lọc theo tin, trạng thái, từ khóa)'),
    retrieve=extend_schema(tags=TAG, summary='Chi tiết hồ sơ: ứng viên, CV, thư giới thiệu, lịch sử trạng thái'),
)
class EmployerApplicationViewSet(
    EmployerAccessMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    filterset_class = EmployerApplicationFilter
    ordering_fields = ['applied_at', 'status_changed_at', 'recruiter_rating']
    ordering = ['-applied_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Application.objects.none()
        if self.action == 'list':
            return selectors.employer_applications(self.company)
        return selectors.employer_application_detail_queryset(self.company)

    def get_serializer_class(self):
        return EmployerApplicationListSerializer if self.action == 'list' else EmployerApplicationDetailSerializer

    @extend_schema(tags=TAG, summary='Đánh giá hồ sơ (1-5 sao, null để bỏ)',
                   request=ApplicationRatingSerializer, responses=EmployerApplicationDetailSerializer)
    def partial_update(self, request, pk=None):
        serializer = ApplicationRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.rate_application(self.get_object(), rating=serializer.validated_data['recruiter_rating'])
        return Response(self._detail(pk))

    @extend_schema(tags=TAG, summary='Chuyển trạng thái hồ sơ theo pipeline',
                   request=ApplicationStatusChangeSerializer, responses=EmployerApplicationDetailSerializer)
    @action(detail=True, methods=['post'], url_path='status')
    def change_status(self, request, pk=None):
        serializer = ApplicationStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        services.change_status(
            self.get_object(),
            to_status=data['status'],
            by=request.user,
            note=data['note'],
            rejection_reason=data['rejection_reason'],
        )
        return Response(self._detail(pk))

    @extend_schema(
        tags=TAG,
        summary='Xem / tải file CV ứng viên đã nộp',
        parameters=[OpenApiParameter('download', OpenApiTypes.BOOL, description='1: tải về thay vì xem trực tiếp')],
        responses={(200, 'application/octet-stream'): OpenApiResponse(OpenApiTypes.BINARY)},
    )
    @action(detail=True, methods=['get'], url_path='cv')
    def cv(self, request, pk=None):
        cv = self.get_object().cv
        if not cv.file or not cv.file.storage.exists(cv.file.name):
            raise NotFound('Không tìm thấy file CV.')
        return FileResponse(
            cv.file.open('rb'),
            as_attachment=request.query_params.get('download') in ('1', 'true'),
            filename=cv.original_filename,
            content_type=cv.mime_type,
        )

    def _detail(self, pk):
        fresh = self.get_queryset().get(pk=pk)
        return EmployerApplicationDetailSerializer(fresh, context=self.get_serializer_context()).data


class EmployerDashboardView(EmployerAccessMixin, APIView):
    @extend_schema(tags=['Employer - Tổng quan'], summary='Thống kê tin & hồ sơ, hồ sơ mới nhận',
                   responses=EmployerDashboardSerializer)
    def get(self, request):
        data = selectors.employer_dashboard(self.company)
        return Response(EmployerDashboardSerializer(data, context={'request': request}).data)


@extend_schema_view(
    list=extend_schema(tags=CANDIDATE_TAG, summary='Hồ sơ tôi đã nộp (lọc theo trạng thái, từ khóa)'),
    retrieve=extend_schema(tags=CANDIDATE_TAG, summary='Chi tiết hồ sơ đã nộp: tin, CV, thư giới thiệu, lịch sử'),
    create=extend_schema(
        tags=CANDIDATE_TAG,
        summary='Ứng tuyển vào một tin bằng CV đã tải lên',
        request=CandidateApplySerializer,
        responses={201: CandidateApplicationDetailSerializer},
    ),
)
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

    def get_serializer_class(self):
        if self.action == 'list':
            return CandidateApplicationListSerializer
        if self.action == 'create':
            return CandidateApplySerializer
        return CandidateApplicationDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = CandidateApplySerializer(
            data=request.data, context={**self.get_serializer_context(), 'candidate': self.candidate}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        application = services.submit_application(
            candidate=self.candidate, job=data['job'], cv=data['cv'], cover_letter=data['cover_letter']
        )
        return Response(self._detail(application.pk), status=status.HTTP_201_CREATED)

    @extend_schema(tags=CANDIDATE_TAG, summary='Rút hồ sơ (khi chưa có kết quả)',
                   request=CandidateWithdrawSerializer, responses=CandidateApplicationDetailSerializer)
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        serializer = CandidateWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.withdraw_application(self.get_object(), by=request.user, reason=serializer.validated_data['reason'])
        return Response(self._detail(pk))

    def _detail(self, pk):
        fresh = selectors.candidate_application_detail_queryset(self.candidate).get(pk=pk)
        return CandidateApplicationDetailSerializer(fresh, context=self.get_serializer_context()).data
