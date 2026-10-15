"""Nhắn tin trực tiếp 1-1 giữa hai tài khoản đã kết bạn (app connections).

Hủy kết bạn thì hội thoại cũ vẫn xem được nhưng không gửi thêm tin nhắn.
Frontend lấy tin nhắn mới bằng cách hỏi định kỳ GET .../messages/?after=<id tin cuối>; id tin nhắn tăng dần
nên dùng được làm con trỏ. Sau này có thể thay bằng WebSocket (Django Channels) mà không đổi model.
"""
from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.utils import timezone

from common.models import TimeStampedModel, UUIDModel


class Conversation(UUIDModel, TimeStampedModel):
    """user_a có id nhỏ hơn user_b, nhờ vậy mỗi cặp tài khoản chỉ có một hội thoại."""

    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', verbose_name='người tham gia A'
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', verbose_name='người tham gia B'
    )
    # Denormalized để sắp xếp danh sách hội thoại; lúc chưa có tin nhắn = thời điểm tạo hội thoại
    last_message_at = models.DateTimeField('tin nhắn gần nhất lúc', default=timezone.now)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'hội thoại'
        verbose_name_plural = 'hội thoại'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['user_a', '-last_message_at'], name='idx_conversations_user_a'),
            models.Index(fields=['user_b', '-last_message_at'], name='idx_conversations_user_b'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user_a', 'user_b'], name='uq_conversations_pair'),
            CheckConstraint(condition=Q(user_a__lt=F('user_b')), name='ck_conversations_ordered_pair'),
        ]

    def __str__(self):
        return f'{self.user_a} - {self.user_b}'

    def has_participant(self, user) -> bool:
        return user.pk in (self.user_a_id, self.user_b_id)

    def other(self, user):
        return self.user_b if self.user_a_id == user.pk else self.user_a


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name='hội thoại'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', verbose_name='người gửi'
    )
    body = models.TextField('nội dung')
    created_at = models.DateTimeField('gửi lúc', default=timezone.now)
    read_at = models.DateTimeField('người nhận đã đọc lúc', null=True, blank=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'tin nhắn'
        verbose_name_plural = 'tin nhắn'
        ordering = ['id']
        indexes = [models.Index(fields=['conversation', 'id'], name='idx_messages_conversation')]

    def __str__(self):
        return self.body[:50]
