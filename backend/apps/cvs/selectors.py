"""Các truy vấn đọc CV."""
from django.db.models import Count

from .models import CV, CVBuilderDocument


def candidate_cvs(candidate):
    """CV (chưa xóa) của một ứng viên, kèm số lần đã dùng để ứng tuyển.

    Đếm qua quan hệ ngược `applications` của app applications (chỉ dùng ORM, không import code của app đó).
    """
    return CV.objects.filter(candidate=candidate).annotate(application_count=Count('applications'))


def get_candidate_cv(candidate, cv_id) -> CV | None:
    return CV.objects.filter(candidate=candidate, pk=cv_id).first()


def get_default_cv(candidate) -> CV | None:
    return CV.objects.filter(candidate=candidate, is_default=True).first()


def get_builder_document(candidate) -> CVBuilderDocument | None:
    """Nội dung CV tự tạo (trang Tạo CV) của ứng viên; None nếu chưa lưu lần nào."""
    return CVBuilderDocument.objects.filter(candidate=candidate).first()
