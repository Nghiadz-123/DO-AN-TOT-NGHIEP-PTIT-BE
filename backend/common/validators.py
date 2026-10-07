from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

phone_validator = RegexValidator(
    r'^\+?[0-9][0-9 .()-]{7,19}$', 'Số điện thoại không hợp lệ.'
)

# Mã số thuế VN: 10 chữ số, chi nhánh thêm "-" + 3 chữ số
tax_code_validator = RegexValidator(
    r'^\d{10}(-\d{3})?$', 'Mã số thuế gồm 10 chữ số (chi nhánh: 10 số + "-" + 3 số).'
)


@deconstructible
class MaxFileSizeValidator:
    def __init__(self, max_bytes):
        self.max_bytes = max_bytes

    def __call__(self, file):
        if file and file.size > self.max_bytes:
            raise ValidationError(
                f'File vượt quá dung lượng cho phép ({self.max_bytes // (1024 * 1024)} MB).'
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_bytes == other.max_bytes
