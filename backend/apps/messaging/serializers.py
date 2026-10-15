from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.accounts.models import User
from apps.connections.serializers import ParticipantSerializer

from .models import Conversation, Message
from .services import BODY_MAX_LENGTH

PREVIEW_LENGTH = 120


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.UUIDField(read_only=True)
    is_mine = serializers.SerializerMethodField(help_text='Tin do người đang đăng nhập gửi')

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'body', 'created_at', 'read_at', 'is_mine']

    def get_is_mine(self, obj) -> bool:
        return obj.sender_id == self.context['request'].user.pk


class LastMessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    body = serializers.CharField(help_text=f'Tối đa {PREVIEW_LENGTH} ký tự đầu')
    is_mine = serializers.BooleanField()


class ConversationSerializer(serializers.ModelSerializer):
    """Hội thoại nhìn từ phía người đang đăng nhập (queryset: selectors.user_conversations)."""

    user = serializers.SerializerMethodField(help_text='Người còn lại trong hội thoại')
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True)
    can_send = serializers.SerializerMethodField(help_text='False khi hai bên không còn là bạn bè')

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'last_message', 'unread_count', 'can_send', 'last_message_at', 'created_at']

    def _me(self):
        return self.context['request'].user

    @extend_schema_field(ParticipantSerializer)
    def get_user(self, obj):
        return ParticipantSerializer(obj.other(self._me()), context=self.context).data

    @extend_schema_field(LastMessageSerializer(allow_null=True))
    def get_last_message(self, obj):
        if not obj.last_message_id:
            return None
        return {
            'id': obj.last_message_id,
            'body': obj.last_message_body[:PREVIEW_LENGTH],
            'is_mine': obj.last_message_sender_id == self._me().pk,
        }

    def get_can_send(self, obj) -> bool:
        return obj.other(self._me()).pk in self.context['friend_ids']


class ConversationOpenSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='other',
        queryset=User.objects.filter(is_active=True, deleted_at__isnull=True),
        pk_field=serializers.UUIDField(),
        error_messages={'does_not_exist': 'Không tìm thấy tài khoản.'},
        help_text='Id tài khoản bạn bè muốn nhắn tin',
    )


class MessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=BODY_MAX_LENGTH)


class MessagesQuerySerializer(serializers.Serializer):
    after = serializers.IntegerField(required=False, min_value=0, help_text='Lấy tin mới hơn id này')
    before = serializers.IntegerField(required=False, min_value=1, help_text='Lấy tin cũ hơn id này')


class MessageListSerializer(serializers.Serializer):
    results = MessageSerializer(many=True)
    has_more = serializers.BooleanField(help_text='Còn tin (cũ hơn, hoặc mới hơn khi dùng after) chưa tải')


class InboxSummarySerializer(serializers.Serializer):
    unread_messages = serializers.IntegerField()
    unread_conversations = serializers.IntegerField()
    pending_requests = serializers.IntegerField(help_text='Lời mời kết bạn đang chờ mình phản hồi')
