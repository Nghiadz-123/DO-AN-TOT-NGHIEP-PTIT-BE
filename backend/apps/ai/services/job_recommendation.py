"""Gợi ý việc làm cho một CV (recommend_jobs của prototype TestAI/pipeline.py).

Giai đoạn 1 (rẻ, nhanh — mỗi lần mở trang): cosine embedding CV ↔ tin đang tuyển + tỉ lệ kỹ năng bắt buộc của
tin có trong CV -> điểm = 60·sim + 40·skill_overlap (công thức TestAI khi không rerank).
Giai đoạn 2 (khi ứng viên bấm "AI đánh giá chi tiết" một tin): LLM đọc hồ sơ CV + tin, cho điểm 0-100, kỹ năng
khớp / thiếu và nhận xét -> điểm = 0.5·llm + 30·sim + 20·skill_overlap (công thức TestAI khi rerank). Kết quả lưu
ở bảng match_results và dùng lại tới khi CV hoặc nội dung tin thay đổi.
"""
import json
import logging
from dataclasses import dataclass, field

from apps.jobs import selectors as job_selectors

from ..llm import factory, schemas
from ..models import JobMatch
from ..nlp.preprocessing import job_brief, years
from ..nlp.skill_extractor import find_skills
from ..prompts import job_recommendation as prompts
from ..vectorstore import client, embeddings, indexer
from . import cv_analysis

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 20  # số việc làm trang "Việc làm phù hợp" hiển thị, cũng là số tin gửi kèm khi gợi ý sửa CV
MAX_LIMIT = 50
UNKNOWN_OVERLAP = 0.5  # tin không khai kỹ năng: không cộng cũng không trừ điểm kỹ năng
# Hồ sơ CV gửi cho LLM khi đánh giá: bỏ thông tin liên hệ (không cần để đánh giá)
PRIVATE_PROFILE_FIELDS = ('email', 'phone')


@dataclass
class JobRecommendation:
    job: object  # Job
    similarity: float  # cosine CV - tin, 0-1
    skill_overlap: float  # tỉ lệ kỹ năng bắt buộc của tin có trong CV, 0-1
    matched_skills: list = field(default_factory=list)  # tên kỹ năng của tin CV đã có
    missing_skills: list = field(default_factory=list)
    reasons: list = field(default_factory=list)
    evaluation: JobMatch | None = None  # kết quả AI đánh giá chi tiết (nếu đã có và còn hiệu lực)

    @property
    def score(self) -> int:
        if self.evaluation is not None:
            value = 0.5 * self.evaluation.score + 30 * self.similarity + 20 * self.skill_overlap
        else:
            value = 60 * self.similarity + 40 * self.skill_overlap
        return min(max(round(value), 0), 100)


def recommend_jobs(cv, *, limit: int = DEFAULT_LIMIT) -> list[JobRecommendation]:
    """Các tin đang tuyển phù hợp nhất với CV, điểm cao trước."""
    cv_analysis.ensure_ready(cv)
    analysis = cv_analysis.get_analysis(cv)
    profile = cv_analysis.ensure_profile(cv, analysis)
    jobs = {job.pk: job for job in job_selectors.public_jobs()}
    if not jobs:
        return []

    query = indexer.cv_vector(cv, profile)
    items = [
        _recommendation(jobs[pk], similarity, profile, cv.raw_text)
        for pk, similarity in client.top_k(query, indexer.job_vectors(jobs.values()))
    ]
    _attach_evaluations(cv, analysis.source_hash, items)
    items.sort(key=lambda item: (-item.score, -item.similarity))
    return items[:limit]


def match_job(cv, job) -> JobRecommendation:
    """Điểm phù hợp của CV với một tin bất kỳ (vd. tin mục tiêu khi gợi ý sửa CV), cùng cách tính với recommend_jobs.
    `job` nên được prefetch job_skills__skill."""
    return _match_one(cv, job)[0]


