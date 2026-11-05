"""Truy vấn đọc của trang quản trị hệ thống (toàn bộ dữ liệu, không giới hạn theo công ty / ứng viên)."""
from django.db.models import Q

from apps.accounts.models import User, UserRole
from apps.applications.models import Application
from apps.employers.models import Company, VerificationStatus
from apps.jobs.models import Job, JobStatus

RECENT_LIMIT = 5  # số người dùng / doanh nghiệp mới nhất trên trang tổng quan
LIST_LIMIT = 100  # danh sách chưa phân trang: chỉ trả các mục mới nhất (kèm tổng số)


def overview() -> dict:
    """Số liệu toàn hệ thống và người dùng / doanh nghiệp mới nhất."""
    return {
        'total_users': User.objects.count(),
        'candidates_count': User.objects.filter(role=UserRole.CANDIDATE).count(),
        'employers_count': User.objects.filter(role=UserRole.EMPLOYER).count(),
        'total_companies': Company.objects.count(),
        'pending_companies': Company.objects.filter(verification_status=VerificationStatus.PENDING).count(),
        'total_jobs': Job.objects.count(),
        'published_jobs': Job.objects.filter(status=JobStatus.PUBLISHED).count(),
        'total_applications': Application.objects.count(),
        'recent_users': User.objects.order_by('-created_at')[:RECENT_LIMIT],
        'recent_companies': Company.objects.order_by('-created_at')[:RECENT_LIMIT],
    }


def users(*, role: str = '', search: str = ''):
    """Người dùng, mới nhất trước. `search`: email, họ tên hoặc số điện thoại."""
    qs = User.objects.order_by('-created_at')
    if role:
        qs = qs.filter(role=role)
    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(full_name__icontains=search) | Q(phone__icontains=search))
    return qs


def companies(*, verification_status: str = '', search: str = ''):
    """Doanh nghiệp (chưa xóa), mới nhất trước. `search`: tên doanh nghiệp."""
    qs = Company.objects.order_by('-created_at')
    if verification_status:
        qs = qs.filter(verification_status=verification_status)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs


def jobs(*, status: str = '', search: str = ''):
    """Tin tuyển dụng (chưa xóa) của mọi công ty, mới nhất trước. `status` là trạng thái lưu trong DB."""
    qs = Job.objects.select_related('company').order_by('-created_at')
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(title__icontains=search)
    return qs


def get_user(user_id) -> User | None:
    return User.objects.filter(pk=user_id).first()


def get_company(company_id) -> Company | None:
    return Company.objects.filter(pk=company_id).first()


def get_job(job_id) -> Job | None:
    return Job.objects.filter(pk=job_id).first()
