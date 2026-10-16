"""Tìm kỹ năng yêu cầu của tin tuyển dụng trong CV bằng quy tắc (rẻ, nhanh), bổ trợ cho embedding.

Một kỹ năng được coi là CV đã có nếu tên chuẩn hoặc tên gọi khác (Skill.aliases của danh mục) trùng một kỹ năng
LLM bóc tách từ CV, hoặc xuất hiện trọn từ trong văn bản CV ("Excel" không khớp "excellent"). So khớp trên dạng
bỏ dấu, chữ thường nên "ban hang" (PDF mất dấu) vẫn khớp "Bán hàng". Cải thiện so với TestAI vốn chỉ so trùng
chuỗi giữa danh sách kỹ năng của CV và JD ("reactjs" ≠ "react").
"""
import re

from .preprocessing import normalize_for_match


def skill_terms(skill) -> set[str]:
    return {term for term in (normalize_for_match(t) for t in [skill.name, *(skill.aliases or [])]) if term}


def find_skills(skills, *, cv_skills, cv_text: str) -> tuple[list, list]:
    """skills: các Skill (danh mục) của tin. Trả về (có, thiếu) theo đúng thứ tự đầu vào."""
    known = {normalize_for_match(s) for s in cv_skills}
    text = normalize_for_match(cv_text)
    found, missing = [], []
    for skill in skills:
        terms = skill_terms(skill)
        hit = bool(terms & known) or any(_contains(text, term) for term in terms)
        (found if hit else missing).append(skill)
    return found, missing


def _contains(text: str, term: str) -> bool:
    # Ranh giới là ký tự không phải chữ / số để giữ được kỹ năng có ký tự đặc biệt: C++, C#, .NET
    return re.search(rf'(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])', text) is not None
