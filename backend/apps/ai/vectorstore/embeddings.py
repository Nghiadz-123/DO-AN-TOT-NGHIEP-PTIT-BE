"""Sinh embedding cho CV và tin tuyển dụng.

CV và tin được đưa về cùng một khuôn văn bản (vị trí, kinh nghiệm, kỹ năng...) trước khi embedding để cosine
similarity so sánh được — giống cv_to_embed_text / jd_to_embed_text của prototype TestAI. CV dùng hồ sơ cấu trúc
do LLM bóc tách; tin tuyển dụng đã có cấu trúc trong DB nên không cần LLM chuẩn hóa như TestAI.
"""
import hashlib
import math

from ..llm import factory
from ..nlp.preprocessing import clip, level_label, lines, years

# gemini-embedding-001 nhận tối đa 2048 token mỗi đoạn văn bản
MAX_EMBED_CHARS = 4000
VECTOR_DECIMALS = 6  # đủ chính xác cho cosine, JSON lưu DB gọn hơn một nửa


def cv_text(profile: dict) -> str:
    experiences = '; '.join(
        f"{e.get('position') or ''} tại {e.get('company') or ''}" for e in profile.get('experiences') or []
    )
    projects = '; '.join(
        f"{p.get('name') or ''} ({', '.join(p.get('tech') or [])})" for p in profile.get('projects') or []
    )
    return clip(
        f"Vị trí: {profile.get('title') or ''}\n"
        f"Kinh nghiệm: {years(profile.get('years_of_experience'))} năm. {experiences}\n"
        f"Kỹ năng: {', '.join(profile.get('skills') or [])}\n"
        f'Dự án: {projects}\n'
        f"Tóm tắt: {profile.get('summary') or ''}",
        MAX_EMBED_CHARS,
    )


def job_text(job) -> str:
    """`job` nên được prefetch job_skills__skill (jobs.selectors.public_jobs đã làm)."""
    skills = [job_skill.skill.name for job_skill in job.job_skills.all()]
    return clip(
        f'Vị trí: {job.title} ({level_label(job.level)})\n'
        f'Kinh nghiệm: tối thiểu {years(job.min_years_experience)} năm\n'
        f"Kỹ năng: {', '.join(skills)}\n"
        f"Yêu cầu: {'; '.join(lines(job.requirements))}\n"
        f"Công việc: {'; '.join(lines(job.description))}",
        MAX_EMBED_CHARS,
    )


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def current_model() -> str:
    return factory.get_llm().embed_model


def embed_texts(texts: list[str]) -> tuple[list[list[float]], str]:
    """Trả về (vector đã chuẩn hóa độ dài 1, tên model embedding)."""
    llm = factory.get_llm()
    return [_unit(vector) for vector in llm.embed(texts)], llm.embed_model


def _unit(vector) -> list[float]:
    norm = math.sqrt(math.sumprod(vector, vector)) or 1.0
    return [round(x / norm, VECTOR_DECIMALS) for x in vector]
