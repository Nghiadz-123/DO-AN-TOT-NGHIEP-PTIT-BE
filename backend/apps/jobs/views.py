from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.employers.permissions import EmployerAccessMixin

from . import selectors, services
from .filters import EmployerJobFilter, PublicJobFilter
from .models import Job, JobStatus
from .serializers import (
    EmployerJobDetailSerializer,
    EmployerJobListSerializer,
    EmployerJobWriteSerializer,
    PublicJobDetailSerializer,
    PublicJobListSerializer,
)

EMPLOYER_TAG = ['Employer - Tin tuyển dụng']


@extend_schema_view(
    list=extend_schema(tags=EMPLOYER_TAG, summary='Danh sách tin của công ty'),
    retrieve=extend_schema(tags=EMPLOYER_TAG, summary='Chi tiết tin'),
    create=extend_schema(
        tags=EMPLOYER_TAG, summary='Tạo tin (lưu nháp hoặc đăng ngay)',
        request=EmployerJobWriteSerializer, responses={201: EmployerJobDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=EMPLOYER_TAG, summary='Sửa nội dung tin',
        request=EmployerJobWriteSerializer, responses=EmployerJobDetailSerializer,
    ),
    destroy=extend_schema(tags=EMPLOYER_TAG, summary='Xóa tin (chỉ khi chưa có hồ sơ ứng tuyển)'),
)
class EmployerJobViewSet(EmployerAccessMixin, viewsets.ModelViewSet):
    """Tin tuyển dụng của công ty mà nhà tuyển dụng đang đăng nhập thuộc về."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filterset_class = EmployerJobFilter
    ordering_fields = ['created_at', 'published_at', 'deadline', 'title', 'applicant_count']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Job.objects.none()
        return selectors.employer_jobs(self.company)

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployerJobListSerializer
        if self.action in ('create', 'partial_update'):
            return EmployerJobWriteSerializer
        return EmployerJobDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        skills = data.pop('skills', None)
        publish = data.pop('status', JobStatus.DRAFT) == JobStatus.PUBLISHED
        job = services.create_job(
            company=self.company, created_by=request.user, data=data, skills=skills, publish=publish
        )
        return Response(self._detail(job), status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        skills = data.pop('skills', None)
        services.update_job(job, data=data, skills=skills)
        return Response(self._detail(job))

    def destroy(self, request, *args, **kwargs):
        services.delete_job(self.get_object(), by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=EMPLOYER_TAG, summary='Đăng / tiếp tục tuyển / mở lại tin', request=None,
                   responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return Response(self._detail(services.publish_job(self.get_object(), by=request.user)))

    @extend_schema(tags=EMPLOYER_TAG, summary='Tạm dừng nhận hồ sơ', request=None,
                   responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        return Response(self._detail(services.pause_job(self.get_object(), by=request.user)))

    @extend_schema(tags=EMPLOYER_TAG, summary='Đóng tin', request=None, responses=EmployerJobDetailSerializer)
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        return Response(self._detail(services.close_job(self.get_object(), by=request.user)))

    def _detail(self, job):
        fresh = self.get_queryset().get(pk=job.pk)  # đọc lại để có số hồ sơ & kỹ năng mới nhất
        return EmployerJobDetailSerializer(fresh, context=self.get_serializer_context()).data


@extend_schema_view(
    list=extend_schema(tags=['Jobs (công khai)'], summary='Tin đang tuyển'),
    retrieve=extend_schema(tags=['Jobs (công khai)'], summary='Chi tiết tin (không gồm bản nháp)'),
)
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

    def get_serializer_class(self):
        return PublicJobListSerializer if self.action == 'list' else PublicJobDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        services.record_view(job)
        return Response(self.get_serializer(job).data)
