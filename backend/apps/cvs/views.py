"""API CV của ứng viên.

- CandidateCVViewSet       "CV của tôi": tải lên, đổi tên, xóa, đặt mặc định, bóc tách lại, xem / tải file
- CandidateCVBuilderView   CV tự tạo (trang Tạo CV): lưu nội dung thì dựng thành file DOCX trong "CV của tôi"
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.candidates.permissions import CandidateAccessMixin
from common.views import DOWNLOAD_PARAMETER, FILE_RESPONSE, file_response, validated_body

from . import selectors, services
from .models import CV
from .serializers import (
    CVBuilderDocumentSerializer,
    CVBuilderSerializer,
    CVDetailSerializer,
    CVSerializer,
    CVUpdateSerializer,
    CVUploadSerializer,
)

TAG = ['Candidate - CV']


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

    def get_serializer_class(self):  # serializer DRF dùng cho list / retrieve (và form trên Swagger)
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

    # GET /api/v1/candidate/cvs/?ordering=   (không phân trang)
    @extend_schema(tags=TAG, summary='Danh sách CV của tôi (CV mặc định đứng đầu)', responses=CVSerializer(many=True))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # GET /api/v1/candidate/cvs/{id}/
    @extend_schema(tags=TAG, summary='Chi tiết CV: trạng thái và kết quả bóc tách', responses=CVDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # POST /api/v1/candidate/cvs/   (multipart/form-data)
    @extend_schema(
        tags=TAG,
        summary='Tải lên CV (PDF/DOCX, tối đa 5 MB)',
        description='multipart/form-data. CV được bóc tách văn bản ngay sau khi lưu: theo dõi `parse_status` '
        '(pending → processing → completed | failed) bằng API chi tiết.',
        request={'multipart/form-data': CVUploadSerializer},
        responses={201: CVDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        body = validated_body(request, CVUploadSerializer)
        cv = services.upload_cv(candidate=self.candidate, **body)
        return Response(self._detail_data(cv), status=status.HTTP_201_CREATED)

    # PATCH /api/v1/candidate/cvs/{id}/
    @extend_schema(tags=TAG, summary='Đổi tên CV', request=CVUpdateSerializer, responses=CVDetailSerializer)
    def partial_update(self, request, *args, **kwargs):
        cv = self.get_object()
        body = validated_body(request, CVUpdateSerializer)
        services.update_cv(cv, **body)
        return Response(self._detail_data(cv))

    # DELETE /api/v1/candidate/cvs/{id}/
    @extend_schema(tags=TAG, summary='Xóa CV (CV đã dùng ứng tuyển vẫn được giữ cho nhà tuyển dụng)',
                   responses={204: None})
    def destroy(self, request, *args, **kwargs):
        services.delete_cv(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    # POST /api/v1/candidate/cvs/{id}/set-default/
    @extend_schema(tags=TAG, summary='Đặt làm CV mặc định', request=None, responses=CVDetailSerializer)
    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, pk=None):
        cv = services.set_default_cv(self.get_object())
        return Response(self._detail_data(cv))

    # POST /api/v1/candidate/cvs/{id}/reparse/
    @extend_schema(tags=TAG, summary='Bóc tách lại CV bị lỗi (parse_status = failed)', request=None,
                   responses=CVDetailSerializer)
    @action(detail=True, methods=['post'])
    def reparse(self, request, pk=None):
        cv = services.reparse_cv(self.get_object())
        return Response(self._detail_data(cv))

    # GET /api/v1/candidate/cvs/{id}/file/?download=1
    @extend_schema(tags=TAG, summary='Xem / tải file CV', parameters=[DOWNLOAD_PARAMETER], responses=FILE_RESPONSE)
    @action(detail=True, methods=['get'])
    def file(self, request, pk=None):
        cv = self.get_object()
        return file_response(request, cv.file, filename=cv.original_filename, content_type=cv.mime_type,
                             not_found_message='Không tìm thấy file CV.')

    def _detail_data(self, cv) -> dict:
        """Đọc lại CV (trạng thái bóc tách & số lần ứng tuyển mới nhất), trả dữ liệu dạng CVDetailSerializer."""
        fresh = self.get_queryset().get(pk=cv.pk)
        return CVDetailSerializer(fresh, context=self.get_serializer_context()).data


class CandidateCVBuilderView(CandidateAccessMixin, APIView):
    """CV tự tạo của ứng viên hiện tại. Lưu = dựng file DOCX và thêm vào danh sách "CV của tôi" (có thể ứng tuyển, AI phân tích)."""

    # GET /api/v1/candidate/cv-builder/
    @extend_schema(tags=TAG, summary='Nội dung CV tự tạo đã lưu và CV tương ứng (mọi trường null nếu chưa lưu)',
                   responses=CVBuilderSerializer)
    def get(self, request):
        document = selectors.get_builder_document(self.candidate)
        return Response(CVBuilderSerializer(self._builder_data(document), context={'request': request}).data)

    # PUT /api/v1/candidate/cv-builder/
    @extend_schema(tags=TAG, summary='Lưu nội dung CV và dựng thành CV thật', request=CVBuilderDocumentSerializer,
                   responses=CVBuilderSerializer)
    def put(self, request):
        body = validated_body(request, CVBuilderDocumentSerializer)
        document = services.save_builder_cv(candidate=self.candidate, content=body['content'])
        return Response(CVBuilderSerializer(self._builder_data(document), context={'request': request}).data)

    def _builder_data(self, document) -> dict:
        if document is None:
            return {'content': None, 'updated_at': None, 'cv': None}
        cv = selectors.candidate_cvs(self.candidate).filter(pk=document.cv_id).first() if document.cv_id else None
        return {'content': document.content, 'updated_at': document.updated_at, 'cv': cv}
