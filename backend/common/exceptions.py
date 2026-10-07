"""Chuẩn hóa response lỗi để frontend xử lý thống nhất.

Mọi lỗi API có dạng:
    {"detail": "<thông điệp chính>", "code": "<mã lỗi>", "errors": {...}}
`errors` chỉ có ở lỗi validate (400), là map field -> danh sách thông điệp.
"""
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, JsonResponse
from django.views.defaults import page_not_found as django_page_not_found
from rest_framework import exceptions, status
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


class BusinessError(exceptions.APIException):
    """Vi phạm quy tắc nghiệp vụ (vd. chuyển trạng thái không hợp lệ, xóa tin đã có hồ sơ)."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Thao tác không hợp lệ.'
    default_code = 'business_error'

    def __init__(self, detail=None, code=None, status_code=None):
        super().__init__(detail, code)
        if status_code is not None:
            self.status_code = status_code


def custom_exception_handler(exc, context):
    # Service ném lỗi của Django (không phụ thuộc DRF) -> đổi sang lỗi tương ứng của DRF
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))
    elif isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)
    if response is None:
        return None  # lỗi 500: để Django ghi log

    if isinstance(exc, exceptions.ValidationError):
        errors = response.data if isinstance(response.data, dict) else {'non_field_errors': response.data}
        response.data = {
            'detail': _first_message(errors) or 'Dữ liệu không hợp lệ.',
            'code': 'validation_error',
            'errors': errors,
        }
    else:
        data = response.data if isinstance(response.data, dict) else {'detail': response.data}
        code = data.get('code') if isinstance(data.get('code'), str) else exc.get_codes()
        response.data = {
            'detail': str(data.get('detail', '')),
            'code': code if isinstance(code, str) else 'error',
        }
    return response


def _first_message(errors):
    if isinstance(errors, dict):
        values = errors.values()
    elif isinstance(errors, list):
        values = errors
    else:
        return str(errors) if errors else None
    for value in values:
        message = _first_message(value)
        if message:
            return message
    return None


def page_not_found(request, exception):
    if request.path.startswith('/api/'):
        return JsonResponse({'detail': 'Không tìm thấy.', 'code': 'not_found'}, status=404)
    return django_page_not_found(request, exception)
