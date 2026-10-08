from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone

from common.models import TimeStampedModel, UUIDModel, choices_constraint


class ApplicationStatus(models.TextChoices):
    APPLIED = 'applied', 'Mới ứng tuyển'
    SCREENING = 'screening', 'Đang sàng lọc'
    INTERVIEW = 'interview', 'Phỏng vấn'
    OFFER = 'offer', 'Đề nghị nhận việc'
    HIRED = 'hired', 'Đã tuyển'
    REJECTED = 'rejected', 'Từ chối'
    WITHDRAWN = 'withdrawn', 'Ứng viên đã rút'


class Application(UUIDModel, TimeStampedModel):
    """Đơn ứng tuyển. created_at = thời điểm nộp."""

    job = models.ForeignKey('jobs.Job', on_delete=models.PROTECT, related_name='applications', verbose_name='tin tuyển dụng')
    candidate = models.ForeignKey(
        'candidates.CandidateProfile', on_delete=models.CASCADE, related_name='applications', verbose_name='ứng viên'
    )
    cv = models.ForeignKey('cvs.CV', on_delete=models.PROTECT, related_name='applications', verbose_name='CV đã nộp')
    cover_letter = models.TextField('thư giới thiệu', blank=True)
    status = models.CharField(
        'trạng thái', max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED
    )
    rejection_reason = models.TextField('lý do từ chối', blank=True)
    recruiter_rating = models.PositiveSmallIntegerField('đánh giá của NTD (1-5)', null=True, blank=True)
    status_changed_at = models.DateTimeField('đổi trạng thái lúc', default=timezone.now)

    class Meta:
        db_table = 'applications'
        verbose_name = 'hồ sơ ứng tuyển'
        verbose_name_plural = 'hồ sơ ứng tuyển'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', 'status'], name='idx_applications_job_status'),
            models.Index(fields=['candidate', '-created_at'], name='idx_applications_candidate'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['job', 'candidate'], name='uq_applications_job_candidate'),
            choices_constraint('status', ApplicationStatus, 'ck_applications_status'),
            CheckConstraint(
                condition=Q(recruiter_rating__isnull=True) | Q(recruiter_rating__gte=1, recruiter_rating__lte=5),
                name='ck_applications_rating_range',
            ),
        ]

    def __str__(self):
        return f'{self.candidate} -> {self.job}'


class ApplicationStatusHistory(models.Model):
    """Mỗi lần đổi trạng thái ghi một dòng: dùng cho timeline và thống kê thời gian tuyển."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField('từ trạng thái', max_length=20, null=True, blank=True)  # NULL ở bản ghi đầu
    to_status = models.CharField('sang trạng thái', max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='người thay đổi',
    )
    note = models.TextField('ghi chú', blank=True)
    created_at = models.DateTimeField('thời điểm', default=timezone.now)

    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'lịch sử trạng thái'
        verbose_name_plural = 'lịch sử trạng thái'
        ordering = ['created_at', 'id']
        indexes = [models.Index(fields=['application', 'created_at'], name='idx_app_history_app')]

    def __str__(self):
        return f'{self.from_status or "-"} -> {self.to_status}'
