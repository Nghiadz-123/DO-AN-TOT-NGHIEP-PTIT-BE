"""Chuẩn hóa kỹ năng người dùng nhập về danh mục `skills`."""
from collections.abc import Iterable

from common.utils import vn_slugify

from .models import Skill

SKILL_NAME_MAX_LENGTH = 100


def clean_skill_name(name) -> str:
    return ' '.join(str(name or '').split())[:SKILL_NAME_MAX_LENGTH]


def skill_slug(name: str) -> str:
    """Slug phân biệt được các tên có ký tự đặc biệt: 'C++' -> 'c-plus-plus', 'C#' -> 'c-sharp',
    '.NET' -> 'dot-net', 'Node.js' -> 'node-dot-js'."""
    text = clean_skill_name(name).lower()
    text = text.replace('+', ' plus ').replace('#', ' sharp ').replace('.', ' dot ')
    return vn_slugify(text, 120)


def resolve_skills(names: Iterable[str]) -> list[Skill | None]:
    """Map từng tên kỹ năng -> Skill trong danh mục (theo slug, rồi theo aliases).

    Tên chưa có trong danh mục được tạo mới với is_verified=False để admin duyệt.
    Trả về list cùng thứ tự đầu vào; tên rỗng -> None.
    """
    names = [clean_skill_name(n) for n in names]
    slugs = {n: skill_slug(n) for n in names if n}
    existing = {s.slug: s for s in Skill.objects.filter(slug__in=set(slugs.values()))}

    result = []
    for name in names:
        slug = slugs.get(name)
        if not slug:
            result.append(None)
            continue
        skill = existing.get(slug) or _find_by_alias(name)
        if skill is None:
            skill, _ = Skill.objects.get_or_create(slug=slug, defaults={'name': name, 'is_verified': False})
        existing[slug] = skill
        result.append(skill)
    return result


def _find_by_alias(name: str) -> Skill | None:
    target = name.lower()
    # icontains trên JSON chạy được cả PostgreSQL lẫn SQLite; lọc chính xác lại bằng Python
    for skill in Skill.objects.filter(aliases__icontains=name):
        if any(str(alias).lower() == target for alias in skill.aliases):
            return skill
    return None
