"""Các truy vấn đọc thư mời ứng tuyển. Thư của tin đã xóa (hoặc của công ty đã xóa) được ẩn."""
from django.db.models import Prefetch

from apps.jobs.models import JobSkill

from .models import Invitation, InvitationStatus


def _visible():
    return Invitation.objects.filter(job__deleted_at__isnull=True, job__company__deleted_at__isnull=True)


def company_invitations(company, *, status: str = '', job_id=None, search: str = ''):
    """Thư công ty đã gửi (của mọi nhà tuyển dụng trong công ty), mới gửi trước. `search`: tên ứng viên."""
    qs = _visible().filter(job__company=company).select_related(
        'job', 'candidate__user', 'candidate__location', 'sender__recruiter'
    )
    if status:
        qs = qs.filter(status=status)
    if job_id:
        qs = qs.filter(job_id=job_id)
    if search:
        qs = qs.filter(candidate__user__full_name__icontains=search)
    return qs


def candidate_invitations(candidate, *, status: str = ''):
    """Thư ứng viên nhận được, mới nhất trước, kèm thông tin tin tuyển dụng như danh sách việc làm công khai."""
    qs = (
        _visible()
        .filter(candidate=candidate)
        .select_related('job__company', 'job__location', 'job__industry', 'sender__recruiter')
        .prefetch_related(Prefetch('job__job_skills', queryset=JobSkill.objects.select_related('skill')))
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def unread_count(candidate) -> int:
    """Thư đang chờ phản hồi mà ứng viên chưa mở (huy hiệu trên menu)."""
    return _visible().filter(candidate=candidate, status=InvitationStatus.PENDING, read_at__isnull=True).count()


def invitation_map(company, candidate_ids, *, job=None) -> dict:
    """{id hồ sơ ứng viên: thư mới nhất công ty đã gửi cho ứng viên đó}; `job`: chỉ xét thư của tin này."""
    qs = company_invitations(company).filter(candidate_id__in=list(candidate_ids))
    if job is not None:
        qs = qs.filter(job=job)
    latest = {}
    for invitation in qs.order_by('created_at'):  # thư mới hơn ghi đè thư cũ
        latest[invitation.candidate_id] = invitation
    return latest
