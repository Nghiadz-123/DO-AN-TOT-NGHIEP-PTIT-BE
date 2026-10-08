import uuid
from pathlib import Path

from django.conf import settings
from django.db import models

from common.models import SoftDeleteModel, TimeStampedModel, UUIDModel, choices_constraint
from common.validators import phone_validator, tax_code_validator


class CompanySize(models.TextChoices):
    XS = '1-10', '1 - 10 nhân viên'
    S = '11-50', '11 - 50 nhân viên'
    M = '51-200', '51 - 200 nhân viên'
    L = '201-500', '201 - 500 nhân viên'
    XL = '501-1000', '501 - 1000 nhân viên'
    XXL = '1000+', 'Trên 1000 nhân viên'


class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Chờ xác minh'
    VERIFIED = 'verified', 'Đã xác minh'
    REJECTED = 'rejected', 'Bị từ chối'


def company_logo_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f'companies/{instance.id}/logo-{uuid.uuid4().hex[:8]}{ext}'


class Company(UUIDModel, TimeStampedModel, SoftDeleteModel):
    name = models.CharField('tên công ty', max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    tax_code = models.CharField(
        'mã số thuế', max_length=20, unique=True, null=True, blank=True, validators=[tax_code_validator]
    )
    logo = models.ImageField('logo', upload_to=company_logo_path, max_length=500, blank=True)
    website = models.URLField('website', max_length=255, blank=True)
    email = models.EmailField('email liên hệ', blank=True)
    phone = models.CharField('điện thoại', max_length=20, blank=True, validators=[phone_validator])
    address = models.CharField('địa chỉ', max_length=255, blank=True)
    location = models.ForeignKey(
        'catalog.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='tỉnh/thành phố',
    )
    industry = models.ForeignKey(
        'catalog.Industry', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='ngành nghề',
    )
    company_size = models.CharField('quy mô', max_length=20, choices=CompanySize.choices, blank=True)
    founded_year = models.PositiveSmallIntegerField('năm thành lập', null=True, blank=True)
    description = models.TextField('giới thiệu', blank=True)
    verification_status = models.CharField(
        'trạng thái xác minh', max_length=20, choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    verified_at = models.DateTimeField('xác minh lúc', null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='admin xác minh',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        verbose_name='người tạo',
    )

    class Meta:
        db_table = 'companies'
        verbose_name = 'công ty'
        verbose_name_plural = 'công ty'
        ordering = ['-created_at']
        constraints = [
            choices_constraint('verification_status', VerificationStatus, 'ck_companies_verification_status'),
        ]

    def __str__(self):
        return self.name

    @property
    def is_verified(self):
        return self.verification_status == VerificationStatus.VERIFIED


class CompanyRole(models.TextChoices):
    OWNER = 'owner', 'Chủ sở hữu'
    ADMIN = 'admin', 'Quản trị'
    MEMBER = 'member', 'Thành viên'


class RecruiterStatus(models.TextChoices):
    PENDING = 'pending', 'Chờ duyệt'
    ACTIVE = 'active', 'Đang hoạt động'
    REMOVED = 'removed', 'Đã rời công ty'


class Recruiter(UUIDModel, TimeStampedModel):
    """Nhà tuyển dụng = User (role=employer) thuộc về một Company."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter', verbose_name='tài khoản'
    )
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name='recruiters', verbose_name='công ty'
    )
    position = models.CharField('chức danh', max_length=100, blank=True)
    company_role = models.CharField(
        'vai trò trong công ty', max_length=20, choices=CompanyRole.choices, default=CompanyRole.MEMBER
    )
    status = models.CharField(
        'trạng thái', max_length=20, choices=RecruiterStatus.choices, default=RecruiterStatus.PENDING
    )
    joined_at = models.DateTimeField('tham gia lúc', null=True, blank=True)

    class Meta:
        db_table = 'recruiters'
        verbose_name = 'nhà tuyển dụng'
        verbose_name_plural = 'nhà tuyển dụng'
        constraints = [
            choices_constraint('company_role', CompanyRole, 'ck_recruiters_company_role'),
            choices_constraint('status', RecruiterStatus, 'ck_recruiters_status'),
        ]

    def __str__(self):
        return f'{self.user} @ {self.company}'

    @property
    def can_manage_company(self):
        return self.company_role in (CompanyRole.OWNER, CompanyRole.ADMIN)
