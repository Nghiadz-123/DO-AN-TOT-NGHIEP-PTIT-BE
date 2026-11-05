"""API nhà tuyển dụng chủ động tìm ứng viên.

- TalentPoolView            mọi ứng viên công khai CV (không cần chọn tin)
- SuggestedCandidatesView   ứng viên phù hợp với một tin của công ty, có điểm 0-100
- TalentCVFileView          xem / tải CV mặc định của một ứng viên công ty được xem
"""
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.employers.permissions import EmployerAccessMixin
from apps.invitations import selectors as invitation_selectors
from common.views import DOWNLOAD_PARAMETER, FILE_RESPONSE, file_response, validated_query

from . import selectors
from .serializers import TalentMatchSerializer, TalentPoolQuerySerializer, TalentProfileSerializer, TalentQuerySerializer

TAG = ['Employer - Tìm ứng viên']


class TalentPoolView(EmployerAccessMixin, generics.GenericAPIView):
    """Mọi ứng viên bật công khai CV (không cần chọn tin tuyển dụng), kèm CV chính và thư mời gần nhất của công ty."""

    serializer_class = TalentProfileSerializer
    filter_backends = []  # lọc bằng query riêng (TalentPoolQuerySerializer), không dùng django-filter / ordering

    # GET /api/v1/employer/talents/?q=&location_id=&level=&page=
    @extend_schema(tags=TAG, summary='Tìm ứng viên: ứng viên công khai CV (CV cập nhật gần nhất trước)',
                   parameters=[TalentPoolQuerySerializer], responses=TalentProfileSerializer(many=True))
    def get(self, request):
        query = validated_query(request, TalentPoolQuerySerializer)
        candidates = selectors.talent_pool(
            search=query['q'].strip(), location_id=query.get('location_id'), level=query.get('level', '')
        )
        page = self.paginate_queryset(candidates)
        # Thư mời chỉ tra cho các ứng viên của trang hiện tại
        invitations = invitation_selectors.invitation_map(self.company, (c.pk for c in page))
        profiles = [
            selectors.TalentProfile(candidate=c, cv=c.default_cvs[0], invitation=invitations.get(c.pk)) for c in page
        ]
        return self.get_paginated_response(self.get_serializer(profiles, many=True).data)


class SuggestedCandidatesView(EmployerAccessMixin, generics.GenericAPIView):
    """Ứng viên có CV phù hợp với một tin của công ty: công khai CV hoặc đã ứng tuyển vào công ty."""

    serializer_class = TalentMatchSerializer
    filter_backends = []  # kết quả là danh sách đã chấm điểm (không phải queryset)

    # GET /api/v1/employer/jobs/{job_id}/suggested-candidates/?q=&min_score=&hide_applied=&page=
    @extend_schema(tags=TAG, summary='Ứng viên phù hợp với tin tuyển dụng (điểm 0-100, kỹ năng đáp ứng / còn thiếu, lý do)',
                   parameters=[TalentQuerySerializer], responses=TalentMatchSerializer(many=True))
    def get(self, request, job_id):
        job = selectors.get_company_job(self.company, job_id)
        if job is None:
            raise NotFound('Không tìm thấy tin tuyển dụng.')
        query = validated_query(request, TalentQuerySerializer)
        matches = selectors.suggested_candidates(
            job, self.company, search=query['q'].strip(), min_score=query['min_score'],
            hide_applied=query['hide_applied'],
        )
        page = self.paginate_queryset(matches)
        # Thư mời của chính tin này, chỉ tra cho các ứng viên của trang hiện tại
        invitations = invitation_selectors.invitation_map(self.company, (m.candidate.pk for m in page), job=job)
        for match in page:
            match.invitation = invitations.get(match.candidate.pk)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)


class TalentCVFileView(EmployerAccessMixin, APIView):
    """CV mặc định của một ứng viên mà công ty được xem (công khai CV hoặc đã ứng tuyển vào công ty)."""

    # GET /api/v1/employer/talents/{candidate_id}/cv/?download=1
    @extend_schema(tags=TAG, summary='Xem / tải CV mặc định của ứng viên', parameters=[DOWNLOAD_PARAMETER],
                   responses=FILE_RESPONSE)
    def get(self, request, candidate_id):
        candidate = selectors.get_discoverable_candidate(self.company, candidate_id)
        cv = candidate.default_cvs[0] if candidate and candidate.default_cvs else None
        if cv is None:
            raise NotFound('Không tìm thấy CV.')
        return file_response(request, cv.file, filename=cv.original_filename, content_type=cv.mime_type,
                             not_found_message='Không tìm thấy CV.')
