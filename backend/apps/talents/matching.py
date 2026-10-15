"""Chấm điểm mức độ phù hợp giữa ứng viên (CV + hồ sơ) và một tin tuyển dụng bằng quy tắc, không dùng LLM.

Điểm 0-100 là tổng điểm 4 tiêu chí (trọng số WEIGHTS):
- skills: kỹ năng của JD (tên chuẩn + tên gọi khác trong danh mục) xuất hiện trong CV / hồ sơ.
  Kỹ năng bắt buộc nặng gấp REQUIRED_SKILL_FACTOR lần, nhân thêm trọng số 1-5 nhà tuyển dụng đặt;
- experience: số năm kinh nghiệm so với yêu cầu tối thiểu;
- level: cấp bậc hiện tại so với cấp bậc của tin (lệch 1 bậc được một phần điểm);
- location: cùng tỉnh/thành, hoặc tin làm việc từ xa.
Thiếu thông tin (hồ sơ chưa khai) được UNKNOWN_RATIO số điểm của tiêu chí.

Văn bản được bỏ dấu + chữ thường trước khi so khớp: CV PDF dùng font chuẩn thường mất dấu tiếng Việt
("Ban hang" vẫn khớp kỹ năng "Bán hàng"). Kỹ năng phải khớp trọn từ ("Java" không khớp "JavaScript").
Module AI (giai đoạn sau) có thể thay bằng embedding + LLM mà không đổi API của app talents.
"""
import re
from dataclasses import dataclass, field

from apps.catalog.choices import JobLevel, WorkMode
from common.utils import strip_accents

WEIGHTS = {'skills': 60, 'experience': 20, 'level': 10, 'location': 10}
REQUIRED_SKILL_FACTOR = 2
UNKNOWN_RATIO = 0.5
NEAR_LEVEL_RATIO = 0.6  # lệch một bậc
LEVEL_ORDER = list(JobLevel.values)  # intern < fresher < staff < supervisor < manager < director


def normalize(text: str) -> str:
    """'Tin học  Văn phòng' -> 'tin hoc van phong' (bỏ dấu, chữ thường, gộp khoảng trắng / xuống dòng)."""
    return ' '.join(strip_accents(text or '').lower().split())


def _term_pattern(term: str):
    # Ranh giới là ký tự không phải chữ / số, để giữ được kỹ năng có ký tự đặc biệt: C++, C#, .NET, Node.js
    return re.compile(rf'(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])')


@dataclass(frozen=True)
class SkillRequirement:
    name: str
    is_required: bool
    weight: int
    patterns: tuple


@dataclass
class MatchResult:
    score: int
    breakdown: dict
    matched_skills: list = field(default_factory=list)
    missing_skills: list = field(default_factory=list)
    reasons: list = field(default_factory=list)


def job_requirements(job) -> list[SkillRequirement]:
    """Kỹ năng yêu cầu của tin (job.job_skills nên được prefetch kèm skill)."""
    requirements = []
    for job_skill in job.job_skills.all():
        skill = job_skill.skill
        terms = {normalize(term) for term in [skill.name, *(skill.aliases or [])]}
        requirements.append(SkillRequirement(
            name=skill.name,
            is_required=job_skill.is_required,
            weight=job_skill.weight * (REQUIRED_SKILL_FACTOR if job_skill.is_required else 1),
            patterns=tuple(_term_pattern(term) for term in terms if term),
        ))
    return requirements


def score_candidate(job, requirements: list[SkillRequirement], *, candidate, cv_text: str = '') -> MatchResult:
    """So khớp một ứng viên với tin `job`. `candidate`: CandidateProfile (kèm location)."""
    text = normalize(' '.join([candidate.headline, candidate.desired_position, candidate.summary, cv_text or '']))
    hits = [any(p.search(text) for p in r.patterns) for r in requirements]
    matched = [r for r, hit in zip(requirements, hits) if hit]
    missing = [r for r, hit in zip(requirements, hits) if not hit]
    total_weight = sum(r.weight for r in requirements)
    ratios = {
        'skills': sum(r.weight for r in matched) / total_weight if total_weight else 0.0,
        'experience': _experience_ratio(candidate.years_of_experience, job.min_years_experience),
        'level': _level_ratio(candidate.current_level, job.level),
        'location': _location_ratio(candidate, job),
    }
    breakdown = {key: round(ratio * WEIGHTS[key]) for key, ratio in ratios.items()}
    return MatchResult(
        score=sum(breakdown.values()),
        breakdown=breakdown,
        matched_skills=[r.name for r in matched],
        missing_skills=[r.name for r in missing],
        reasons=_reasons(job, candidate, requirements, matched, missing),
    )


def _experience_ratio(years, required) -> float:
    required = float(required or 0)
    if required <= 0:
        return 1.0
    if years is None:
        return UNKNOWN_RATIO
    return min(float(years) / required, 1.0)


def _level_ratio(candidate_level: str, job_level: str) -> float:
    if candidate_level not in LEVEL_ORDER or job_level not in LEVEL_ORDER:
        return UNKNOWN_RATIO
    gap = abs(LEVEL_ORDER.index(candidate_level) - LEVEL_ORDER.index(job_level))
    return 1.0 if gap == 0 else NEAR_LEVEL_RATIO if gap == 1 else 0.0


def _location_ratio(candidate, job) -> float:
    if job.work_mode == WorkMode.REMOTE:
        return 1.0
    if not job.location_id or not candidate.location_id:
        return UNKNOWN_RATIO
    return 1.0 if candidate.location_id == job.location_id else 0.0


def _years(value) -> str:
    return f'{float(value):g}'.replace('.', ',')


def _reasons(job, candidate, requirements, matched, missing) -> list[str]:
    """Giải thích ngắn bằng tiếng Việt cho nhà tuyển dụng."""
    reasons = [f'Đáp ứng {len(matched)}/{len(requirements)} kỹ năng yêu cầu']
    missing_required = [r.name for r in missing if r.is_required]
    if missing_required:
        reasons.append('Thiếu kỹ năng bắt buộc: ' + ', '.join(missing_required))

    required_years = float(job.min_years_experience or 0)
    if candidate.years_of_experience is None:
        reasons.append('Chưa khai báo số năm kinh nghiệm')
    elif required_years:
        reasons.append(f'{_years(candidate.years_of_experience)} năm kinh nghiệm '
                       f'(yêu cầu từ {_years(required_years)} năm)')
    else:
        reasons.append(f'{_years(candidate.years_of_experience)} năm kinh nghiệm')

    if candidate.current_level:
        level = JobLevel(candidate.current_level).label
        reasons.append(f'Đúng cấp bậc {level}' if candidate.current_level == job.level else f'Cấp bậc hiện tại: {level}')

    if job.work_mode == WorkMode.REMOTE:
        reasons.append('Làm việc từ xa, không giới hạn địa điểm')
    elif candidate.location_id and job.location_id:
        if candidate.location_id == job.location_id:
            reasons.append(f'Cùng địa điểm {job.location.name}')
        else:
            reasons.append(f'Ở {candidate.location.name} (nơi làm việc: {job.location.name})')
    return reasons
