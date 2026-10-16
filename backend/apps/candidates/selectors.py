from django.db.models import Q

from .models import CandidateProfile


def get_candidate_profile(user) -> CandidateProfile | None:
    """Hồ sơ ứng viên của user, kèm tài khoản và tỉnh/thành (view dùng lại, không query thêm)."""
    if not user or not user.is_authenticated:
        return None
    return CandidateProfile.objects.select_related('user', 'location').filter(user=user).first()


def _active():
    return CandidateProfile.objects.filter(user__is_active=True, user__deleted_at__isnull=True)


def public_candidates():
    """Ứng viên bật "công khai CV" (is_public): mọi nhà tuyển dụng tìm thấy và xem được CV chính."""
    return _active().filter(is_public=True)


def discoverable_candidates(company):
    """Ứng viên mà nhà tuyển dụng của `company` được tìm thấy, xem CV chính và gửi thư mời:
    ứng viên công khai CV (is_public) hoặc đã ứng tuyển vào một tin của công ty.

    Lọc qua quan hệ ngược `applications` (chỉ dùng ORM, không import code của app applications).
    """
    applied = CandidateProfile.objects.filter(applications__job__company=company).values('pk')
    return _active().filter(Q(is_public=True) | Q(pk__in=applied))
