"""Các truy vấn đọc tin tuyển dụng (lọc, annotate, tối ưu query)."""
from django.db.models import Count, Prefetch, Q

from apps.employers.models import Company

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
        .select_related('company', 'location', 'industry')
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


def public_companies():
    """Danh bạ công ty công khai (chưa bị xóa), kèm số tin đang tuyển.

    Đặt ở jobs thay vì employers vì cần quy tắc "đang tuyển" của tin (jobs phụ thuộc employers, không ngược lại).
    """
    open_jobs = workflow.status_q(JobStatus.PUBLISHED, prefix='jobs__') & Q(jobs__deleted_at__isnull=True)
    return Company.objects.select_related('location', 'industry').annotate(
        open_job_count=Count('jobs', filter=open_jobs, distinct=True)
    )
