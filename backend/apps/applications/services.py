"""Nghiệp vụ hồ sơ ứng tuyển."""
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.jobs import workflow as job_workflow
from apps.jobs.models import Job
from common.exceptions import BusinessError
from common.utils import send_on_commit

from . import signals, workflow
from .models import Application, ApplicationStatus, ApplicationStatusHistory


@transaction.atomic
def submit_application(*, candidate, job: Job, cv, cover_letter: str = '') -> Application:
    """Ứng viên nộp hồ sơ vào một tin.

    Giai đoạn 1 chỉ được gọi từ lệnh `seed_demo`; API ứng viên ở giai đoạn sau sẽ gọi lại đúng hàm này
    nên mọi quy tắc (tin còn nhận hồ sơ, chống nộp trùng, đếm hồ sơ, lịch sử) nằm sẵn ở đây.
    """
    if not job_workflow.is_accepting_applications(job):
        raise BusinessError('Tin tuyển dụng không còn nhận hồ sơ.', code='job_not_accepting')
    if cv.candidate_id != candidate.id or cv.is_deleted:
        raise BusinessError('CV không hợp lệ.', code='invalid_cv')
    try:
        with transaction.atomic():
            application = Application.objects.create(
                job=job, candidate=candidate, cv=cv, cover_letter=cover_letter.strip()
            )
    except IntegrityError as exc:
        raise BusinessError('Bạn đã ứng tuyển công việc này.', code='duplicate_application', status_code=409) from exc

    ApplicationStatusHistory.objects.create(
        application=application, from_status=None, to_status=ApplicationStatus.APPLIED, changed_by=candidate.user
    )
    Job.all_objects.filter(pk=job.pk).update(application_count=F('application_count') + 1)
    send_on_commit(signals.application_submitted, sender=Application, application=application)
    return application


@transaction.atomic
def change_status(
    application: Application, *, to_status: str, by, note: str = '', rejection_reason: str = ''
) -> Application:
    """Chuyển hồ sơ sang bước tiếp theo của pipeline (kiểm tra state machine) và ghi lịch sử."""
    application = Application.objects.select_for_update().get(pk=application.pk)
    from_status = application.status
    if not workflow.can_transition(from_status, to_status):
        raise BusinessError(
            f'Không thể chuyển hồ sơ từ "{ApplicationStatus(from_status).label}" '
            f'sang "{ApplicationStatus(to_status).label}".',
            code='invalid_status_transition',
            status_code=409,
        )

    application.status = to_status
    application.status_changed_at = timezone.now()
    if to_status == ApplicationStatus.REJECTED:
        application.rejection_reason = rejection_reason.strip()
    elif from_status == ApplicationStatus.REJECTED:
        application.rejection_reason = ''  # mở lại hồ sơ: bỏ lý do từ chối cũ
    application.save(update_fields=['status', 'status_changed_at', 'rejection_reason', 'updated_at'])

    ApplicationStatusHistory.objects.create(
        application=application, from_status=from_status, to_status=to_status, changed_by=by, note=note.strip()
    )
    send_on_commit(
        signals.application_status_changed,
        sender=Application,
        application=application,
        from_status=from_status,
        to_status=to_status,
        changed_by=by,
    )
    return application


def rate_application(application: Application, *, rating: int | None) -> Application:
    application.recruiter_rating = rating
    application.save(update_fields=['recruiter_rating', 'updated_at'])
    return application
