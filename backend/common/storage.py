"""Abstraction lưu file.

- File công khai (logo): storage mặc định của Django (MEDIA_ROOT, có URL công khai).
- File riêng tư (CV - dữ liệu cá nhân): PrivateMediaStorage, không có URL công khai,
  chỉ trả về qua API sau khi kiểm tra quyền. Khi lên production có thể thay bằng
  bucket S3/MinIO private mà không phải sửa model.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property


class PrivateMediaStorage(FileSystemStorage):
    @cached_property
    def base_location(self):
        return self._value_or_setting(self._location, settings.PRIVATE_MEDIA_ROOT)

    def url(self, name):
        return None


def private_storage():
    # Truyền callable vào FileField(storage=...) để migration không phụ thuộc đường dẫn cụ thể
    return PrivateMediaStorage()
