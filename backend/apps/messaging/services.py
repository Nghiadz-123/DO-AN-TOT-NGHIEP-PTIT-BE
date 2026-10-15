"""Nghiệp vụ nhắn tin: mở hội thoại, gửi tin nhắn, đánh dấu đã đọc. Chỉ bạn bè (connections) mới nhắn được."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.connections import selectors as connection_selectors
from common.exceptions import BusinessError
from common.utils import send_on_commit

from . import signals
from .models import Conversation, Message

BODY_MAX_LENGTH = 2000
NOT_CONNECTED_MESSAGE = 'Chỉ nhắn tin được với tài khoản đã kết bạn.'


def get_or_create_conversation(user, other) -> tuple[Conversation, bool]:
    """Hội thoại giữa hai bạn bè (tạo mới nếu chưa có). Trả về (conversation, created)."""
    if other.pk == user.pk:
        raise BusinessError('Không thể nhắn tin cho chính mình.', code='invalid_recipient')
    if not connection_selectors.are_connected(user, other):
        raise BusinessError(NOT_CONNECTED_MESSAGE, code='not_connected', status_code=403)
    user_a, user_b = sorted((user, other), key=lambda u: u.pk)
    return Conversation.objects.get_or_create(user_a=user_a, user_b=user_b)


@transaction.atomic
def send_message(conversation: Conversation, *, sender, body: str) -> Message:
    body = (body or '').strip()
    if not body:
        raise ValidationError({'body': 'Nội dung tin nhắn không được để trống.'})
    if not connection_selectors.are_connected(sender, conversation.other(sender)):
        raise BusinessError(
            'Hai bạn không còn là bạn bè nên không thể gửi tin nhắn.', code='not_connected', status_code=403
        )
    message = Message.objects.create(conversation=conversation, sender=sender, body=body[:BODY_MAX_LENGTH])
    Conversation.objects.filter(pk=conversation.pk).update(
        last_message_at=message.created_at, updated_at=message.created_at
    )
    send_on_commit(signals.message_sent, sender=Message, message=message)
    return message


def mark_read(conversation: Conversation, *, user) -> int:
    """Đánh dấu đã đọc mọi tin nhắn `user` nhận trong hội thoại. Trả về số tin vừa đánh dấu."""
    return (
        conversation.messages.filter(read_at__isnull=True).exclude(sender=user).update(read_at=timezone.now())
    )


@transaction.atomic
def start_conversation_from_connection(connection) -> Conversation:
    """Khi ứng viên chấp nhận lời mời: tạo hội thoại (kết bạn lại thì dùng hội thoại cũ); lời nhắn kèm lời
    mời thành một tin nhắn (giữ thời điểm gửi lời mời, coi như đã đọc vì ứng viên vừa xem trong lời mời)."""
    conversation, _ = get_or_create_conversation(connection.addressee, connection.requester)
    already_added = conversation.messages.filter(sender=connection.requester, created_at=connection.created_at)
    if connection.message.strip() and not already_added.exists():  # gọi lại nhiều lần không tạo trùng
        Message.objects.create(
            conversation=conversation, sender=connection.requester, body=connection.message.strip(),
            created_at=connection.created_at, read_at=connection.responded_at,
        )
        Conversation.objects.filter(pk=conversation.pk).update(last_message_at=connection.responded_at)
    return conversation
