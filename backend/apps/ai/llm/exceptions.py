"""Lỗi chuẩn hóa của module AI.

Kế thừa BusinessError nên view không phải bắt: DRF trả về đúng định dạng lỗi chung
{"detail": "...", "code": "..."} (common.exceptions), frontend hiển thị `detail` cho ứng viên.
"""
from rest_framework import status

from common.exceptions import BusinessError


class AIError(BusinessError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Chức năng AI tạm thời không khả dụng. Vui lòng thử lại sau.'
    default_code = 'ai_error'


class AINotConfiguredError(AIError):
    """Thiếu / sai API key, model không tồn tại hoặc chọn provider chưa hỗ trợ."""

    default_detail = 'Chức năng AI chưa được cấu hình (thiếu GEMINI_API_KEY trong backend/.env).'
    default_code = 'ai_not_configured'


class AIUnavailableError(AIError):
    """Mọi model đều quá tải / hết quota / lỗi mạng sau khi đã thử lại."""

    default_detail = 'Dịch vụ AI đang quá tải hoặc tạm hết lượt dùng. Vui lòng thử lại sau ít phút.'
    default_code = 'ai_unavailable'


class AIInvalidOutputError(AIError):
    """Model trả về nội dung không phải JSON đúng cấu trúc mong muốn."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'AI trả về kết quả không hợp lệ. Vui lòng thử lại.'
    default_code = 'ai_invalid_output'
