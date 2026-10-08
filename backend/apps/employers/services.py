"""Nghiệp vụ nhà tuyển dụng: đăng ký, hồ sơ công ty, hồ sơ recruiter, xác minh công ty."""
from django.db import transaction
from django.utils import timezone

from apps.accounts import services as account_services
from apps.accounts.models import UserRole

from common.utils import unique_slug

from .models import Company, CompanyRole, Recruiter, RecruiterStatus, VerificationStatus

# Đổi các trường này sau khi đã xác minh thì công ty phải được xác minh lại
VERIFICATION_SENSITIVE_FIELDS = ('name', 'tax_code')


@transaction.atomic
def register_employer(
    *, email: str, password: str, full_name: str, company_name: str, phone: str = '', position: str = ''
) -> Recruiter:
    """Tạo đồng thời User (role=employer) + Company + Recruiter (owner, active)."""
    user = account_services.create_user(
        email=email, password=password, role=UserRole.EMPLOYER, full_name=full_name, phone=phone
    )
    company_name = company_name.strip()
    company = Company.objects.create(name=company_name, slug=unique_slug(company_name, 280), created_by=user)
    return Recruiter.objects.create(
        user=user,
        company=company,
        position=position.strip(),
        company_role=CompanyRole.OWNER,
        status=RecruiterStatus.ACTIVE,
        joined_at=timezone.now(),
    )


@transaction.atomic
def update_recruiter_profile(
    recruiter: Recruiter, *, full_name: str | None = None, phone: str | None = None, position: str | None = None
) -> Recruiter:
    account_services.update_account(recruiter.user, full_name=full_name, phone=phone)
    if position is not None:
        recruiter.position = position.strip()
        recruiter.save(update_fields=['position', 'updated_at'])
    return recruiter


@transaction.atomic
def update_company(company: Company, *, data: dict) -> Company:
    needs_reverify = company.verification_status == VerificationStatus.VERIFIED and any(
        field in data and data[field] != getattr(company, field) for field in VERIFICATION_SENSITIVE_FIELDS
    )
    for field, value in data.items():
        setattr(company, field, value)
    if needs_reverify:
        company.verification_status = VerificationStatus.PENDING
        company.verified_at = None
        company.verified_by = None
    company.save()
    return company


def set_company_logo(company: Company, logo) -> Company:
    old_name = company.logo.name if company.logo else None
    company.logo = logo
    company.save(update_fields=['logo', 'updated_at'])
    if old_name and old_name != company.logo.name:
        company.logo.storage.delete(old_name)
    return company


def remove_company_logo(company: Company) -> Company:
    if company.logo:
        company.logo.delete(save=False)
        company.save(update_fields=['logo', 'updated_at'])
    return company


def set_verification(company: Company, *, status: str, by) -> Company:
    """Admin xác minh / từ chối công ty (gọi từ Django Admin)."""
    company.verification_status = status
    company.verified_at = timezone.now() if status == VerificationStatus.VERIFIED else None
    company.verified_by = by
    company.save(update_fields=['verification_status', 'verified_at', 'verified_by', 'updated_at'])
    return company
