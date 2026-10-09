from functools import cached_property

from apps.accounts.models import UserRole
from common.permissions import RolePermission

from .selectors import get_candidate_profile


class IsCandidate(RolePermission):
    """User role=candidate và đã có hồ sơ ứng viên.

    Gắn hồ sơ vào request.candidate để view dùng lại, không query lần nữa.
    """

    role = UserRole.CANDIDATE
    message = 'Chức năng này chỉ dành cho ứng viên.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        candidate = get_candidate_profile(request.user)
        if candidate is None:
            self.message = 'Tài khoản ứng viên chưa có hồ sơ. Vui lòng liên hệ quản trị viên.'
            return False
        request.candidate = candidate
        return True


class CandidateAccessMixin:
    """Mixin cho view của ứng viên: mọi truy vấn phải giới hạn theo `self.candidate`.

    Dữ liệu của ứng viên khác trả về 404 (không lộ sự tồn tại), không phải 403.
    """

    permission_classes = [IsCandidate]

    @cached_property
    def candidate(self):
        return self.request.candidate
