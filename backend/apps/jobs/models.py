from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, F, Q

from apps.catalog.choices import JobLevel, JobType, WorkMode
from common.models import SoftDeleteModel, TimeStampedModel, UUIDModel, choices_constraint


class JobStatus(models.TextChoices):
    DRAFT = 'draft', 'Bản nháp'
    PUBLISHED = 'published', 'Đang tuyển'
    PAUSED = 'paused', 'Tạm dừng'
    CLOSED = 'closed', 'Đã đóng'
    # Suy ra khi tin đang tuyển nhưng đã qua hạn nộp (xem jobs/workflow.py), không cần cron
    EXPIRED = 'expired', 'Hết hạn'


class SalaryCurrency(models.TextChoices):
    VND = 'VND', 'VND'
    USD = 'USD', 'USD'


class Job(UUIDModel, TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(
        'employers.Company', on_delete=models.PROTECT, related_name='jobs', verbose_name='công ty'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='người tạo',
    )
    title = models.CharField('tiêu đề', max_length=255)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField('mô tả công việc')
    requirements = models.TextField('yêu cầu ứng viên')
    benefits = models.TextField('quyền lợi', blank=True)
    job_type = models.CharField('hình thức', max_length=20, choices=JobType.choices)
    work_mode = models.CharField('chế độ làm việc', max_length=20, choices=WorkMode.choices, default=WorkMode.ONSITE)
    level = models.CharField('cấp bậc', max_length=20, choices=JobLevel.choices)
    min_years_experience = models.DecimalField('số năm kinh nghiệm tối thiểu', max_digits=4, decimal_places=1, default=0)
    salary_min = models.BigIntegerField('lương từ', null=True, blank=True)
    salary_max = models.BigIntegerField('lương đến', null=True, blank=True)
    salary_currency = models.CharField('tiền tệ', max_length=3, choices=SalaryCurrency.choices, default=SalaryCurrency.VND)
    is_salary_negotiable = models.BooleanField('lương thỏa thuận', default=False)
    headcount = models.PositiveSmallIntegerField('số lượng tuyển', default=1)
    location = models.ForeignKey(
        'catalog.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='tỉnh/thành phố',
    )
    address = models.CharField('địa chỉ làm việc', max_length=255, blank=True)
    industry = models.ForeignKey(
        'catalog.Industry', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='ngành nghề',
    )
    deadline = models.DateField('hạn nộp hồ sơ', null=True, blank=True)
    status = models.CharField('trạng thái', max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT)
    published_at = models.DateTimeField('đăng lúc', null=True, blank=True)
    closed_at = models.DateTimeField('đóng lúc', null=True, blank=True)
    view_count = models.PositiveIntegerField('lượt xem', default=0)
    # Denormalized để hiển thị nhanh; cập nhật trong applications.services.submit_application
    application_count = models.PositiveIntegerField('số hồ sơ', default=0)
    skills = models.ManyToManyField('catalog.Skill', through='JobSkill', related_name='jobs', verbose_name='kỹ năng')

    class Meta:
        db_table = 'jobs'
        verbose_name = 'tin tuyển dụng'
        verbose_name_plural = 'tin tuyển dụng'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at'], name='idx_jobs_company'),
            models.Index(
                fields=['-published_at'], name='idx_jobs_public_list',
                condition=Q(status='published', deleted_at__isnull=True),
            ),
            models.Index(
                fields=['location', 'level', 'job_type'], name='idx_jobs_filter',
                condition=Q(status='published', deleted_at__isnull=True),
            ),
        ]
        constraints = [
            choices_constraint('status', JobStatus, 'ck_jobs_status'),
            choices_constraint('job_type', JobType, 'ck_jobs_job_type'),
            choices_constraint('work_mode', WorkMode, 'ck_jobs_work_mode'),
            choices_constraint('level', JobLevel, 'ck_jobs_level'),
            CheckConstraint(condition=Q(salary_min__gte=0), name='ck_jobs_salary_min_non_negative'),
            CheckConstraint(
                condition=Q(salary_max__isnull=True) | Q(salary_min__isnull=True) | Q(salary_max__gte=F('salary_min')),
                name='ck_jobs_salary_range',
            ),
            CheckConstraint(condition=Q(headcount__gt=0), name='ck_jobs_headcount_positive'),
            CheckConstraint(condition=Q(min_years_experience__gte=0), name='ck_jobs_min_years_non_negative'),
        ]

    def __str__(self):
        return self.title


class JobSkill(models.Model):
    """Kỹ năng job yêu cầu: bắt buộc hay nice-to-have, trọng số dùng khi chấm điểm matching (giai đoạn AI)."""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_skills')
    skill = models.ForeignKey('catalog.Skill', on_delete=models.CASCADE, related_name='job_skills')
    is_required = models.BooleanField('bắt buộc', default=True)
    min_years = models.DecimalField('số năm tối thiểu', max_digits=4, decimal_places=1, null=True, blank=True)
    weight = models.PositiveSmallIntegerField('trọng số', default=3)

    class Meta:
        db_table = 'job_skills'
        verbose_name = 'kỹ năng yêu cầu'
        verbose_name_plural = 'kỹ năng yêu cầu'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['job', 'skill'], name='uq_job_skills_job_skill'),
            CheckConstraint(condition=Q(weight__gte=1, weight__lte=5), name='ck_job_skills_weight_range'),
        ]

    def __str__(self):
        return f'{self.job_id} - {self.skill}'
