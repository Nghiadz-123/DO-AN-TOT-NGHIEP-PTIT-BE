"""Các truy vấn đọc tin tuyển dụng (lọc, annotate, tối ưu query)."""
from django.db.models import Count, Prefetch, Q

from . import workflow
from .models import Job, JobSkill, JobStatus

_SKILLS_PREFETCH = Prefetch('job_skills', queryset=JobSkill.objects.select_related('skill'))


def employer_jobs(company):
    """Tin của một công ty, kèm số hồ sơ. Đếm qua quan hệ ngược `applications` của app applications
    (chỉ dùng ORM, không import code của app đó); 'applied' = hồ sơ mới chưa xử lý."""
    return (
        Job.objects.filter(company=company)
        .select_related('company', 'location', 'industry', 'created_by')
        .prefetch_related(_SKILLS_PREFETCH)
        .annotate(
            applicant_count=Count('applications', distinct=True),
            new_applicant_count=Count('applications', filter=Q(applications__status='applied'), distinct=True),
        )
    )


def public_jobs():
    """Tin đang tuyển (đã đăng, chưa hết hạn) của công ty chưa bị xóa."""
    return (
        Job.objects.filter(workflow.status_q(JobStatus.PUBLISHED), company__deleted_at__isnull=True)
        .select_related('company', 'location')
        .prefetch_related(_SKILLS_PREFETCH)
    )


def public_job_detail_queryset():
    """Trang chi tiết công khai: mọi tin trừ bản nháp (tin đã đóng vẫn xem được, chỉ không nhận hồ sơ)."""
    return (
        Job.objects.exclude(status=JobStatus.DRAFT)
        .filter(company__deleted_at__isnull=True)
        .select_related('company', 'location', 'industry')
        .prefetch_related(_SKILLS_PREFETCH)
    )
