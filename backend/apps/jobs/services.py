"""Nghiệp vụ tin tuyển dụng (các thao tác ghi). View chỉ validate input rồi gọi vào đây."""
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.catalog.services import resolve_skills
from common.exceptions import BusinessError
from common.utils import send_on_commit, unique_slug

from . import signals, workflow
from .models import Job, JobSkill, JobStatus

ACTION_LABELS = {workflow.PUBLISH: 'đăng', workflow.PAUSE: 'tạm dừng', workflow.CLOSE: 'đóng'}


@transaction.atomic
def create_job(*, company, created_by, data: dict, skills: list[dict] | None = None, publish: bool = False) -> Job:
    job = Job.objects.create(company=company, created_by=created_by, slug=unique_slug(data['title'], 300), **data)
    if skills:
        set_job_skills(job, skills)
    if publish:
        publish_job(job, by=created_by)
    return job


@transaction.atomic
def update_job(job: Job, *, data: dict, skills: list[dict] | None = None) -> Job:
    changed = [field for field, value in data.items() if getattr(job, field) != value]
    for field in changed:
        setattr(job, field, data[field])
    if changed:
        job.save()
    if skills is not None and set_job_skills(job, skills):
        changed.append('skills')
    if changed:
        send_on_commit(signals.job_updated, sender=Job, job=job, changed_fields=changed)
    return job


def set_job_skills(job: Job, skills: list[dict]) -> bool:
    """Thay toàn bộ kỹ năng yêu cầu theo đúng thứ tự nhập. Trả về True nếu có thay đổi."""
    desired = {}
    for item, skill in zip(skills, resolve_skills(item['name'] for item in skills)):
        if skill is not None and skill.id not in desired:
            desired[skill.id] = (item.get('is_required', True), item.get('weight', 3), item.get('min_years'))

    current = {js.skill_id: (js.is_required, js.weight, js.min_years) for js in job.job_skills.all()}
    if list(current.items()) == list(desired.items()):
        return False
    job.job_skills.all().delete()
    JobSkill.objects.bulk_create(
        JobSkill(job=job, skill_id=skill_id, is_required=required, weight=weight, min_years=min_years)
        for skill_id, (required, weight, min_years) in desired.items()
    )
    return True


@transaction.atomic
def publish_job(job: Job, *, by) -> Job:
    """Đăng tin (từ nháp), tiếp tục tuyển (từ tạm dừng) hoặc mở lại (từ đã đóng)."""
    _ensure_can(workflow.PUBLISH, job)
    _ensure_publishable(job)
    if job.status != JobStatus.PAUSED or job.published_at is None:
        job.published_at = timezone.now()  # đăng mới / mở lại: tin nổi lên đầu danh sách
    job.status = JobStatus.PUBLISHED
    job.closed_at = None
    job.save(update_fields=['status', 'published_at', 'closed_at', 'updated_at'])
    send_on_commit(signals.job_published, sender=Job, job=job)
    return job


@transaction.atomic
def pause_job(job: Job, *, by) -> Job:
    _ensure_can(workflow.PAUSE, job)
    job.status = JobStatus.PAUSED
    job.save(update_fields=['status', 'updated_at'])
    send_on_commit(signals.job_unpublished, sender=Job, job=job)
    return job


@transaction.atomic
def close_job(job: Job, *, by) -> Job:
    _ensure_can(workflow.CLOSE, job)
    job.status = JobStatus.CLOSED
    job.closed_at = timezone.now()
    job.save(update_fields=['status', 'closed_at', 'updated_at'])
    send_on_commit(signals.job_unpublished, sender=Job, job=job)
    return job


@transaction.atomic
def delete_job(job: Job, *, by) -> None:
    """Xóa mềm. Tin đã có hồ sơ ứng tuyển thì chỉ được đóng, để không mất dấu ứng viên."""
    if job.applications.exists():
        raise BusinessError(
            'Tin đã có hồ sơ ứng tuyển nên không thể xóa. Hãy đóng tin để ngừng nhận hồ sơ.',
            code='job_has_applications',
            status_code=409,
        )
    job.soft_delete()
    send_on_commit(signals.job_deleted, sender=Job, job=job)


def record_view(job: Job) -> None:
    Job.all_objects.filter(pk=job.pk).update(view_count=F('view_count') + 1)


def _ensure_can(action: str, job: Job) -> None:
    if not workflow.can(action, job):
        current = JobStatus(workflow.effective_status(job)).label
        raise BusinessError(
            f'Không thể {ACTION_LABELS[action]} tin đang ở trạng thái "{current}".',
            code='invalid_status_transition',
            status_code=409,
        )


def _ensure_publishable(job: Job) -> None:
    if job.deadline and job.deadline < workflow.today():
        raise BusinessError('Hạn nộp hồ sơ đã qua. Vui lòng cập nhật hạn nộp trước khi đăng tin.', code='deadline_passed')
    if not JobSkill.objects.filter(job=job).exists():  # không dùng job.job_skills: có thể là cache prefetch
        raise BusinessError('Cần ít nhất một kỹ năng yêu cầu trước khi đăng tin.', code='skills_required')
    if settings.EMPLOYER_REQUIRE_VERIFIED_COMPANY and not job.company.is_verified:
        raise BusinessError(
            'Công ty chưa được xác minh nên chưa thể đăng tin. Vui lòng chờ quản trị viên xác minh.',
            code='company_not_verified',
            status_code=403,
        )
