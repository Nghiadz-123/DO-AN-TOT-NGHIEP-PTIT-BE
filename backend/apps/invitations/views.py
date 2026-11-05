"""API thư mời ứng tuyển.

- EmployerInvitationViewSet   nhà tuyển dụng gửi, xem, thu hồi thư mời của công ty
- CandidateInvitationViewSet  ứng viên xem, đánh dấu đã xem, từ chối thư mời
"""
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.candidates.permissions import CandidateAccessMixin
from apps.employers.permissions import EmployerAccessMixin
from common.views import validated_body, validated_query

from . import selectors, services
from .models import Invitation
from .serializers import (
    CandidateInvitationQuerySerializer,
    CandidateInvitationSerializer,
    EmployerInvitationQuerySerializer,
    EmployerInvitationSerializer,
    InvitationCreateSerializer,
    InvitationSummarySerializer,
)

EMPLOYER_TAG = ['Employer - Thư mời ứng tuyển']
CANDIDATE_TAG = ['Candidate - Thư mời ứng tuyển']


class EmployerInvitationViewSet(EmployerAccessMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                                mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Thư mời của công ty (mọi nhà tuyển dụng trong công ty). Thư của công ty khác trả về 404."""

    serializer_class = EmployerInvitationSerializer  # dữ liệu trả về của mọi endpoint (self.get_serializer)
    filter_backends = []  # lọc bằng query riêng (EmployerInvitationQuerySerializer)
    throttle_scope = 'invitation'

    def get_throttles(self):
        return [ScopedRateThrottle()] if self.action == 'create' else []

    def get_queryset(self):  # thư dùng cho các thao tác theo {id}
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Invitation.objects.none()
        return selectors.company_invitations(self.company)

    # GET /api/v1/employer/invitations/?status=&job_id=&q=&page=
    @extend_schema(tags=EMPLOYER_TAG, summary='Thư mời công ty đã gửi (mới gửi trước)',
                   parameters=[EmployerInvitationQuerySerializer], responses=EmployerInvitationSerializer(many=True))
    def list(self, request, *args, **kwargs):
        query = validated_query(request, EmployerInvitationQuerySerializer)
        invitations = selectors.company_invitations(
            self.company, status=query.get('status', ''), job_id=query.get('job_id'), search=query['q'].strip()
        )
        page = self.paginate_queryset(invitations)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    # POST /api/v1/employer/invitations/
    @extend_schema(tags=EMPLOYER_TAG, summary='Gửi thư mời ứng tuyển tới ứng viên',
                   request=InvitationCreateSerializer, responses={201: EmployerInvitationSerializer})
    def create(self, request, *args, **kwargs):
        body = validated_body(request, InvitationCreateSerializer)
        invitation = services.send_invitation(recruiter=self.recruiter, **body)
        fresh = selectors.company_invitations(self.company).get(pk=invitation.pk)
        return Response(self.get_serializer(fresh).data, status=status.HTTP_201_CREATED)

    # DELETE /api/v1/employer/invitations/{id}/
    @extend_schema(tags=EMPLOYER_TAG, summary='Thu hồi thư mời chưa được phản hồi', responses={204: None})
    def destroy(self, request, *args, **kwargs):
        services.withdraw_invitation(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateInvitationViewSet(CandidateAccessMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    """Thư mời ứng viên đang đăng nhập nhận được. Thư của người khác trả về 404.

    Nhận lời mời = nộp hồ sơ vào tin (POST /candidate/applications/): thư tự chuyển sang `accepted`.
    """

    serializer_class = CandidateInvitationSerializer  # dữ liệu trả về của mọi endpoint (self.get_serializer)
    filter_backends = []  # lọc bằng query riêng (CandidateInvitationQuerySerializer)

    def get_queryset(self):  # thư dùng cho các thao tác theo {id}
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Invitation.objects.none()
        return selectors.candidate_invitations(self.candidate)

    # GET /api/v1/candidate/invitations/?status=&page=
    @extend_schema(tags=CANDIDATE_TAG, summary='Thư mời tôi nhận được (mới nhất trước)',
                   parameters=[CandidateInvitationQuerySerializer], responses=CandidateInvitationSerializer(many=True))
    def list(self, request, *args, **kwargs):
        query = validated_query(request, CandidateInvitationQuerySerializer)
        invitations = selectors.candidate_invitations(self.candidate, status=query.get('status', ''))
        page = self.paginate_queryset(invitations)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    # GET /api/v1/candidate/invitations/{id}/
    @extend_schema(tags=CANDIDATE_TAG, summary='Chi tiết thư mời', responses=CandidateInvitationSerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # POST /api/v1/candidate/invitations/{id}/read/
    @extend_schema(tags=CANDIDATE_TAG, summary='Đánh dấu đã xem thư mời', request=None,
                   responses=CandidateInvitationSerializer)
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        invitation = services.mark_read(self.get_object())
        return Response(self._detail_data(invitation))

    # POST /api/v1/candidate/invitations/{id}/decline/
    @extend_schema(tags=CANDIDATE_TAG, summary='Từ chối thư mời đang chờ phản hồi', request=None,
                   responses=CandidateInvitationSerializer)
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        invitation = services.decline_invitation(self.get_object())
        return Response(self._detail_data(invitation))

    # GET /api/v1/candidate/invitations/summary/
    @extend_schema(tags=CANDIDATE_TAG, summary='Số thư mời chưa xem (huy hiệu trên menu)',
                   responses=InvitationSummarySerializer)
    @action(detail=False, methods=['get'])
    def summary(self, request):
        return Response(InvitationSummarySerializer({'unread': selectors.unread_count(self.candidate)}).data)

    def _detail_data(self, invitation) -> dict:
        """Đọc lại thư sau khi sửa, trả dữ liệu dạng CandidateInvitationSerializer."""
        fresh = selectors.candidate_invitations(self.candidate).get(pk=invitation.pk)
        return CandidateInvitationSerializer(fresh, context=self.get_serializer_context()).data
