"""Lời mời kết bạn và quan hệ bạn bè giữa hai tài khoản.

Hiện chỉ nhà tuyển dụng gửi lời mời tới ứng viên mà họ tìm thấy (xem services.send_request); ứng viên
chấp nhận thì hai bên trở thành bạn bè và nhắn tin được với nhau (app messaging).
Mỗi cặp tài khoản có tối đa một bản ghi: gửi lại sau khi bị từ chối dùng lại bản ghi cũ,
hủy lời mời / hủy kết bạn thì xóa bản ghi.
"""
from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, F, Q

from common.models import TimeStampedModel, UUIDModel, choices_constraint


class ConnectionStatus(models.TextChoices):
    PENDING = 'pending', 'Chờ phản hồi'
    ACCEPTED = 'accepted', 'Đã kết bạn'
    DECLINED = 'declined', 'Đã từ chối'


class Connection(UUIDModel, TimeStampedModel):
    """created_at = thời điểm gửi lời mời (gửi lại thì cập nhật)."""

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_connections',
        verbose_name='người gửi lời mời',
    )
    addressee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_connections',
        verbose_name='người nhận lời mời',
    )
    status = models.CharField(
        'trạng thái', max_length=20, choices=ConnectionStatus.choices, default=ConnectionStatus.PENDING
    )
    message = models.TextField('lời nhắn', blank=True)
    # Tin tuyển dụng nhà tuyển dụng đang xem khi gửi lời mời (để ứng viên biết lý do được mời)
    job = models.ForeignKey(
        'jobs.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='tin tuyển dụng liên quan',
    )
    responded_at = models.DateTimeField('phản hồi lúc', null=True, blank=True)

    class Meta:
        db_table = 'connections'
        verbose_name = 'kết bạn'
        verbose_name_plural = 'kết bạn'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['addressee', 'status'], name='idx_connections_addressee')]
        constraints = [
            models.UniqueConstraint(fields=['requester', 'addressee'], name='uq_connections_pair'),
            CheckConstraint(condition=~Q(requester=F('addressee')), name='ck_connections_not_self'),
            choices_constraint('status', ConnectionStatus, 'ck_connections_status'),
        ]

    def __str__(self):
        return f'{self.requester} -> {self.addressee} ({self.status})'

    def other(self, user):
        """Người còn lại của quan hệ, nhìn từ phía `user`."""
        return self.addressee if self.requester_id == user.pk else self.requester
