"""Phân tích CV bằng AI: bóc tách hồ sơ cấu trúc và chấm điểm chất lượng CV.

Tương ứng bước LLM parse của ingest_cv và score_cv trong prototype TestAI/pipeline.py. Văn bản CV lấy từ kết quả
bóc tách của app cvs (CV.raw_text) nên không đọc lại file. Hồ sơ cấu trúc dùng cho gợi ý việc làm / gợi ý sửa CV
và tab "Thông tin AI trích xuất" trên giao diện.
"""
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor

from django.db import transaction
from django.utils import timezone

from apps.cvs.models import CVParseStatus
from common.exceptions import BusinessError

from ..llm import factory, schemas
from ..models import CVAnalysis, CVEmbedding, JobMatch
from ..nlp.preprocessing import cv_prompt_text
from ..prompts import cv_analysis as prompts

logger = logging.getLogger(__name__)

CV_NOT_READY_MESSAGE = (
    'CV chưa đọc được nội dung nên AI chưa phân tích được. Hãy chờ hệ thống đọc xong CV, '
    'hoặc tải lên file PDF xuất từ Word / Google Docs hay file DOCX.'
)


def ensure_ready(cv) -> None:
    """AI chỉ làm việc với CV đã bóc tách được văn bản (app cvs)."""
    if cv.parse_status != CVParseStatus.COMPLETED or not (cv.raw_text or '').strip():
        raise BusinessError(CV_NOT_READY_MESSAGE, code='cv_not_ready', status_code=409)


def source_hash(cv) -> str:
    return hashlib.sha256(cv.raw_text.encode()).hexdigest()


def get_analysis(cv) -> CVAnalysis:
    analysis, _ = CVAnalysis.objects.get_or_create(cv=cv)
    return analysis


def ensure_profile(cv, analysis: CVAnalysis | None = None) -> dict:
    """Hồ sơ cấu trúc của CV; chỉ gọi LLM khi chưa có hoặc văn bản CV đã đổi (bóc tách lại)."""
    ensure_ready(cv)
    analysis = analysis or get_analysis(cv)
    digest = source_hash(cv)
    if analysis.profile is not None and analysis.source_hash == digest:
        return analysis.profile
    _set_profile(analysis, _parse_profile(cv), digest)
    analysis.save(update_fields=['profile', 'source_hash', 'profiled_at', 'updated_at'])
    return analysis.profile


def score_cv(cv) -> CVAnalysis:
    """Chấm điểm CV theo 5 tiêu chí (prompts.cv_analysis.SCORE_CRITERIA).

    Nếu chưa có hồ sơ cấu trúc thì bóc tách song song (2 lời gọi LLM chạy cùng lúc) để lần gợi ý việc làm sau
    không phải chờ; bóc tách lỗi chỉ ghi log, không làm hỏng kết quả chấm điểm.
    """
    ensure_ready(cv)
    analysis = get_analysis(cv)
    digest = source_hash(cv)
    need_profile = analysis.profile is None or analysis.source_hash != digest

    # Các luồng phụ chỉ gọi API của LLM, không truy cập DB
    with ThreadPoolExecutor(max_workers=2) as pool:
        profile_job = pool.submit(_parse_profile, cv) if need_profile else None
        score = _score(cv)

    analysis.score_total = score['total']
    analysis.score_breakdown = score['breakdown']
    analysis.strengths = score['strengths']
    analysis.weaknesses = score['weaknesses']
    analysis.scored_at = timezone.now()
    fields = ['score_total', 'score_breakdown', 'strengths', 'weaknesses', 'scored_at', 'updated_at']
    if profile_job is not None:
        try:
            _set_profile(analysis, profile_job.result(), digest)
            fields += ['profile', 'source_hash', 'profiled_at']
        except Exception:
            logger.warning('Bóc tách hồ sơ CV %s thất bại, sẽ thử lại khi gợi ý việc làm', cv.pk, exc_info=True)
    analysis.save(update_fields=fields)
    return analysis


@transaction.atomic
def delete_cv_data(cv) -> None:
    """Xóa kết quả AI và vector của CV (CV bị xóa: dữ liệu cá nhân không giữ khi không còn cần)."""
    CVAnalysis.objects.filter(cv_id=cv.pk).delete()
    CVEmbedding.objects.filter(cv_id=cv.pk).delete()
    JobMatch.objects.filter(cv_id=cv.pk).delete()


def _parse_profile(cv) -> dict:
    result = factory.get_llm().generate_json(prompts.PARSE_CV_SYSTEM, cv_prompt_text(cv))
    logger.info('[AI] Bóc tách hồ sơ CV %s bằng %s', cv.pk, result.model)
    return schemas.normalize_cv_profile(result.data)


def _score(cv) -> dict:
    result = factory.get_llm().generate_json(prompts.SCORE_CV_SYSTEM, cv_prompt_text(cv))
    logger.info('[AI] Chấm điểm CV %s bằng %s', cv.pk, result.model)
    return schemas.normalize_score(result.data)


def _set_profile(analysis: CVAnalysis, profile: dict, digest: str) -> None:
    analysis.profile = profile
    analysis.source_hash = digest
    analysis.profiled_at = timezone.now()
