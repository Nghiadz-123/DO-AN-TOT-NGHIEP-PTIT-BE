"""Điểm mở rộng theo vai trò.

`accounts` là module nền tảng nên không import ngược các app nghiệp vụ. App của từng vai trò
(employers, sau này candidates) tự đăng ký hàm trả về thông tin hồ sơ trong AppConfig.ready().
Thông tin này được gắn vào trường `profile` của /auth/me/ và response đăng nhập.
"""
from collections.abc import Callable

_profile_providers: dict[str, Callable] = {}


def register_profile_provider(role: str, provider: Callable) -> None:
    _profile_providers[role] = provider


def get_profile(user, request=None) -> dict | None:
    provider = _profile_providers.get(user.role)
    return provider(user, request=request) if provider else None
