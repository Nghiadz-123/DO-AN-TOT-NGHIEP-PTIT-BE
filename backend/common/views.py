"""Hàm dùng chung cho views.py của các app: đọc dữ liệu request đã validate, trả file.

Quy ước viết view (để nhìn vào là biết endpoint nhận gì, trả gì):
- Mỗi endpoint là một method, ngay trên đó là comment `# METHOD /api/v1/<đường-dẫn>/`.
- `@extend_schema(request=..., parameters=..., responses=...)` đặt trên chính method đó là hợp đồng của endpoint
  (nhận body / query nào, trả serializer nào với mã HTTP nào); Swagger /api/docs/ sinh ra từ đây.
- Thân method đọc từ trên xuống: dữ liệu vào (`validated_body` / `validated_query`) -> services / selectors
  -> `Response(<Serializer trả về>(...).data, status=...)`.
"""
from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from rest_framework.exceptions import NotFound

# Tài liệu OpenAPI cho endpoint trả file: tham số ?download=1 và response nhị phân
DOWNLOAD_PARAMETER = OpenApiParameter('download', OpenApiTypes.BOOL, description='1: tải về thay vì xem trực tiếp')
FILE_RESPONSE = {(200, 'application/octet-stream'): OpenApiResponse(OpenApiTypes.BINARY)}


def validated_body(request, serializer_class, *, instance=None, partial=False, context=None):
    """Body của request (JSON / multipart) sau khi `serializer_class` validate.

    `instance` + `partial=True`: sửa một phần đối tượng có sẵn (PATCH). Dữ liệu sai thì ném ValidationError,
    exception handler chung (common/exceptions.py) trả 400 kèm lỗi từng trường.
    """
    serializer = serializer_class(
        instance, data=request.data, partial=partial, context={'request': request, **(context or {})}
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def validated_query(request, serializer_class):
    """Tham số query string (?q=...&status=...) sau khi `serializer_class` validate; sai thì 400."""
    serializer = serializer_class(data=request.query_params, context={'request': request})
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def file_response(request, file, *, filename, content_type, not_found_message):
    """Trả file để trình duyệt xem trực tiếp; `?download=1` (hoặc `true`) thì tải về.

    File không còn trên storage thì 404 với `not_found_message`.
    """
    if not file or not file.storage.exists(file.name):
        raise NotFound(not_found_message)
    return FileResponse(
        file.open('rb'),
        as_attachment=request.query_params.get('download') in ('1', 'true'),
        filename=filename,
        content_type=content_type,
    )
