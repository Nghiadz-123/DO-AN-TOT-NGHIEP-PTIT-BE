"""Hàm tiện ích nhỏ, không phụ thuộc app nghiệp vụ nào."""
import hashlib
import unicodedata

from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils.text import slugify

_SLUG_SUFFIX_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'


def strip_accents(value: str) -> str:
    """Bỏ dấu tiếng Việt: 'Đà Nẵng' -> 'Da Nang' ('đ' không tự tách dấu nên phải thay riêng)."""
    value = str(value).replace('đ', 'd').replace('Đ', 'D')
    normalized = unicodedata.normalize('NFKD', value)
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch))


def vn_slugify(value: str, max_length: int | None = None) -> str:
    slug = slugify(strip_accents(value))
    if max_length:
        slug = slug[:max_length].strip('-')
    return slug


def unique_slug(value: str, max_length: int) -> str:
    """Slug kèm hậu tố ngẫu nhiên, vd. 'frontend-developer-k3x9q2' (không cần query kiểm tra trùng)."""
    suffix = get_random_string(6, _SLUG_SUFFIX_CHARS)
    base = vn_slugify(value, max_length - len(suffix) - 1) or 'item'
    return f'{base}-{suffix}'


def file_sha256(file) -> str:
    digest = hashlib.sha256()
    for chunk in file.chunks():
        digest.update(chunk)
    file.seek(0)
    return digest.hexdigest()


def absolute_media_url(request, file) -> str | None:
    """URL tuyệt đối của file công khai (frontend chạy khác origin với API)."""
    if not file:
        return None
    url = file.url
    return request.build_absolute_uri(url) if request else url


def send_on_commit(signal, sender, **kwargs):
    """Phát domain event sau khi transaction commit, để receiver (vd. module AI) không đọc dữ liệu chưa lưu."""
    transaction.on_commit(lambda: signal.send(sender=sender, **kwargs))
