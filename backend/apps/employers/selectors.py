from .models import Recruiter, RecruiterStatus


def get_active_recruiter(user) -> Recruiter | None:
    """Recruiter đang hoạt động của user, kèm công ty chưa bị xóa."""
    if not user or not user.is_authenticated:
        return None
    return (
        Recruiter.objects.select_related('company', 'company__location', 'company__industry', 'user')
        .filter(user=user, status=RecruiterStatus.ACTIVE, company__deleted_at__isnull=True)
        .first()
    )
