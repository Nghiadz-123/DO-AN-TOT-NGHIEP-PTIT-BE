from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from common.models import UUIDModel, choices_constraint
from common.validators import phone_validator

from .managers import UserManager


class UserRole(models.TextChoices):
    CANDIDATE = 'candidate', 'Ứng viên'
    EMPLOYER = 'employer', 'Nhà tuyển dụng'
    ADMIN = 'admin', 'Quản trị viên'


class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    """Đăng nhập bằng email. Hồ sơ theo vai trò nằm ở app tương ứng (employers.Recruiter, ...)."""

    email = models.EmailField('email', max_length=254, unique=True)
    full_name = models.CharField('họ tên', max_length=150, blank=True)
    phone = models.CharField('số điện thoại', max_length=20, blank=True, validators=[phone_validator])
    role = models.CharField('vai trò', max_length=20, choices=UserRole.choices)
    is_active = models.BooleanField('đang hoạt động', default=True)
    is_staff = models.BooleanField('quyền vào trang quản trị', default=False)
    email_verified_at = models.DateTimeField('xác thực email lúc', null=True, blank=True)
    created_at = models.DateTimeField('ngày tạo', default=timezone.now, editable=False)
    updated_at = models.DateTimeField('ngày cập nhật', auto_now=True)
    deleted_at = models.DateTimeField('ngày xóa', null=True, blank=True, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'người dùng'
        verbose_name_plural = 'người dùng'
        ordering = ['-created_at']
        constraints = [choices_constraint('role', UserRole, 'ck_users_role')]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name or self.email

    def get_short_name(self):
        return self.get_full_name()

    @property
    def is_employer(self):
        return self.role == UserRole.EMPLOYER
