from .models import CandidateProfile


def get_candidate_profile(user) -> CandidateProfile | None:
    """Hồ sơ ứng viên của user, kèm tài khoản và tỉnh/thành (view dùng lại, không query thêm)."""
    if not user or not user.is_authenticated:
        return None
    return CandidateProfile.objects.select_related('user', 'location').filter(user=user).first()
