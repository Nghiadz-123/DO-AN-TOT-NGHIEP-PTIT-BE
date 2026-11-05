"""Thao tác ghi của trang quản trị hệ thống: khóa tài khoản, xác minh doanh nghiệp, đổi trạng thái tin."""
from apps.accounts.models import User
from apps.employers.models import Company
from apps.jobs.models import Job


def update_user(user: User, *, is_active: bool | None = None, role: str | None = None) -> User:
    """Khóa / mở khóa tài khoản (`is_active`) và đổi vai trò (`role`); tham số None thì giữ nguyên."""
    fields = []
    if is_active is not None:
        user.is_active = is_active
        fields.append('is_active')
    if role is not None:
        user.role = role
        fields.append('role')
    if fields:
        user.save(update_fields=[*fields, 'updated_at'])
    return user


def set_company_verification(company: Company, verification_status: str) -> Company:
    company.verification_status = verification_status
    company.save(update_fields=['verification_status', 'updated_at'])
    return company


def set_job_status(job: Job, status: str) -> Job:
    """Ghi thẳng trạng thái tin. Không đi qua jobs.services (publish/pause/close) nên không cập nhật
    published_at / closed_at và không phát signal của tin."""
    job.status = status
    job.save(update_fields=['status', 'updated_at'])
    return job
