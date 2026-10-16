from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.candidates.permissions import CandidateAccessMixin
from apps.employers.permissions import EmployerAccessMixin

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


def _query(serializer_class, request) -> dict:
    query = serializer_class(data=request.query_params)
    query.is_valid(raise_exception=True)
    return query.validated_data


@extend_schema_view(
    list=extend_schema(
        tags=EMPLOYER_TAG, summary='Thư mời công ty đã gửi (mới gửi trước)', parameters=[EmployerInvitationQuerySerializer]
    ),
    create=extend_schema(
        tags=EMPLOYER_TAG, summary='Gửi thư mời ứng tuyển tới ứng viên',
        request=InvitationCreateSerializer, responses={201: EmployerInvitationSerializer},
    ),
    destroy=extend_schema(tags=EMPLOYER_TAG, summary='Thu hồi thư mời chưa được phản hồi'),
)
class EmployerInvitationViewSet(EmployerAccessMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                                mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Thư mời của công ty (mọi nhà tuyển dụng trong công ty). Thư của công ty khác trả về 404."""

    serializer_class = EmployerInvitationSerializer
    filter_backends = []
    throttle_scope = 'invitation'

    def get_throttles(self):
        return [ScopedRateThrottle()] if self.action == 'create' else []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Invitation.objects.none()
        if self.action == 'list':
            params = _query(EmployerInvitationQuerySerializer, self.request)
            return selectors.company_invitations(
                self.company, status=params.get('status', ''), job_id=params.get('job_id'), search=params['q'].strip()
            )
        return selectors.company_invitations(self.company)

    def create(self, request, *args, **kwargs):
        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = services.send_invitation(recruiter=self.recruiter, **serializer.validated_data)
        fresh = selectors.company_invitations(self.company).get(pk=invitation.pk)
        return Response(self.get_serializer(fresh).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        services.withdraw_invitation(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        tags=CANDIDATE_TAG, summary='Thư mời tôi nhận được (mới nhất trước)', parameters=[CandidateInvitationQuerySerializer]
    ),
    retrieve=extend_schema(tags=CANDIDATE_TAG, summary='Chi tiết thư mời'),
)
class CandidateInvitationViewSet(CandidateAccessMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    """Thư mời ứng viên đang đăng nhập nhận được. Thư của người khác trả về 404.

    Nhận lời mời = nộp hồ sơ vào tin (POST /candidate/applications/): thư tự chuyển sang `accepted`.
    """

    serializer_class = CandidateInvitationSerializer
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Invitation.objects.none()
        if self.action == 'list':
            params = _query(CandidateInvitationQuerySerializer, self.request)
            return selectors.candidate_invitations(self.candidate, status=params.get('status', ''))
        return selectors.candidate_invitations(self.candidate)

    @extend_schema(tags=CANDIDATE_TAG, summary='Đánh dấu đã xem thư mời', request=None,
                   responses=CandidateInvitationSerializer)
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        return Response(self._detail(services.mark_read(self.get_object())))

    @extend_schema(tags=CANDIDATE_TAG, summary='Từ chối thư mời đang chờ phản hồi', request=None,
                   responses=CandidateInvitationSerializer)
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        return Response(self._detail(services.decline_invitation(self.get_object())))

    @extend_schema(tags=CANDIDATE_TAG, summary='Số thư mời chưa xem (huy hiệu trên menu)',
                   responses=InvitationSummarySerializer)
    @action(detail=False, methods=['get'])
    def summary(self, request):
        return Response({'unread': selectors.unread_count(self.candidate)})

    def _detail(self, invitation):
        fresh = selectors.candidate_invitations(self.candidate).get(pk=invitation.pk)
        return CandidateInvitationSerializer(fresh, context=self.get_serializer_context()).data
