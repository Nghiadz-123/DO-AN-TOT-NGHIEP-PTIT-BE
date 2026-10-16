"""Nghiệp vụ thư mời ứng tuyển: gửi, thu hồi, ứng viên xem / từ chối, chuyển "đã ứng tuyển" khi nộp hồ sơ.

Quy tắc:
- Chỉ nhà tuyển dụng (recruiter đang hoạt động) gửi thư, cho tin đang nhận hồ sơ của công ty mình, tới ứng viên
  mà công ty được phép thấy (candidates.selectors.discoverable_candidates: công khai CV hoặc đã ứng tuyển vào công ty).
- Mỗi ứng viên một thư cho mỗi tin; ứng viên đã nộp hồ sơ vào tin thì không mời nữa.
- Nhà tuyển dụng của công ty thu hồi được thư đang chờ phản hồi; ứng viên từ chối được thư đang chờ phản hồi.
"""
from django.db import IntegrityError, transaction
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.applications.models import Application
from apps.candidates import selectors as candidate_selectors
from apps.jobs import workflow as job_workflow
from common.exceptions import BusinessError

from .models import Invitation, InvitationStatus

MESSAGE_MAX_LENGTH = 2000


@transaction.atomic
def send_invitation(*, recruiter, candidate, job, message: str) -> Invitation:
    """Nhà tuyển dụng `recruiter` mời ứng viên `candidate` (CandidateProfile) ứng tuyển vào tin `job`."""
    company = recruiter.company
    if job.company_id != company.pk:
        raise BusinessError('Tin tuyển dụng không tồn tại.', code='job_not_found', status_code=404)
    if not job_workflow.is_accepting_applications(job):
        raise BusinessError('Chỉ gửi được thư mời cho tin đang tuyển.', code='job_not_accepting')
    if not candidate_selectors.discoverable_candidates(company).filter(pk=candidate.pk).exists():
        # Không phân biệt "không tồn tại" và "không được phép thấy" để không lộ hồ sơ riêng tư
        raise BusinessError('Không tìm thấy ứng viên.', code='candidate_not_found', status_code=404)
    if Application.objects.filter(job=job, candidate=candidate).exists():
        raise BusinessError('Ứng viên đã ứng tuyển vào tin này.', code='already_applied', status_code=409)
    try:
        with transaction.atomic():
            return Invitation.objects.create(job=job, candidate=candidate, sender=recruiter.user, message=message.strip())
    except IntegrityError as exc:  # đã có thư cho tin này (kể cả hai request gửi cùng lúc)
        raise BusinessError(
            'Công ty đã gửi thư mời ứng viên này cho tin này.', code='already_invited', status_code=409
        ) from exc


@transaction.atomic
def withdraw_invitation(invitation: Invitation) -> None:
    """Thu hồi thư đang chờ phản hồi (xóa hẳn, nên có thể mời lại)."""
    invitation = _lock_pending(invitation, 'thu hồi')
    invitation.delete()


def mark_read(invitation: Invitation) -> Invitation:
    """Ứng viên mở thư; chỉ ghi nhận lần đầu."""
    if invitation.read_at is None:
        invitation.read_at = timezone.now()
        invitation.save(update_fields=['read_at', 'updated_at'])
    return invitation


@transaction.atomic
def decline_invitation(invitation: Invitation) -> Invitation:
    invitation = _lock_pending(invitation, 'từ chối')
    now = timezone.now()
    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = now
    invitation.read_at = invitation.read_at or now
    invitation.save(update_fields=['status', 'responded_at', 'read_at', 'updated_at'])
    return invitation


def mark_applied(application) -> int:
    """Ứng viên nộp hồ sơ vào tin được mời: thư (đang chờ hoặc đã từ chối) chuyển sang đã ứng tuyển.

    Gọi từ receivers khi có hồ sơ mới; gọi lại không sao (thư đã chuyển thì bỏ qua). Trả về số thư được cập nhật.
    """
    now = timezone.now()
    return (
        Invitation.objects.filter(job_id=application.job_id, candidate_id=application.candidate_id)
        .exclude(status=InvitationStatus.ACCEPTED)
        .update(
            status=InvitationStatus.ACCEPTED, application=application, responded_at=now,
            read_at=Coalesce('read_at', Value(now)), updated_at=now,
        )
    )


def _lock_pending(invitation: Invitation, action: str) -> Invitation:
    invitation = Invitation.objects.select_for_update().get(pk=invitation.pk)
    if invitation.status != InvitationStatus.PENDING:
        raise BusinessError(
            f'Không thể {action} thư mời ở trạng thái "{InvitationStatus(invitation.status).label}".',
            code='invalid_invitation_action',
            status_code=409,
        )
    return invitation
