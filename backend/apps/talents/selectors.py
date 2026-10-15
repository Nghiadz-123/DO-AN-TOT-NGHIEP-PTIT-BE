"""Gợi ý ứng viên phù hợp với một tin tuyển dụng (nhà tuyển dụng chủ động tìm ứng viên).

Nguồn ứng viên: candidates.selectors.discoverable_candidates (hồ sơ công khai hoặc đã ứng tuyển vào công ty),
so khớp bằng CV mặc định của ứng viên. Điểm tính khi gọi API (matching.py, không lưu DB): số ứng viên ở
quy mô đồ án nhỏ; khi có module AI có thể lưu kết quả vào bảng match_results và đọc từ đó.
"""
from dataclasses import dataclass

from django.db.models import Prefetch, Q

from apps.applications.models import Application
from apps.candidates import selectors as candidate_selectors
from apps.cvs.models import CV
from apps.jobs.models import Job, JobSkill

from . import matching


@dataclass
class TalentMatch:
    candidate: object  # CandidateProfile
    cv: CV
    match: matching.MatchResult
    application_id: object = None  # hồ sơ ứng viên đã nộp vào chính tin này (nếu có)
    connection: object = None  # Connection giữa nhà tuyển dụng đang xem và ứng viên (gắn ở view)


def get_company_job(company, job_id) -> Job | None:
    """Tin (chưa xóa) của công ty, kèm kỹ năng yêu cầu để so khớp."""
    return (
        Job.objects.filter(company=company, pk=job_id)
        .select_related('location')
        .prefetch_related(Prefetch('job_skills', queryset=JobSkill.objects.select_related('skill')))
        .first()
    )


def suggested_candidates(job, company, *, search: str = '', min_score: int = 0,
                         hide_applied: bool = False) -> list[TalentMatch]:
    """Ứng viên khớp ít nhất một kỹ năng của tin, điểm cao trước."""
    requirements = matching.job_requirements(job)
    if not requirements:
        return []

    candidates = (
        candidate_selectors.discoverable_candidates(company)
        .filter(cvs__is_default=True, cvs__deleted_at__isnull=True)
        .select_related('user', 'location')
        .prefetch_related(
            Prefetch('cvs', queryset=CV.objects.filter(is_default=True).defer('parsed_data'), to_attr='default_cvs')
        )
    )
    if search:
        candidates = candidates.filter(
            Q(user__full_name__icontains=search) | Q(headline__icontains=search)
            | Q(desired_position__icontains=search)
        )
    applied = dict(Application.objects.filter(job=job).values_list('candidate_id', 'id'))

    results = []
    for candidate in candidates:
        if hide_applied and candidate.pk in applied:
            continue
        cv = candidate.default_cvs[0] if candidate.default_cvs else None
        if cv is None:
            continue
        match = matching.score_candidate(job, requirements, candidate=candidate, cv_text=cv.raw_text)
        if match.matched_skills and match.score >= min_score:
            results.append(TalentMatch(candidate=candidate, cv=cv, match=match, application_id=applied.get(candidate.pk)))
    results.sort(key=lambda r: (-r.match.score, -len(r.match.matched_skills), r.candidate.user.full_name))
    return results


def get_discoverable_candidate(company, candidate_id):
    """Hồ sơ ứng viên công ty được xem, kèm CV mặc định (None nếu không được xem / không tồn tại)."""
    return (
        candidate_selectors.discoverable_candidates(company)
        .filter(pk=candidate_id)
        .prefetch_related(Prefetch('cvs', queryset=CV.objects.filter(is_default=True), to_attr='default_cvs'))
        .first()
    )
