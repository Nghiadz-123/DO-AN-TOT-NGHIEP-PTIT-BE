from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsCandidateOrEmployer(BasePermission):
    """Kết bạn và nhắn tin dành cho ứng viên và nhà tuyển dụng (không gồm admin)."""

    message = 'Chức năng này dành cho ứng viên và nhà tuyển dụng.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, 'role', None) in (UserRole.CANDIDATE, UserRole.EMPLOYER)
        )
