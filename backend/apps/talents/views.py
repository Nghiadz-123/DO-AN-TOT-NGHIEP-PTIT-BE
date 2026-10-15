from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.connections import selectors as connection_selectors
from apps.employers.permissions import EmployerAccessMixin

from . import selectors
from .serializers import TalentMatchSerializer, TalentQuerySerializer

TAG = ['Employer - Ứng viên phù hợp']


@extend_schema_view(get=extend_schema(
    tags=TAG,
    summary='Ứng viên phù hợp với tin tuyển dụng (điểm 0-100, kỹ năng đáp ứng / còn thiếu, lý do)',
    parameters=[TalentQuerySerializer],
))
class SuggestedCandidatesView(EmployerAccessMixin, generics.ListAPIView):
    """Ứng viên có CV phù hợp với một tin của công ty: hồ sơ công khai hoặc đã ứng tuyển vào công ty.
    Kết quả là danh sách đã chấm điểm (không phải queryset) nên không dùng filter backend."""

    serializer_class = TalentMatchSerializer
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return []
        job = selectors.get_company_job(self.company, self.kwargs['job_id'])
        if job is None:
            raise NotFound('Không tìm thấy tin tuyển dụng.')
        query = TalentQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data
        return selectors.suggested_candidates(
            job, self.company, search=params['q'].strip(), min_score=params['min_score'],
            hide_applied=params['hide_applied'],
        )

    def paginate_queryset(self, queryset):
        # Trạng thái kết bạn chỉ tra cho các ứng viên của trang hiện tại
        page = super().paginate_queryset(queryset)
        connections = connection_selectors.connection_map(self.request.user, (m.candidate.user_id for m in page))
        for item in page:
            item.connection = connections.get(item.candidate.user_id)
        return page


class TalentCVFileView(EmployerAccessMixin, APIView):
    """CV mặc định của một ứng viên mà công ty được xem (hồ sơ công khai hoặc đã ứng tuyển vào công ty)."""

    @extend_schema(
        tags=TAG,
        summary='Xem / tải CV mặc định của ứng viên',
        parameters=[OpenApiParameter('download', OpenApiTypes.BOOL, description='1: tải về thay vì xem trực tiếp')],
        responses={(200, 'application/octet-stream'): OpenApiResponse(OpenApiTypes.BINARY)},
    )
    def get(self, request, candidate_id):
        candidate = selectors.get_discoverable_candidate(self.company, candidate_id)
        cv = candidate.default_cvs[0] if candidate and candidate.default_cvs else None
        if cv is None or not cv.file or not cv.file.storage.exists(cv.file.name):
            raise NotFound('Không tìm thấy CV.')
        return FileResponse(
            cv.file.open('rb'),
            as_attachment=request.query_params.get('download') in ('1', 'true'),
            filename=cv.original_filename,
            content_type=cv.mime_type,
        )
