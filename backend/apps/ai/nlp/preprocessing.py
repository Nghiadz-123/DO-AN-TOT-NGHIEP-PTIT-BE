"""Làm sạch, chuẩn hóa văn bản CV / tin tuyển dụng trước khi đưa vào LLM, embedding hoặc so khớp từ khóa."""
from apps.catalog.choices import JobLevel
from common.utils import strip_accents

# Giới hạn văn bản CV gửi cho LLM mỗi lần gọi (CV thật hiếm khi dài hơn), tránh tốn token với file bất thường
MAX_PROMPT_CV_CHARS = 20_000
MAX_JOB_LINES = 20


def normalize_for_match(text: str) -> str:
    """'Tin học  Văn phòng' -> 'tin hoc van phong': bỏ dấu, chữ thường, gộp khoảng trắng.
    CV PDF dùng font chuẩn hay mất dấu tiếng Việt nên so khớp trên dạng không dấu."""
    return ' '.join(strip_accents(text or '').lower().split())


def clip(text: str, limit: int) -> str:
    text = (text or '').strip()
    return text if len(text) <= limit else text[:limit].rstrip() + '…'


def lines(text: str) -> list[str]:
    """Các dòng không rỗng, bỏ ký hiệu đầu dòng ("- ", "• ")."""
    return [line.strip(' \t-•*+') for line in (text or '').splitlines() if line.strip(' \t-•*+')]


def years(value) -> str:
    """Decimal('2.0') -> '2', Decimal('1.5') -> '1.5'."""
    return f'{float(value or 0):g}'


def level_label(level: str) -> str:
    return JobLevel(level).label if level in JobLevel.values else (level or '')


def cv_prompt_text(cv) -> str:
    return clip(cv.raw_text, MAX_PROMPT_CV_CHARS)


def job_brief(job, *, max_lines: int = MAX_JOB_LINES) -> dict:
    """Thông tin tin tuyển dụng đưa vào prompt, tương đương JD đã chuẩn hóa (JD_SCHEMA) của TestAI.

    Tin trong hệ thống đã có cấu trúc (kỹ năng bắt buộc / ưu tiên, cấp bậc, số năm kinh nghiệm) nên không cần
    gọi LLM chuẩn hóa. `job` nên được prefetch job_skills__skill, select_related company, location.
    max_lines: số dòng mô tả / yêu cầu tối đa (gửi nhiều tin cùng lúc thì rút gọn để prompt không quá dài).
    """
    job_skills = list(job.job_skills.all())
    return {
        'title': job.title,
        'company': job.company.name,
        'level': level_label(job.level),
        'min_years_experience': float(job.min_years_experience or 0),
        'required_skills': [js.skill.name for js in job_skills if js.is_required],
        'nice_to_have_skills': [js.skill.name for js in job_skills if not js.is_required],
        'responsibilities': lines(job.description)[:max_lines],
        'requirements': lines(job.requirements)[:max_lines],
        'location': job.location.name if job.location_id else None,
    }
