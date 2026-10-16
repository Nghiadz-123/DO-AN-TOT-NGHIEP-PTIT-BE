from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.candidates.models import CandidateProfile
from apps.employers.permissions import EmployerAccessMixin
from apps.invitations import selectors as invitation_selectors

from . import selectors
from .serializers import TalentMatchSerializer, TalentPoolQuerySerializer, TalentProfileSerializer, TalentQuerySerializer

TAG = ['Employer - Tìm ứng viên']


@extend_schema_view(get=extend_schema(
    tags=TAG,
    summary='Tìm ứng viên: ứng viên công khai CV (CV cập nhật gần nhất trước)',
    parameters=[TalentPoolQuerySerializer],
))
class TalentPoolView(EmployerAccessMixin, generics.ListAPIView):
    """Mọi ứng viên bật công khai CV (không cần chọn tin tuyển dụng), kèm CV chính và thư mời gần nhất của công ty."""

    serializer_class = TalentProfileSerializer
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return CandidateProfile.objects.none()
        query = TalentPoolQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data
        return selectors.talent_pool(
            search=params['q'].strip(), location_id=params.get('location_id'), level=params.get('level', '')
        )

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        invitations = invitation_selectors.invitation_map(self.company, (c.pk for c in page))
        return [
            selectors.TalentProfile(candidate=c, cv=c.default_cvs[0], invitation=invitations.get(c.pk)) for c in page
        ]


@extend_schema_view(get=extend_schema(
    tags=TAG,
    summary='Ứng viên phù hợp với tin tuyển dụng (điểm 0-100, kỹ năng đáp ứng / còn thiếu, lý do)',
    parameters=[TalentQuerySerializer],
))
class SuggestedCandidatesView(EmployerAccessMixin, generics.ListAPIView):
    """Ứng viên có CV phù hợp với một tin của công ty: công khai CV hoặc đã ứng tuyển vào công ty.
    Kết quả là danh sách đã chấm điểm (không phải queryset) nên không dùng filter backend."""

    serializer_class = TalentMatchSerializer
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return []
        self.job = selectors.get_company_job(self.company, self.kwargs['job_id'])
        if self.job is None:
            raise NotFound('Không tìm thấy tin tuyển dụng.')
        query = TalentQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data
        return selectors.suggested_candidates(
            self.job, self.company, search=params['q'].strip(), min_score=params['min_score'],
            hide_applied=params['hide_applied'],
        )

    def paginate_queryset(self, queryset):
        # Thư mời của tin đang xem chỉ tra cho các ứng viên của trang hiện tại
        page = super().paginate_queryset(queryset)
        invitations = invitation_selectors.invitation_map(self.company, (m.candidate.pk for m in page), job=self.job)
        for item in page:
            item.invitation = invitations.get(item.candidate.pk)
        return page


class TalentCVFileView(EmployerAccessMixin, APIView):
    """CV mặc định của một ứng viên mà công ty được xem (công khai CV hoặc đã ứng tuyển vào công ty)."""

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
