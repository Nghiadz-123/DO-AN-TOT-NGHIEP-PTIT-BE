from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Tạo user bằng email; email luôn được lưu dạng chữ thường."""

    use_in_migrations = True

    @staticmethod
    def normalize_email_address(email):
        return (email or '').strip().lower()

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email là bắt buộc.')
        user = self.model(email=self.normalize_email_address(email), **extra_fields)
        user.set_password(password)  # password=None -> mật khẩu không dùng được (không đăng nhập)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if not extra_fields.get('role'):
            raise ValueError('Vai trò (role) là bắt buộc.')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_staff=True và is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=self.normalize_email_address(email))
