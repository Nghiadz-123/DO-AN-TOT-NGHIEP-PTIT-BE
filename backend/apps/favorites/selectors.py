"""Truy vấn đọc danh sách yêu thích. Chỉ trả về tin / công ty còn hiển thị công khai."""
from django.db.models import Exists, OuterRef, Subquery

from apps.jobs import selectors as job_selectors

from .models import FavoriteCompany, FavoriteJob


def favorite_jobs(candidate):
    """Tin yêu thích (queryset Job, kèm `favorited_at`), mới thêm trước.

    Tin đã đóng / hết hạn vẫn giữ (frontend hiển thị trạng thái); tin đã xóa hoặc của công ty đã xóa thì ẩn.
    """
    favorites = FavoriteJob.objects.filter(candidate=candidate, job=OuterRef('pk'))
    return (
        job_selectors.public_job_detail_queryset()
        .filter(Exists(favorites))
        .annotate(favorited_at=Subquery(favorites.values('created_at')[:1]))
        .order_by('-favorited_at')
    )


def favorite_companies(candidate):
    """Công ty yêu thích (queryset Company kèm `open_job_count`, `favorited_at`), mới thêm trước."""
    favorites = FavoriteCompany.objects.filter(candidate=candidate, company=OuterRef('pk'))
    return (
        job_selectors.public_companies()
        .filter(Exists(favorites))
        .annotate(favorited_at=Subquery(favorites.values('created_at')[:1]))
        .order_by('-favorited_at')
    )


def favorite_ids(candidate) -> dict:
    """Id các tin / công ty đang yêu thích, để frontend đánh dấu nút yêu thích."""
    visible_jobs = job_selectors.public_job_detail_queryset()
    return {
        'jobs': list(
            FavoriteJob.objects.filter(candidate=candidate, job__in=visible_jobs).values_list('job_id', flat=True)
        ),
        'companies': list(
            FavoriteCompany.objects.filter(candidate=candidate, company__deleted_at__isnull=True)
            .values_list('company_id', flat=True)
        ),
    }
