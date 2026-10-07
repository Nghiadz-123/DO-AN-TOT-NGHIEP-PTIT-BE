"""Quy tắc trạng thái tin tuyển dụng.

    draft ──publish──▶ published ──pause──▶ paused ──publish──▶ published
                          │                   │
                          └──────close────────┴──▶ closed ──publish (mở lại)──▶ published

"expired" không lưu vào DB: tin `published` có deadline < hôm nay được coi là hết hạn.
Gia hạn deadline (sửa tin) là tin tự động "đang tuyển" trở lại.
"""
from django.db.models import Q
from django.utils import timezone

from .models import JobStatus

PUBLISH, PAUSE, CLOSE, DELETE = 'publish', 'pause', 'close', 'delete'

# hành động -> các trạng thái (hiệu lực) được phép thực hiện
ACTION_SOURCES = {
    PUBLISH: {JobStatus.DRAFT, JobStatus.PAUSED, JobStatus.CLOSED},
    PAUSE: {JobStatus.PUBLISHED},
    CLOSE: {JobStatus.PUBLISHED, JobStatus.PAUSED, JobStatus.EXPIRED},
}


def today():
    return timezone.localdate()


def effective_status(job) -> str:
    if job.status == JobStatus.PUBLISHED and job.deadline and job.deadline < today():
        return JobStatus.EXPIRED
    return job.status


def is_accepting_applications(job) -> bool:
    return not job.is_deleted and effective_status(job) == JobStatus.PUBLISHED


def can(action: str, job) -> bool:
    return effective_status(job) in ACTION_SOURCES[action]


def allowed_actions(job, *, has_applications: bool) -> list[str]:
    actions = [action for action in (PUBLISH, PAUSE, CLOSE) if can(action, job)]
    if not has_applications:
        actions.append(DELETE)
    return actions


def status_q(status: str) -> Q:
    """Điều kiện lọc theo trạng thái hiệu lực (dùng trong queryset)."""
    if status == JobStatus.EXPIRED:
        return Q(status=JobStatus.EXPIRED) | Q(status=JobStatus.PUBLISHED, deadline__lt=today())
    if status == JobStatus.PUBLISHED:
        return Q(status=JobStatus.PUBLISHED) & (Q(deadline__isnull=True) | Q(deadline__gte=today()))
    return Q(status=status)
