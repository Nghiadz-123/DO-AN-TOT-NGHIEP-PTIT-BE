"""Nghiệp vụ tài khoản: tạo user, cấp/thu hồi token, đổi mật khẩu.

Service ném django.core.exceptions.ValidationError; exception handler chung đổi sang response 400.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


def create_user(*, email: str, password: str | None, role: str, full_name: str = '', phone: str = '') -> User:
    email = User.objects.normalize_email_address(email)
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError({'email': 'Email đã được sử dụng.'})
    return User.objects.create_user(
        email=email, password=password, role=role, full_name=full_name.strip(), phone=phone.strip()
    )


def issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


def update_account(user: User, *, full_name: str | None = None, phone: str | None = None) -> User:
    fields = []
    if full_name is not None:
        user.full_name = full_name.strip()
        fields.append('full_name')
    if phone is not None:
        user.phone = phone.strip()
        fields.append('phone')
    if fields:
        user.save(update_fields=[*fields, 'updated_at'])
    return user


@transaction.atomic
def change_password(user: User, *, current_password: str, new_password: str) -> dict:
    """Đổi mật khẩu, thu hồi mọi phiên cũ và cấp token mới cho phiên hiện tại."""
    if not user.check_password(current_password):
        raise ValidationError({'current_password': 'Mật khẩu hiện tại không đúng.'})
    user.set_password(new_password)
    user.save(update_fields=['password', 'updated_at'])
    revoke_all_tokens(user)
    return issue_tokens(user)


def revoke_all_tokens(user: User) -> None:
    for token in OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True):
        BlacklistedToken.objects.get_or_create(token=token)


def logout(refresh_token: str) -> None:
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError as exc:
        raise ValidationError({'refresh': 'Refresh token không hợp lệ hoặc đã hết hạn.'}) from exc
