"""Hồ sơ ứng viên.

Giai đoạn 1 (nhà tuyển dụng): thông tin để NTD xem ứng viên đã nộp đơn.
Giai đoạn 2 (ứng viên - CV): ứng viên tự đăng ký, cập nhật hồ sơ này qua /candidate/profile/.
Các bảng học vấn, kinh nghiệm, kỹ năng tự khai (xem database/schema.sql) bổ sung sau. Việc làm / công ty yêu thích: app favorites.
"""
from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q

from apps.catalog.choices import JobLevel, JobType, WorkMode
from common.models import TimeStampedModel, UUIDModel


class Gender(models.TextChoices):
    MALE = 'male', 'Nam'
    FEMALE = 'female', 'Nữ'
    OTHER = 'other', 'Khác'


class CandidateProfile(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile',
        verbose_name='tài khoản',
    )
    headline = models.CharField('tiêu đề hồ sơ', max_length=200, blank=True)
    date_of_birth = models.DateField('ngày sinh', null=True, blank=True)
    gender = models.CharField('giới tính', max_length=10, choices=Gender.choices, blank=True)
    address = models.CharField('địa chỉ', max_length=255, blank=True)
    location = models.ForeignKey(
        'catalog.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='tỉnh/thành phố',
    )
    summary = models.TextField('giới thiệu', blank=True)
    years_of_experience = models.DecimalField('số năm kinh nghiệm', max_digits=4, decimal_places=1, null=True, blank=True)
    current_level = models.CharField('cấp bậc hiện tại', max_length=20, choices=JobLevel.choices, blank=True)
    desired_position = models.CharField('vị trí mong muốn', max_length=150, blank=True)
    desired_salary_min = models.BigIntegerField('lương mong muốn từ', null=True, blank=True)
    desired_salary_max = models.BigIntegerField('lương mong muốn đến', null=True, blank=True)
    salary_currency = models.CharField('tiền tệ', max_length=3, default='VND')
    desired_job_type = models.CharField('hình thức mong muốn', max_length=20, choices=JobType.choices, blank=True)
    desired_work_mode = models.CharField('chế độ làm việc mong muốn', max_length=20, choices=WorkMode.choices, blank=True)
    is_open_to_work = models.BooleanField('đang tìm việc', default=True)
    is_public = models.BooleanField('cho phép NTD tìm thấy', default=False)

    class Meta:
        db_table = 'candidate_profiles'
        verbose_name = 'hồ sơ ứng viên'
        verbose_name_plural = 'hồ sơ ứng viên'
        constraints = [
            CheckConstraint(condition=Q(years_of_experience__gte=0), name='ck_candidate_years_non_negative'),
            CheckConstraint(
                condition=Q(desired_salary_max__isnull=True)
                | Q(desired_salary_min__isnull=True)
                | Q(desired_salary_max__gte=models.F('desired_salary_min')),
                name='ck_candidate_desired_salary_range',
            ),
        ]

    def __str__(self):
        return self.user.get_full_name()
