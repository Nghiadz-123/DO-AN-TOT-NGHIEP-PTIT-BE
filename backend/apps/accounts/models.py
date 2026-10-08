from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    CANDIDATE = 'candidate'
    RECRUITER = 'recruiter'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (CANDIDATE, 'Ứng viên'),
        (RECRUITER, 'Nhà tuyển dụng'),
        (ADMIN, 'Quản trị viên'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=150, verbose_name='Họ và tên')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CANDIDATE, verbose_name='Vai trò')
    company_name = models.CharField(max_length=200, blank=True, default='', verbose_name='Tên công ty')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='Số điện thoại')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'
