"""Chuyển file CV thành văn bản thô và thông tin cơ bản (không dùng AI).

    extract_text(file, mime_type)  -> ExtractedText (văn bản đã chuẩn hóa + số trang)
    build_parsed_data(extracted)   -> dict lưu vào CV.parsed_data
    detect_language(text)          -> 'vi' | 'en' | ''

Lỗi người dùng cần biết (file có mật khẩu, CV dạng ảnh...) ném CVParseError với thông điệp tiếng Việt.
Bóc tách cấu trúc (học vấn, kinh nghiệm, kỹ năng...) và chấm điểm thuộc module AI (giai đoạn sau).
"""
import re
import unicodedata
from dataclasses import dataclass

from ..models import CVMimeType

# CV thật hiếm khi quá 20.000 ký tự; giới hạn để file bất thường không làm phình DB / prompt AI
RAW_TEXT_MAX_LENGTH = 100_000
# Ít hơn ngưỡng này coi như không có lớp chữ (CV dạng ảnh, PDF scan)
MIN_TEXT_LENGTH = 30
PARSED_DATA_VERSION = 1
MAX_CONTACTS = 5
MAX_LINKS = 10


class CVParseError(Exception):
    """Không trích xuất được văn bản. str(exc) là thông điệp hiển thị cho ứng viên."""


@dataclass
class ExtractedText:
    text: str
    page_count: int | None = None


def extract_text(file, mime_type: str) -> ExtractedText:
    from . import docx_parser, pdf_parser

    parsers = {CVMimeType.PDF: pdf_parser.extract_text, CVMimeType.DOCX: docx_parser.extract_text}
    parser = parsers.get(mime_type)
    if parser is None:
        raise CVParseError('Định dạng file không được hỗ trợ.')

    extracted = parser(file)
    extracted.text = normalize_text(extracted.text)[:RAW_TEXT_MAX_LENGTH]
    if len(extracted.text) < MIN_TEXT_LENGTH:
        raise CVParseError(
            'Không trích xuất được nội dung chữ từ CV (có thể CV ở dạng ảnh hoặc bản scan). '
            'Vui lòng tải lên file PDF xuất từ Word/Google Docs hoặc file DOCX.'
        )
    return extracted


# --------------------------------------------------------------------------- chuẩn hóa văn bản
_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b-\x1f\x7f​-‏﻿]')
_INLINE_SPACES = re.compile(r'[ \t\xa0]+')
_MANY_BLANK_LINES = re.compile(r'\n{3,}')


def normalize_text(text: str) -> str:
    """NFC (tiếng Việt từ PDF hay ở dạng tổ hợp), bỏ ký tự điều khiển (PostgreSQL không nhận \\x00),
    gộp khoảng trắng trong dòng và dòng trống liên tiếp."""
    text = unicodedata.normalize('NFC', text or '').replace('\r\n', '\n').replace('\r', '\n')
    text = _CONTROL_CHARS.sub('', text)
    lines = (_INLINE_SPACES.sub(' ', line).strip() for line in text.split('\n'))
    return _MANY_BLANK_LINES.sub('\n\n', '\n'.join(lines)).strip()


# --------------------------------------------------------------------------- thông tin cơ bản
_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
# Số di động/cố định VN: 0xxxxxxxxx hoặc +84xxxxxxxxx, cho phép dấu cách/chấm/gạch giữa các nhóm số
_PHONE = re.compile(r'(?<![\d+])(?:\+84|0)(?:[ .-]?\d){9,10}(?!\d)')
_LINK = re.compile(
    r'(?:https?://|www\.)[^\s<>"\')]+'
    r'|\b(?:linkedin\.com|github\.com|gitlab\.com|behance\.net|dribbble\.com)/[^\s<>"\')]+',
    re.IGNORECASE,
)
_VIETNAMESE_CHARS = set(
    'ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
)


def build_parsed_data(extracted: ExtractedText) -> dict:
    """Dữ liệu cơ bản lấy được bằng rule. Module AI bổ sung cấu trúc chi tiết vào cùng JSON này
    (trường `source` cho biết phần nào do parser tạo)."""
    text = extracted.text
    return {
        'version': PARSED_DATA_VERSION,
        'source': 'parser',
        'stats': {'pages': extracted.page_count, 'words': len(text.split()), 'characters': len(text)},
        'contact': {
            'emails': _unique(m.lower() for m in _EMAIL.findall(text))[:MAX_CONTACTS],
            'phones': _unique(_clean_phone(m) for m in _PHONE.findall(text))[:MAX_CONTACTS],
            'links': _unique(m.rstrip('.,;:') for m in _LINK.findall(text))[:MAX_LINKS],
        },
    }


def detect_language(text: str) -> str:
    """Ước lượng ngôn ngữ CV: có chữ cái tiếng Việt có dấu -> 'vi', còn lại -> 'en'.
    (CV tiếng Việt viết không dấu sẽ bị nhận là 'en'; ứng viên/AI có thể sửa sau.)"""
    letters = [ch for ch in text.lower() if ch.isalpha()]
    if not letters:
        return ''
    vietnamese = sum(ch in _VIETNAMESE_CHARS for ch in letters)
    return 'vi' if vietnamese / len(letters) >= 0.01 else 'en'


def _clean_phone(value: str) -> str:
    return re.sub(r'[ .-]', '', value)


def _unique(values) -> list:
    return list(dict.fromkeys(v for v in values if v))
