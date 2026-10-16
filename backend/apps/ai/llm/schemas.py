"""Kiểm tra và chuẩn hóa JSON do LLM trả về trước khi lưu / trả cho frontend.

Model đôi khi trả thiếu trường, sai kiểu ("18" thay vì 18) hoặc vượt thang điểm: các hàm ở đây sửa những lỗi
nhỏ đó (ép kiểu, kẹp trong thang điểm, bỏ phần tử rỗng) thay vì từ chối cả kết quả. Chỉ ném AIInvalidOutputError
khi thiếu phần cốt lõi (vd. không có điểm nào).
"""
import json
import re

from ..prompts.cv_analysis import SCORE_CRITERIA
from .exceptions import AIInvalidOutputError

PRIORITIES = ('high', 'medium', 'low')
_FENCE = re.compile(r'```(?:json)?\s*(.*?)```', re.S)


def parse_json(text: str | None) -> dict:
    """Parse JSON kể cả khi model bọc trong ```json ... ``` hoặc thêm chữ trước / sau (như TestAI)."""
    text = (text or '').strip()
    match = _FENCE.search(text)
    if match:
        text = match.group(1)
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end < start:
        raise ValueError('Không tìm thấy JSON object')
    data = json.loads(text[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError('JSON không phải object')
    return data


# ------------------------------------------------------------------------------------------ chấm điểm CV
def normalize_score(data: dict) -> dict:
    """{"total", "breakdown": {tiêu chí: điểm}, "strengths", "weaknesses"}.

    Tổng điểm được cộng lại từ breakdown (đã kẹp trong điểm tối đa của từng tiêu chí) để luôn khớp với phần
    chi tiết hiển thị, không dùng `total` model tự cộng.
    """
    raw = data.get('breakdown') if isinstance(data.get('breakdown'), dict) else {}
    breakdown = {key: _int(raw.get(key), 0, maximum) for key, (_, maximum, _) in SCORE_CRITERIA.items()}
    if all(value is None for value in breakdown.values()):
        raise AIInvalidOutputError()
    breakdown = {key: value or 0 for key, value in breakdown.items()}
    return {
        'total': sum(breakdown.values()),
        'breakdown': breakdown,
        'strengths': _str_list(data.get('strengths'), limit=10),
        'weaknesses': _str_list(data.get('weaknesses'), limit=10),
    }


# ------------------------------------------------------------------------------------------ hồ sơ cấu trúc CV
def normalize_cv_profile(data: dict) -> dict:
    """Theo prompts.cv_analysis.CV_SCHEMA."""
    return {
        'full_name': _str(data.get('full_name'), 150),
        'email': _str(data.get('email'), 254) or None,
        'phone': _str(data.get('phone'), 30) or None,
        'location': _str(data.get('location'), 200) or None,
        'title': _str(data.get('title'), 200),
        'summary': _str(data.get('summary'), 3000, multiline=True),
        'years_of_experience': _number(data.get('years_of_experience'), 0, 60),
        'skills': _str_list(data.get('skills'), limit=60, max_length=100, lower=True),
        'experiences': [
            _fields(item, {'company': 200, 'position': 200, 'start': 30, 'end': 30, 'description': 3000})
            for item in _dict_list(data.get('experiences'), 20)
        ],
        'educations': [
            _fields(item, {'school': 200, 'degree': 150, 'major': 150, 'start': 30, 'end': 30, 'gpa': 20})
            for item in _dict_list(data.get('educations'), 10)
        ],
        'projects': [
            {**_fields(item, {'name': 200, 'description': 3000}), 'tech': _str_list(item.get('tech'), limit=20)}
            for item in _dict_list(data.get('projects'), 20)
        ],
        'certifications': _str_list(data.get('certifications'), limit=20),
        'languages': _str_list(data.get('languages'), limit=10),
    }


# ------------------------------------------------------------------------------------------ gợi ý sửa CV
def normalize_suggestions(data: dict, *, valid_refs: set[int]) -> dict:
    """{"suggestions": [...], "missing_keywords": [...]}; `jd_refs` chỉ giữ số thứ tự JD có trong prompt.
    Gợi ý được xếp theo mức ưu tiên (giữ thứ tự của model trong cùng mức)."""
    items = []
    for item in _dict_list(data.get('suggestions'), 15):
        suggestion = _str(item.get('suggestion'), 2000, multiline=True)
        if not suggestion:
            continue
        priority = str(item.get('priority') or '').lower()
        items.append({
            'section': _str(item.get('section'), 100) or 'Chung',
            'issue': _str(item.get('issue'), 1000, multiline=True),
            'suggestion': suggestion,
            'example_before': _str(item.get('example_before'), 2000, multiline=True) or None,
            'example_after': _str(item.get('example_after'), 2000, multiline=True) or None,
            'priority': priority if priority in PRIORITIES else 'medium',
            'jd_refs': [ref for ref in _int_list(item.get('jd_refs')) if ref in valid_refs],
        })
    if not items:
        raise AIInvalidOutputError()
    items.sort(key=lambda s: PRIORITIES.index(s['priority']))
    return {'suggestions': items, 'missing_keywords': _str_list(data.get('missing_keywords'), limit=20, max_length=100)}


# ------------------------------------------------------------------------------------------ đánh giá CV - việc làm
def normalize_match(data: dict) -> dict:
    score = _int(data.get('score'), 0, 100)
    if score is None:
        raise AIInvalidOutputError()
    return {
        'score': score,
        'matched_skills': _str_list(data.get('matched_skills'), limit=30, max_length=100),
        'missing_skills': _str_list(data.get('missing_skills'), limit=30, max_length=100),
        'reason': _str(data.get('reason'), 2000, multiline=True),
    }


# ------------------------------------------------------------------------------------------ helpers
def _str(value, max_length: int = 500, *, multiline: bool = False) -> str:
    """Chuỗi đã gộp khoảng trắng; multiline=True giữ xuống dòng (đoạn mô tả, ví dụ trước / sau khi sửa)."""
    if value is None or isinstance(value, (dict, list)):
        return ''
    lines = (' '.join(line.split()) for line in str(value).splitlines()) if multiline else [' '.join(str(value).split())]
    return '\n'.join(line for line in lines if line)[:max_length]


def _number(value, low: float, high: float) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:  # NaN
        return None
    return min(max(number, low), high)


def _int(value, low: int, high: int) -> int | None:
    number = _number(value, low, high)
    return None if number is None else round(number)


def _int_list(value) -> list[int]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        number = _int(str(item).lstrip('#') if isinstance(item, str) else item, 0, 10_000)
        if number is not None and number not in result:
            result.append(number)
    return result


def _str_list(value, *, limit: int, max_length: int = 500, lower: bool = False) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        text = _str(item, max_length)
        if lower:
            text = text.lower()
        if text and text not in result:
            result.append(text)
    return result[:limit]


def _dict_list(value, limit: int) -> list[dict]:
    return [item for item in value if isinstance(item, dict)][:limit] if isinstance(value, list) else []


def _fields(item: dict, lengths: dict) -> dict:
    """Lấy các trường chuỗi của một phần tử (kinh nghiệm, học vấn...); trường 'description' giữ xuống dòng."""
    return {
        key: _str(item.get(key), length, multiline=key == 'description') or None for key, length in lengths.items()
    }
