"""API tin tuyển dụng.

- EmployerJobViewSet     nhà tuyển dụng quản lý tin của công ty (tạo, sửa, đăng, tạm dừng, đóng, xóa)
- PublicJobViewSet       việc làm công khai cho ứng viên / khách (chỉ đọc)
- PublicCompanyViewSet   danh bạ công ty công khai (chỉ đọc)
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.employers.permissions import EmployerAccessMixin
from common.views import validated_body

from . import selectors, services
from .filters import EmployerJobFilter, PublicCompanyFilter, PublicJobFilter
from .models import Job, JobStatus
from .serializers import (
    EmployerJobDetailSerializer,
    EmployerJobListSerializer,
    EmployerJobWriteSerializer,
    PublicCompanyDetailSerializer,
    PublicCompanyListSerializer,
    PublicJobDetailSerializer,
    PublicJobListSerializer,
)

EMPLOYER_TAG = ['Employer - Tin tuyển dụng']
JOB_TAG = ['Jobs (công khai)']
COMPANY_TAG = ['Companies (công khai)']


class EmployerJobViewSet(EmployerAccessMixin, viewsets.ModelViewSet):
    """Tin tuyển dụng của công ty mà nhà tuyển dụng đang đăng nhập thuộc về. Tin của công ty khác trả về 404."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filterset_class = EmployerJobFilter
    ordering_fields = ['created_at', 'published_at', 'deadline', 'title', 'applicant_count']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Job.objects.none()
        return selectors.employer_jobs(self.company)

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve (và form trên Swagger)
        if self.action == 'list':
            return EmployerJobListSerializer
        if self.action in ('create', 'partial_update'):
            return EmployerJobWriteSerializer
        return EmployerJobDetailSerializer

    # GET /api/v1/employer/jobs/?q=&status=&job_type=&level=&work_mode=&location=&industry=&ordering=&page=
    @extend_schema(tags=EMPLOYER_TAG, summary='Danh sách tin của công ty', responses=EmployerJobListSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/employer/jobs/{id}/
    @extend_schema(tags=EMPLOYER_TAG, summary='Chi tiết tin', responses=EmployerJobDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # POST /api/v1/employer/jobs/
    @extend_schema(tags=EMPLOYER_TAG, summary='Tạo tin (lưu nháp hoặc đăng ngay)',
                   request=EmployerJobWriteSerializer, responses={201: EmployerJobDetailSerializer})
    def create(self, request, *args, **kwargs):
        body = validated_body(request, EmployerJobWriteSerializer)
        skills = body.pop('skills', None)
        publish = body.pop('status', JobStatus.DRAFT) == JobStatus.PUBLISHED
        job = services.create_job(
            company=self.company, created_by=request.user, data=body, skills=skills, publish=publish
        )
        return Response(self._detail_data(job), status=status.HTTP_201_CREATED)

    # PATCH /api/v1/employer/jobs/{id}/
    @extend_schema(tags=EMPLOYER_TAG, summary='Sửa nội dung tin',
                   request=EmployerJobWriteSerializer, responses=EmployerJobDetailSerializer)
    def partial_update(self, request, *args, **kwargs):
        job = self.get_object()
        body = validated_body(request, EmployerJobWriteSerializer, instance=job, partial=True)
        skills = body.pop('skills', None)
        services.update_job(job, data=body, skills=skills)
        return Response(self._detail_data(job))

    # DELETE /api/v1/employer/jobs/{id}/
    @extend_schema(tags=EMPLOYER_TAG, summary='Xóa tin (chỉ khi chưa có hồ sơ ứng tuyển)', responses={204: None})
    def destroy(self, request, *args, **kwargs):
        services.delete_job(self.get_object(), by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # POST /api/v1/employer/jobs/{id}/publish/
    @extend_schema(tags=EMPLOYER_TAG, summary='Đăng / tiếp tục tuyển / mở lại tin', request=None,
                   responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        job = services.publish_job(self.get_object(), by=request.user)
        return Response(self._detail_data(job))

    # POST /api/v1/employer/jobs/{id}/pause/
    @extend_schema(tags=EMPLOYER_TAG, summary='Tạm dừng nhận hồ sơ', request=None,
                   responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        job = services.pause_job(self.get_object(), by=request.user)
        return Response(self._detail_data(job))

    # POST /api/v1/employer/jobs/{id}/close/
    @extend_schema(tags=EMPLOYER_TAG, summary='Đóng tin', request=None, responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        job = services.close_job(self.get_object(), by=request.user)
        return Response(self._detail_data(job))

    def _detail_data(self, job) -> dict:
        """Đọc lại tin (để có số hồ sơ & kỹ năng mới nhất), trả dữ liệu dạng EmployerJobDetailSerializer."""
        fresh = self.get_queryset().get(pk=job.pk)
        return EmployerJobDetailSerializer(fresh, context=self.get_serializer_context()).data


class PublicJobViewSet(viewsets.ReadOnlyModelViewSet):
    """Chỉ đọc. Phục vụ trang việc làm của frontend và để nhà tuyển dụng xem trước tin đã đăng."""

    permission_classes = [AllowAny]
    authentication_classes = []
    filterset_class = PublicJobFilter
    ordering_fields = ['published_at', 'salary_max', 'deadline']
    ordering = ['-published_at']

    def get_queryset(self):
        if self.action == 'list':
            return selectors.public_jobs()
        return selectors.public_job_detail_queryset()

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve
        return PublicJobListSerializer if self.action == 'list' else PublicJobDetailSerializer

    # GET /api/v1/jobs/?q=&company=&job_type=&level=&work_mode=&location=&industry=&posted_within=&ordering=&page=
    @extend_schema(tags=JOB_TAG, summary='Tin đang tuyển', responses=PublicJobListSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/jobs/{id}/
    @extend_schema(tags=JOB_TAG, summary='Chi tiết tin (không gồm bản nháp)', responses=PublicJobDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        services.record_view(job)
        return Response(PublicJobDetailSerializer(job, context=self.get_serializer_context()).data)


class PublicCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """Danh bạ công ty cho ứng viên. Tin đang tuyển của một công ty lấy qua GET /api/v1/jobs/?company=<id>."""

    permission_classes = [AllowAny]
    authentication_classes = []
    filterset_class = PublicCompanyFilter
    ordering_fields = ['name', 'open_job_count']
    ordering = ['-open_job_count', 'name']

    def get_queryset(self):
        return selectors.public_companies()

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve
        return PublicCompanyListSerializer if self.action == 'list' else PublicCompanyDetailSerializer

    # GET /api/v1/companies/?q=&industry=&location=&ordering=&page=
    @extend_schema(tags=COMPANY_TAG, summary='Danh bạ công ty: tìm theo tên, lọc ngành nghề / tỉnh',
                   responses=PublicCompanyListSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/companies/{id}/
    @extend_schema(tags=COMPANY_TAG, summary='Hồ sơ công ty', responses=PublicCompanyDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
