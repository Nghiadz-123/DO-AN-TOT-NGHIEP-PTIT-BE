from functools import cached_property

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import UserRole
from common.permissions import RolePermission

from .selectors import get_active_recruiter


class IsEmployer(RolePermission):
    """User role=employer, có Recruiter đang hoạt động thuộc một công ty chưa bị xóa.

    Gắn recruiter vào request.recruiter để view dùng lại, không query lần nữa.
    """

    role = UserRole.EMPLOYER
    message = 'Chức năng này chỉ dành cho nhà tuyển dụng.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        recruiter = get_active_recruiter(request.user)
        if recruiter is None:
            self.message = 'Tài khoản nhà tuyển dụng chưa được kích hoạt hoặc chưa thuộc công ty nào.'
            return False
        request.recruiter = recruiter
        return True


class CanManageCompany(BasePermission):
    """Chỉ owner/admin của công ty được sửa hồ sơ công ty; mọi recruiter đều xem được."""

    message = 'Chỉ chủ sở hữu hoặc quản trị viên công ty được chỉnh sửa hồ sơ công ty.'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.recruiter.can_manage_company


class EmployerAccessMixin:
    """Mixin cho view của nhà tuyển dụng: mọi truy vấn phải giới hạn theo `self.company`.

    Đối tượng của công ty khác trả về 404 (không lộ sự tồn tại), không phải 403.
    """

    permission_classes = [IsEmployer]

    @cached_property
    def recruiter(self):
        return self.request.recruiter

    @property
    def company(self):
        return self.recruiter.company
