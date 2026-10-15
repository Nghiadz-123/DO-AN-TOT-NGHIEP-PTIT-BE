from functools import cached_property

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.connections import selectors as connection_selectors
from apps.connections.permissions import IsCandidateOrEmployer

from . import selectors, services
from .models import Conversation
from .serializers import (
    ConversationOpenSerializer,
    ConversationSerializer,
    InboxSummarySerializer,
    MessageCreateSerializer,
    MessageListSerializer,
    MessageSerializer,
    MessagesQuerySerializer,
)

TAG = ['Tin nhắn']


@extend_schema_view(
    list=extend_schema(tags=TAG, summary='Hội thoại của tôi (có tin nhắn gần nhất trước)'),
    retrieve=extend_schema(tags=TAG, summary='Chi tiết hội thoại'),
    create=extend_schema(
        tags=TAG, summary='Mở hội thoại với một bạn bè (đã có thì trả về hội thoại cũ, 200)',
        request=ConversationOpenSerializer, responses={201: ConversationSerializer, 200: ConversationSerializer},
    ),
)
class ConversationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """Hội thoại 1-1 của người đang đăng nhập. Hội thoại của người khác trả về 404."""

    permission_classes = [IsCandidateOrEmployer]
    serializer_class = ConversationSerializer
    filter_backends = []
    throttle_scope = 'chat_message'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # lúc sinh tài liệu OpenAPI không có user
            return Conversation.objects.none()
        return selectors.user_conversations(self.request.user)

    def get_throttles(self):
        # Giới hạn tốc độ gửi tin nhắn; đọc / hỏi định kỳ không giới hạn
        sending = self.action == 'messages' and self.request.method == 'POST'
        return [ScopedRateThrottle()] if sending else []

    @cached_property
    def friend_ids(self):
        return connection_selectors.friend_ids(self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not getattr(self, 'swagger_fake_view', False):
            context['friend_ids'] = self.friend_ids
        return context

    def create(self, request, *args, **kwargs):
        serializer = ConversationOpenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation, created = services.get_or_create_conversation(request.user, serializer.validated_data['other'])
        return Response(self._detail(conversation), status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(methods=['GET'], tags=TAG, summary='Tin nhắn của hội thoại (mới nhất, cũ hơn hoặc mới hơn một id)',
                   parameters=[MessagesQuerySerializer], responses=MessageListSerializer)
    @extend_schema(methods=['POST'], tags=TAG, summary='Gửi tin nhắn (chỉ khi hai bên là bạn bè)',
                   request=MessageCreateSerializer, responses={201: MessageSerializer})
    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == 'POST':
            serializer = MessageCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            message = services.send_message(conversation, sender=request.user, body=serializer.validated_data['body'])
            return Response(MessageSerializer(message, context=self.get_serializer_context()).data,
                            status=status.HTTP_201_CREATED)

        query = MessagesQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        items, has_more = selectors.conversation_messages(conversation, **query.validated_data)
        return Response({
            'results': MessageSerializer(items, many=True, context=self.get_serializer_context()).data,
            'has_more': has_more,
        })

    @extend_schema(tags=TAG, summary='Đánh dấu đã đọc mọi tin nhắn mình nhận trong hội thoại', request=None,
                   responses={204: None})
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        services.mark_read(self.get_object(), user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=TAG, summary='Số tin nhắn chưa đọc và lời mời kết bạn đang chờ (huy hiệu trên menu)',
                   responses=InboxSummarySerializer)
    @action(detail=False, methods=['get'])
    def summary(self, request):
        return Response(InboxSummarySerializer(selectors.inbox_summary(request.user)).data)

    def _detail(self, conversation):
        fresh = self.get_queryset().get(pk=conversation.pk)
        return ConversationSerializer(fresh, context=self.get_serializer_context()).data
