from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    """Chỉ cho phép user đã đăng nhập có đúng vai trò `role`.

    Các app khai báo lớp con với role cụ thể (vd. employers.permissions.IsEmployer),
    nhờ vậy `common` không phải import từ `apps`.
    """

    role = None
    message = 'Bạn không có quyền thực hiện thao tác này.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'role', None) == self.role)
