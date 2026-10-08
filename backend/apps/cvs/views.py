from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.candidates.permissions import CandidateAccessMixin

from . import selectors, services
from .models import CV
from .serializers import CVDetailSerializer, CVSerializer, CVUpdateSerializer, CVUploadSerializer

TAG = ['Candidate - CV']


@extend_schema_view(
    list=extend_schema(tags=TAG, summary='Danh sách CV của tôi (CV mặc định đứng đầu)'),
    retrieve=extend_schema(tags=TAG, summary='Chi tiết CV: trạng thái và kết quả bóc tách'),
    create=extend_schema(
        tags=TAG,
        summary='Tải lên CV (PDF/DOCX, tối đa 5 MB)',
        description='multipart/form-data. CV được bóc tách văn bản ngay sau khi lưu: theo dõi `parse_status` '
        '(pending → processing → completed | failed) bằng API chi tiết.',
        request={'multipart/form-data': CVUploadSerializer},
        responses={201: CVDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=TAG, summary='Đổi tên CV', request=CVUpdateSerializer, responses=CVDetailSerializer
    ),
    destroy=extend_schema(tags=TAG, summary='Xóa CV (CV đã dùng ứng tuyển vẫn được giữ cho nhà tuyển dụng)'),
)
class CandidateCVViewSet(CandidateAccessMixin, viewsets.ModelViewSet):
    """CV của ứng viên đang đăng nhập. CV của người khác trả về 404."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = None  # tối đa settings.CANDIDATE_MAX_CVS bản ghi nên trả về toàn bộ
    ordering_fields = ['created_at', 'title']
    ordering = ['-is_default', '-created_at']
    throttle_scope = 'cv_upload'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return CV.objects.none()
        return selectors.candidate_cvs(self.candidate)

    def get_serializer_class(self):
        if self.action == 'list':
            return CVSerializer
        if self.action == 'create':
            return CVUploadSerializer
        if self.action == 'partial_update':
            return CVUpdateSerializer
        return CVDetailSerializer

    def get_throttles(self):
        # Giới hạn số lần upload (mỗi lần upload tốn CPU để bóc tách); các thao tác khác không giới hạn
        return [ScopedRateThrottle()] if self.action == 'create' else []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cv = services.upload_cv(candidate=self.candidate, **serializer.validated_data)
        return Response(self._detail(cv), status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        cv = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.update_cv(cv, **serializer.validated_data)
        return Response(self._detail(cv))

    def destroy(self, request, *args, **kwargs):
        services.delete_cv(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=TAG, summary='Đặt làm CV mặc định', request=None, responses=CVDetailSerializer)
    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, pk=None):
        return Response(self._detail(services.set_default_cv(self.get_object())))

    @extend_schema(
        tags=TAG, summary='Bóc tách lại CV bị lỗi (parse_status = failed)', request=None, responses=CVDetailSerializer
    )
    @action(detail=True, methods=['post'])
    def reparse(self, request, pk=None):
        return Response(self._detail(services.reparse_cv(self.get_object())))

    @extend_schema(
        tags=TAG,
        summary='Xem / tải file CV',
        parameters=[OpenApiParameter('download', OpenApiTypes.BOOL, description='1: tải về thay vì xem trực tiếp')],
        responses={(200, 'application/octet-stream'): OpenApiResponse(OpenApiTypes.BINARY)},
    )
    @action(detail=True, methods=['get'])
    def file(self, request, pk=None):
        cv = self.get_object()
        if not cv.file or not cv.file.storage.exists(cv.file.name):
            raise NotFound('Không tìm thấy file CV.')
        return FileResponse(
            cv.file.open('rb'),
            as_attachment=request.query_params.get('download') in ('1', 'true'),
            filename=cv.original_filename,
            content_type=cv.mime_type,
        )

    def _detail(self, cv):
        fresh = self.get_queryset().get(pk=cv.pk)  # đọc lại để có trạng thái bóc tách & số lần ứng tuyển mới nhất
        return CVDetailSerializer(fresh, context=self.get_serializer_context()).data
