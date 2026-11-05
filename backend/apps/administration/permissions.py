from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsSystemAdmin(BasePermission):
    """Admin hệ thống: user role=admin hoặc có quyền vào Django Admin (is_staff)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.role == UserRole.ADMIN))
