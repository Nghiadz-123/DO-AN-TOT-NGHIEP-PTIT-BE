"""Nhà tuyển dụng chủ động tìm ứng viên.

- Tìm ứng viên (talent_pool): mọi ứng viên công khai CV, không cần tin tuyển dụng.
- Ứng viên phù hợp với một tin (suggested_candidates): nguồn là candidates.selectors.discoverable_candidates
  (công khai CV hoặc đã ứng tuyển vào công ty), so khớp bằng CV mặc định của ứng viên. Điểm tính khi gọi API
  (matching.py, không lưu DB): số ứng viên ở quy mô đồ án nhỏ; khi có module AI có thể lưu kết quả vào bảng
  match_results và đọc từ đó.
"""
from dataclasses import dataclass

from django.db.models import Exists, OuterRef, Prefetch, Q, Subquery

from apps.applications.models import Application
from apps.candidates import selectors as candidate_selectors
from apps.cvs.models import CV
from apps.jobs.models import Job, JobSkill
from common.utils import strip_accents

from . import matching


@dataclass
class TalentProfile:
    candidate: object  # CandidateProfile
    cv: CV  # CV chính ứng viên công khai
    invitation: object = None  # thư mời gần nhất của công ty đang xem (gắn ở view)


@dataclass
class TalentMatch:
    candidate: object  # CandidateProfile
    cv: CV
    match: matching.MatchResult
    application_id: object = None  # hồ sơ ứng viên đã nộp vào chính tin này (nếu có)
    invitation: object = None  # thư mời của công ty cho chính tin này (gắn ở view)


def talent_pool(*, search: str = '', location_id=None, level: str = ''):
    """Ứng viên công khai CV, kèm CV chính (`default_cvs`), CV cập nhật gần nhất trước.

    `search` tìm trong tên, tiêu đề hồ sơ, vị trí mong muốn, giới thiệu và nội dung CV. CV PDF font chuẩn mất dấu
    tiếng Việt nên nội dung CV được so thêm với từ khóa đã bỏ dấu ("kế toán" vẫn tìm thấy "Ke toan").
    """
    default_cv = CV.objects.filter(candidate=OuterRef('pk'), is_default=True)
    candidates = (
        candidate_selectors.public_candidates()
        .filter(Exists(default_cv))
        .select_related('user', 'location')
        .prefetch_related(
            Prefetch(
                'cvs', queryset=CV.objects.filter(is_default=True).defer('raw_text', 'parsed_data'), to_attr='default_cvs'
            )
        )
        .annotate(cv_updated_at=Subquery(default_cv.values('updated_at')[:1]))
        .order_by('-cv_updated_at', 'user__full_name')
    )
    if location_id:
        candidates = candidates.filter(location_id=location_id)
    if level:
        candidates = candidates.filter(current_level=level)
    if search:
        cv_text = Q(raw_text__icontains=search) | Q(raw_text__icontains=strip_accents(search))
        candidates = candidates.filter(
            Q(user__full_name__icontains=search) | Q(headline__icontains=search)
            | Q(desired_position__icontains=search) | Q(summary__icontains=search)
            | Q(Exists(default_cv.filter(cv_text)))
        )
    return candidates


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
