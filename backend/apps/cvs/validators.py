"""Kiểm tra file CV trước khi lưu.

Định dạng được xác định theo NỘI DUNG file (chữ ký đầu file, cấu trúc DOCX), không tin phần mở rộng
hay Content-Type do trình duyệt gửi lên; phần mở rộng phải khớp với nội dung.
"""
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError

from common.validators import MaxFileSizeValidator

from .models import CVMimeType

EXTENSION_MIME_TYPES = {'.pdf': CVMimeType.PDF, '.docx': CVMimeType.DOCX}
PDF_SIGNATURE = b'%PDF-'
ZIP_SIGNATURE = b'PK\x03\x04'
DOCX_MAIN_PART = 'word/document.xml'
DOCX_MACRO_PART = 'word/vbaProject.bin'
# Theo đặc tả, header %PDF- có thể nằm sau vài byte rác nhưng trong 1024 byte đầu
HEADER_SCAN_BYTES = 1024


def validate_cv_file(file) -> str:
    """Trả về mime type (CVMimeType) của file CV hợp lệ, ngược lại ném ValidationError."""
    expected = EXTENSION_MIME_TYPES.get(Path(file.name or '').suffix.lower())
    if expected is None:
        raise ValidationError('Chỉ hỗ trợ file PDF hoặc DOCX.', code='invalid_extension')
    if not file.size:
        raise ValidationError('File rỗng.', code='empty_file')
    MaxFileSizeValidator(settings.CV_MAX_SIZE)(file)

    detected = _detect_mime_type(file)
    if detected != expected:
        raise ValidationError(
            'Nội dung file không đúng định dạng PDF/DOCX hoặc file đã bị hỏng.', code='invalid_content'
        )
    return detected


def _detect_mime_type(file) -> str | None:
    file.seek(0)
    head = file.read(HEADER_SCAN_BYTES)
    file.seek(0)
    if head.startswith(ZIP_SIGNATURE):
        return _detect_docx(file)
    if PDF_SIGNATURE in head:
        return CVMimeType.PDF
    return None  # .doc (Word 97-2003), ảnh, file khác...


def _detect_docx(file) -> str | None:
    try:
        with zipfile.ZipFile(file) as archive:
            names = set(archive.namelist())
    except (zipfile.BadZipFile, OSError, ValueError):
        return None
    finally:
        file.seek(0)
    if DOCX_MAIN_PART not in names:
        return None  # zip khác (xlsx, pptx, ...)
    if DOCX_MACRO_PART in names:
        raise ValidationError('File chứa macro (.docm đổi đuôi) không được hỗ trợ.', code='macro_not_allowed')
    return CVMimeType.DOCX
