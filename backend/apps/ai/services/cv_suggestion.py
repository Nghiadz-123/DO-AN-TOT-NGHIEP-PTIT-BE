"""Gợi ý sửa CV dựa trên tin tuyển dụng thật trong hệ thống (suggest_cv của prototype TestAI/pipeline.py).

Tin tham chiếu gửi kèm prompt:
- target_job: tin mục tiêu ứng viên chọn (nếu có), luôn đứng đầu và được ưu tiên cao nhất;
- REFERENCE_JOBS việc làm được gợi ý cho CV — đúng danh sách và thứ tự trang "Việc làm phù hợp" (so sánh embedding +
  kỹ năng bắt buộc, services.job_recommendation), thay vì 3 tin gần nhất như TestAI.
Mỗi tin kèm điểm phù hợp, kỹ năng CV đã có / còn thiếu; thêm bảng tổng hợp kỹ năng còn thiếu lặp lại ở nhiều tin phù
hợp, để AI gợi ý bám vào yêu cầu thật của thị trường thay vì gợi ý chung chung.
"""
import json
import logging
from collections import Counter

from django.utils import timezone

from ..llm import factory, schemas
from ..models import CVAnalysis
from ..nlp.preprocessing import cv_prompt_text, job_brief
from ..prompts import cv_suggestion as prompts
from . import cv_analysis, job_recommendation

logger = logging.getLogger(__name__)

REFERENCE_JOBS = job_recommendation.DEFAULT_LIMIT
REFERENCE_JOB_LINES = 8  # tin tham chiếu (không phải tin mục tiêu): rút gọn mô tả / yêu cầu cho prompt gọn
SUMMARY_MIN_SCORE = 50  # chỉ tổng hợp kỹ năng còn thiếu từ các tin đủ phù hợp (tránh kỹ năng của ngành khác)
SUMMARY_SKILLS = 10


def suggest_cv(cv, *, target_job=None) -> CVAnalysis:
    """target_job: tin (jobs.selectors.public_job_detail_queryset) ứng viên muốn nhắm tới, hoặc None."""
    cv_analysis.ensure_ready(cv)
    analysis = cv_analysis.get_analysis(cv)
    cv_analysis.ensure_profile(cv, analysis)
    references = _reference_jobs(cv, target_job)

    user = f'CV:\n{cv_prompt_text(cv)}'
    if references:
        user += '\n\n' + _references_prompt(references, target_job)
    result = factory.get_llm().generate_json(prompts.SUGGEST_CV_SYSTEM, user)
    logger.info('[AI] Gợi ý sửa CV %s bằng %s (%s tin tham chiếu)', cv.pk, result.model, len(references))
    data = schemas.normalize_suggestions(result.data, valid_refs=set(range(1, len(references) + 1)))

    for item in data['suggestions']:
        # Số thứ tự JD trong prompt -> id tin để frontend dẫn link
        item['job_ids'] = [str(references[number - 1].job.pk) for number in item.pop('jd_refs')]
    analysis.suggestions = data['suggestions']
    analysis.missing_keywords = data['missing_keywords']
    analysis.reference_jobs = [
        {
            'id': str(item.job.pk), 'title': item.job.title, 'company': item.job.company.name,
            'score': item.score, 'is_target': _is_target(item, target_job),
        }
        for item in references
    ]
    analysis.target_job = target_job
    analysis.suggested_at = timezone.now()
    analysis.save(update_fields=[
        'suggestions', 'missing_keywords', 'reference_jobs', 'target_job', 'suggested_at', 'updated_at',
    ])
    return analysis


def _reference_jobs(cv, target_job) -> list:
    """Tin mục tiêu (nếu có) đứng đầu, sau đó REFERENCE_JOBS việc làm được gợi ý (điểm cao trước)."""
    recommended = job_recommendation.recommend_jobs(cv, limit=REFERENCE_JOBS + 1)
    if target_job is None:
        return recommended[:REFERENCE_JOBS]
    target = next((item for item in recommended if item.job.pk == target_job.pk), None)
    if target is None:  # tin mục tiêu không nằm trong danh sách gợi ý (vd. điểm thấp, đã đóng)
        target = job_recommendation.match_job(cv, target_job)
    return [target] + [item for item in recommended if item.job.pk != target_job.pk][:REFERENCE_JOBS]


def _references_prompt(references, target_job) -> str:
    blocks = []
    for number, item in enumerate(references, start=1):
        is_target = _is_target(item, target_job)
        brief = job_brief(item.job) if is_target else job_brief(item.job, max_lines=REFERENCE_JOB_LINES)
        brief.update({
            'match_score': item.score,
            'cv_has_skills': item.matched_skills,
            'cv_missing_skills': item.missing_skills,
        })
        tag = ' (JD MỤC TIÊU do ứng viên chọn)' if is_target else ''
        blocks.append(f'JD #{number}{tag}:\n{json.dumps(brief, ensure_ascii=False)}')
    text = 'CÁC JD THAM CHIẾU:\n' + '\n\n'.join(blocks)

    relevant = [item for item in references if _is_target(item, target_job) or item.score >= SUMMARY_MIN_SCORE]
    missing = Counter(skill for item in relevant for skill in item.missing_skills)
    if missing:
        text += (
            f'\n\nKỸ NĂNG CV CÒN THIẾU LẶP LẠI NHIỀU NHẤT (trong {len(relevant)} JD phù hợp nhất): '
            + ', '.join(f'{skill} ({count} JD)' for skill, count in missing.most_common(SUMMARY_SKILLS))
        )
    return text


def _is_target(item, target_job) -> bool:
    return target_job is not None and item.job.pk == target_job.pk
