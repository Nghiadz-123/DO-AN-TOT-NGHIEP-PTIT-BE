"""Các truy vấn đọc hội thoại và tin nhắn."""
from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from apps.connections import selectors as connection_selectors

from .models import Conversation, Message

MESSAGES_PAGE_SIZE = 50   # số tin nhắn mỗi lần tải (mới nhất / cũ hơn)
NEW_MESSAGES_LIMIT = 200  # số tin nhắn mới tối đa mỗi lần hỏi định kỳ (?after=)

_PARTICIPANT_RELATED = (
    'user_a__candidate_profile', 'user_a__recruiter__company',
    'user_b__candidate_profile', 'user_b__recruiter__company',
)


def _involving(user) -> Q:
    return Q(user_a=user) | Q(user_b=user)


def _unread_for(user):
    return Message.objects.filter(read_at__isnull=True).exclude(sender=user)


def user_conversations(user):
    """Hội thoại của `user`, có tin nhắn gần nhất trước, kèm số tin chưa đọc và tin nhắn cuối."""
    last = Message.objects.filter(conversation=OuterRef('pk')).order_by('-id')
    unread = (
        _unread_for(user).filter(conversation=OuterRef('pk'))
        .values('conversation').annotate(n=Count('id')).values('n')
    )
    return (
        Conversation.objects.filter(_involving(user))
        .select_related(*_PARTICIPANT_RELATED)
        .annotate(
            unread_count=Coalesce(Subquery(unread, output_field=IntegerField()), 0),
            last_message_id=Subquery(last.values('id')[:1]),
            last_message_body=Subquery(last.values('body')[:1]),
            last_message_sender_id=Subquery(last.values('sender_id')[:1]),
        )
        .order_by('-last_message_at', '-created_at')
    )


def conversation_messages(conversation, *, after: int | None = None, before: int | None = None):
    """Tin nhắn theo thứ tự gửi. Trả về (danh sách, has_more).

    - after: tin mới hơn id này (hỏi định kỳ), tối đa NEW_MESSAGES_LIMIT;
    - before: MESSAGES_PAGE_SIZE tin cũ hơn id này (cuộn lên xem tin cũ);
    - không truyền: MESSAGES_PAGE_SIZE tin mới nhất.
    """
    qs = conversation.messages.all()
    if after is not None:
        items = list(qs.filter(id__gt=after).order_by('id')[: NEW_MESSAGES_LIMIT + 1])
        return items[:NEW_MESSAGES_LIMIT], len(items) > NEW_MESSAGES_LIMIT
    if before is not None:
        qs = qs.filter(id__lt=before)
    items = list(qs.order_by('-id')[: MESSAGES_PAGE_SIZE + 1])
    return list(reversed(items[:MESSAGES_PAGE_SIZE])), len(items) > MESSAGES_PAGE_SIZE


def inbox_summary(user) -> dict:
    """Số liệu cho huy hiệu trên menu: tin nhắn chưa đọc, lời mời kết bạn đang chờ phản hồi."""
    unread = _unread_for(user).filter(Q(conversation__user_a=user) | Q(conversation__user_b=user))
    stats = unread.aggregate(messages=Count('id'), conversations=Count('conversation', distinct=True))
    return {
        'unread_messages': stats['messages'],
        'unread_conversations': stats['conversations'],
        'pending_requests': connection_selectors.received_requests(user).count(),
    }
