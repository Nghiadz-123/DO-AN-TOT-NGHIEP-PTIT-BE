"""Thư mời ứng tuyển: nhà tuyển dụng mời một ứng viên nộp hồ sơ vào một tin đang tuyển của công ty.

Ứng viên đọc thư ở trang Thư mời, rồi nộp hồ sơ theo luồng ứng tuyển thường (app applications) hoặc từ chối.
Nộp hồ sơ vào tin được mời thì thư tự chuyển sang "đã ứng tuyển" (receivers.py nghe applications.signals).
Mỗi ứng viên nhận tối đa một thư cho mỗi tin; thư chưa được phản hồi thì nhà tuyển dụng thu hồi (xóa) được.
"""
from django.conf import settings
from django.db import models

from common.models import TimeStampedModel, UUIDModel, choices_constraint


class InvitationStatus(models.TextChoices):
    PENDING = 'pending', 'Chờ phản hồi'
    ACCEPTED = 'accepted', 'Đã ứng tuyển'
    DECLINED = 'declined', 'Đã từ chối'


class Invitation(UUIDModel, TimeStampedModel):
    """created_at = thời điểm gửi thư."""

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='+', verbose_name='tin tuyển dụng')
    candidate = models.ForeignKey(
        'candidates.CandidateProfile', on_delete=models.CASCADE, related_name='+', verbose_name='ứng viên'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='người gửi',
    )
    message = models.TextField('nội dung thư mời')
    status = models.CharField(
        'trạng thái', max_length=20, choices=InvitationStatus.choices, default=InvitationStatus.PENDING
    )
    read_at = models.DateTimeField('ứng viên đã xem lúc', null=True, blank=True)
    responded_at = models.DateTimeField('phản hồi lúc', null=True, blank=True)
    application = models.ForeignKey(
        'applications.Application', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='hồ sơ đã nộp',
    )

    class Meta:
        db_table = 'invitations'
        verbose_name = 'thư mời ứng tuyển'
        verbose_name_plural = 'thư mời ứng tuyển'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['candidate', '-created_at'], name='idx_invitations_candidate')]
        constraints = [
            models.UniqueConstraint(fields=['job', 'candidate'], name='uq_invitations_job_candidate'),
            choices_constraint('status', InvitationStatus, 'ck_invitations_status'),
        ]

    def __str__(self):
        return f'{self.job} -> {self.candidate}'
