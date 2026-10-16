"""Truy vấn đọc kết quả AI."""
from .models import CVAnalysis


def candidate_analyses(candidate):
    """Kết quả AI của các CV (chưa xóa) của ứng viên."""
    return CVAnalysis.objects.filter(cv__candidate=candidate, cv__deleted_at__isnull=True).order_by('-updated_at')
