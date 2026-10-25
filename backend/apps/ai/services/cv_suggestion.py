"""Gợi ý sửa CV dựa trên tin tuyển dụng thật trong hệ thống (suggest_cv của prototype TestAI/pipeline.py).

Tin tham chiếu gửi kèm prompt: REFERENCE_JOBS việc làm được gợi ý cho CV — đúng danh sách và thứ tự trang "Việc làm
phù hợp" (so sánh embedding + kỹ năng bắt buộc, services.job_recommendation), thay vì 3 tin gần nhất như TestAI.
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
REFERENCE_JOB_LINES = 8  # rút gọn mô tả / yêu cầu của tin tham chiếu cho prompt gọn
SUMMARY_MIN_SCORE = 50  # chỉ tổng hợp kỹ năng còn thiếu từ các tin đủ phù hợp (tránh kỹ năng của ngành khác)
SUMMARY_SKILLS = 10


def suggest_cv(cv) -> CVAnalysis:
    cv_analysis.ensure_ready(cv)
    analysis = cv_analysis.get_analysis(cv)
    cv_analysis.ensure_profile(cv, analysis)
    references = job_recommendation.recommend_jobs(cv, limit=REFERENCE_JOBS)

    user = f'CV:\n{cv_prompt_text(cv)}'
    if references:
        user += '\n\n' + _references_prompt(references)
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
            'score': item.score,
        }
        for item in references
    ]
    analysis.suggested_at = timezone.now()
    analysis.save(update_fields=[
        'suggestions', 'missing_keywords', 'reference_jobs', 'suggested_at', 'updated_at',
    ])
    return analysis


def _references_prompt(references) -> str:
    blocks = []
    for number, item in enumerate(references, start=1):
        brief = job_brief(item.job, max_lines=REFERENCE_JOB_LINES)
        brief.update({
            'match_score': item.score,
            'cv_has_skills': item.matched_skills,
            'cv_missing_skills': item.missing_skills,
        })
        blocks.append(f'JD #{number}:\n{json.dumps(brief, ensure_ascii=False)}')
    text = 'CÁC JD THAM CHIẾU:\n' + '\n\n'.join(blocks)

    relevant = [item for item in references if item.score >= SUMMARY_MIN_SCORE]
    missing = Counter(skill for item in relevant for skill in item.missing_skills)
    if missing:
        text += (
            f'\n\nKỸ NĂNG CV CÒN THIẾU LẶP LẠI NHIỀU NHẤT (trong {len(relevant)} JD phù hợp nhất): '
            + ', '.join(f'{skill} ({count} JD)' for skill, count in missing.most_common(SUMMARY_SKILLS))
        )
    return text
