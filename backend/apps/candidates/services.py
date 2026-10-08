"""Nghiệp vụ ứng viên: đăng ký, cập nhật hồ sơ."""
from django.db import transaction

from apps.accounts import services as account_services
from apps.accounts.models import UserRole

from .models import CandidateProfile


@transaction.atomic
def register_candidate(*, email: str, password: str, full_name: str, phone: str = '') -> CandidateProfile:
    """Tạo đồng thời User (role=candidate) + hồ sơ ứng viên rỗng."""
    user = account_services.create_user(
        email=email, password=password, role=UserRole.CANDIDATE, full_name=full_name, phone=phone
    )
    return CandidateProfile.objects.create(user=user)


@transaction.atomic
def update_candidate_profile(
    profile: CandidateProfile, *, data: dict, full_name: str | None = None, phone: str | None = None
) -> CandidateProfile:
    account_services.update_account(profile.user, full_name=full_name, phone=phone)
    changed = [field for field, value in data.items() if getattr(profile, field) != value]
    for field in changed:
        setattr(profile, field, data[field])
    if changed:
        profile.save(update_fields=[*changed, 'updated_at'])
    return profile