def evaluate_job(cv, job) -> JobRecommendation:
    """AI đánh giá chi tiết một tin (job lấy từ jobs.selectors.public_jobs); luôn gọi lại LLM."""
    item, analysis, profile = _match_one(cv, job)

    cv_brief = {key: value for key, value in profile.items() if key not in PRIVATE_PROFILE_FIELDS}
    result = factory.get_llm().generate_json(
        prompts.MATCH_SYSTEM,
        f'CV:\n{json.dumps(cv_brief, ensure_ascii=False)}\n\nJD:\n{json.dumps(job_brief(job), ensure_ascii=False)}',
    )
    logger.info('[AI] Đánh giá CV %s - tin %s bằng %s', cv.pk, job.pk, result.model)
    data = schemas.normalize_match(result.data)
    item.evaluation, _ = JobMatch.objects.update_or_create(
        cv=cv, job=job,
        defaults={**data, 'cv_hash': analysis.source_hash, 'job_hash': embeddings.content_hash(embeddings.job_text(job))},
    )
    return item


def _match_one(cv, job):
    """(JobRecommendation kèm kết quả AI đánh giá còn hiệu lực, CVAnalysis, hồ sơ CV)."""
    cv_analysis.ensure_ready(cv)
    analysis = cv_analysis.get_analysis(cv)
    profile = cv_analysis.ensure_profile(cv, analysis)
    query = indexer.cv_vector(cv, profile)
    vector = indexer.job_vectors([job])[job.pk]
    item = _recommendation(job, client.cosine(query, vector), profile, cv.raw_text)
    _attach_evaluations(cv, analysis.source_hash, [item])
    return item, analysis, profile


def _recommendation(job, similarity: float, profile: dict, cv_text: str) -> JobRecommendation:
    job_skills = list(job.job_skills.all())
    found, missing = find_skills(
        [js.skill for js in job_skills], cv_skills=profile.get('skills') or [], cv_text=cv_text
    )
    found_ids = {skill.pk for skill in found}
    # Tỉ lệ khớp tính trên kỹ năng bắt buộc (như TestAI); tin chỉ có kỹ năng ưu tiên thì tính trên tất cả
    basis = [js for js in job_skills if js.is_required] or job_skills
    overlap = sum(js.skill_id in found_ids for js in basis) / len(basis) if basis else UNKNOWN_OVERLAP
    similarity = min(max(similarity, 0.0), 1.0)
    return JobRecommendation(
        job=job,
        similarity=similarity,
        skill_overlap=overlap,
        matched_skills=[skill.name for skill in found],
        missing_skills=[skill.name for skill in missing],
        reasons=_reasons(job, job_skills, found_ids, similarity, profile),
    )


def _attach_evaluations(cv, cv_hash: str, items: list[JobRecommendation]) -> None:
    """Gắn kết quả AI đánh giá đã lưu, bỏ qua kết quả cũ (CV bóc tách lại hoặc tin đã sửa nội dung)."""
    by_job = {item.job.pk: item for item in items}
    for match in JobMatch.objects.filter(cv=cv, job_id__in=by_job, cv_hash=cv_hash):
        item = by_job[match.job_id]
        if match.job_hash == embeddings.content_hash(embeddings.job_text(item.job)):
            item.evaluation = match


def _reasons(job, job_skills, found_ids: set, similarity: float, profile: dict) -> list[str]:
    """Giải thích ngắn bằng tiếng Việt cho ứng viên."""
    reasons = [f'Nội dung CV tương đồng {round(similarity * 100)}% với mô tả công việc']
    required = [js for js in job_skills if js.is_required]
    if required:
        have = [js.skill.name for js in required if js.skill_id in found_ids]
        lacking = [js.skill.name for js in required if js.skill_id not in found_ids]
        reasons.append(f'Đáp ứng {len(have)}/{len(required)} kỹ năng bắt buộc' + (f': {", ".join(have)}' if have else ''))
        if lacking:
            reasons.append('Còn thiếu: ' + ', '.join(lacking))
    required_years = float(job.min_years_experience or 0)
    cv_years = profile.get('years_of_experience')
    if required_years and cv_years is not None:
        reasons.append(f'CV có {years(cv_years)} năm kinh nghiệm (yêu cầu từ {years(required_years)} năm)')
    return reasons
