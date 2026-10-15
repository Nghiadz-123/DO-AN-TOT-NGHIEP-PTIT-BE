from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.employers.permissions import IsEmployer

from . import selectors, services
from .models import Connection
from .permissions import IsCandidateOrEmployer
from .serializers import ConnectionRequestSerializer, ConnectionSerializer

TAG = ['Kết bạn']
BOXES = ('received', 'sent')


@extend_schema_view(
    list=extend_schema(
        tags=TAG, summary='Danh sách bạn bè (kết bạn gần nhất trước)',
        parameters=[OpenApiParameter('q', str, description='Tìm theo tên')],
    ),
    create=extend_schema(
        tags=TAG, summary='Nhà tuyển dụng gửi lời mời kết bạn tới ứng viên',
        request=ConnectionRequestSerializer, responses={201: ConnectionSerializer},
    ),
    destroy=extend_schema(tags=TAG, summary='Hủy kết bạn / hủy lời mời đang chờ (người gửi)'),
)
class ConnectionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Lời mời kết bạn và bạn bè của người đang đăng nhập. Bản ghi của người khác trả về 404."""

    serializer_class = ConnectionSerializer
    filter_backends = []
    throttle_scope = 'connection_request'

    def get_permissions(self):
        # Chỉ nhà tuyển dụng gửi lời mời (IsEmployer gắn request.recruiter)
        return [IsEmployer()] if self.action == 'create' else [IsCandidateOrEmployer()]

    def get_throttles(self):
        return [ScopedRateThrottle()] if self.action == 'create' else []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Connection.objects.none()
        user = self.request.user
        if self.action == 'list':
            return selectors.friends(user, search=self.request.query_params.get('q', '').strip())
        if self.action == 'requests':
            box = self.request.query_params.get('box', 'received')
            return selectors.sent_requests(user) if box == 'sent' else selectors.received_requests(user)
        return selectors.user_connections(user)

    def create(self, request, *args, **kwargs):
        serializer = ConnectionRequestSerializer(data=request.data, context={'company': request.recruiter.company})
        serializer.is_valid(raise_exception=True)
        connection = services.send_request(recruiter=request.recruiter, **serializer.validated_data)
        return Response(self._detail(connection), status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        services.remove_connection(self.get_object(), by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=TAG, summary='Lời mời kết bạn: đã nhận (đang chờ mình phản hồi) hoặc đã gửi (đang chờ / bị từ chối)',
        parameters=[OpenApiParameter('box', str, enum=BOXES, description='received (mặc định) | sent')],
        responses=ConnectionSerializer(many=True),
    )
    @action(detail=False, methods=['get'])
    def requests(self, request):
        return self.list(request)

    @extend_schema(tags=TAG, summary='Chấp nhận lời mời (người nhận)', request=None, responses=ConnectionSerializer)
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        return Response(self._detail(services.accept_request(self.get_object(), by=request.user)))

    @extend_schema(tags=TAG, summary='Từ chối lời mời (người nhận)', request=None, responses=ConnectionSerializer)
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        return Response(self._detail(services.decline_request(self.get_object(), by=request.user)))

    def _detail(self, connection):
        fresh = selectors.user_connections(self.request.user).get(pk=connection.pk)
        return ConnectionSerializer(fresh, context=self.get_serializer_context()).data
