from datetime import timedelta

from django.db.models import Count, F, Prefetch, Q
from django.utils import timezone

from apps.jobs import workflow as job_workflow
from apps.jobs.models import Job, JobStatus

from .models import Application, ApplicationStatus, ApplicationStatusHistory

RECENT_APPLICATIONS_LIMIT = 6


def employer_applications(company):
    """Hồ sơ nộp vào các tin (chưa xóa) của một công ty. `applied_at` = created_at (tên trường trong API)."""
    return (
        Application.objects.filter(job__company=company, job__deleted_at__isnull=True)
        .select_related('job', 'cv', 'candidate__user', 'candidate__location')
        .annotate(applied_at=F('created_at'))
    )


def employer_application_detail_queryset(company):
    return employer_applications(company).prefetch_related(
        Prefetch('status_history', queryset=ApplicationStatusHistory.objects.select_related('changed_by'))
    )


def candidate_applications(candidate):
    """Hồ sơ một ứng viên đã nộp, gồm cả hồ sơ vào tin đã đóng (vẫn hiển thị để ứng viên theo dõi)."""
    return (
        Application.objects.filter(candidate=candidate)
        .select_related('job__company', 'job__location', 'cv')
        .annotate(applied_at=F('created_at'))
    )


def candidate_application_detail_queryset(candidate):
    return candidate_applications(candidate).prefetch_related('status_history')


def employer_dashboard(company) -> dict:
    job_stats = Job.objects.filter(company=company).aggregate(
        total=Count('id'),
        **{status: Count('id', filter=job_workflow.status_q(status)) for status in JobStatus.values},
    )

    applications = employer_applications(company)
    week_ago = timezone.now() - timedelta(days=7)
    application_stats = applications.aggregate(
        total=Count('id'),
        new_last_7_days=Count('id', filter=Q(created_at__gte=week_ago)),
        **{status: Count('id', filter=Q(status=status)) for status in ApplicationStatus.values},
    )

    return {
        'jobs': job_stats,
        'applications': application_stats,
        'recent_applications': applications.order_by('-applied_at')[:RECENT_APPLICATIONS_LIMIT],
    }
