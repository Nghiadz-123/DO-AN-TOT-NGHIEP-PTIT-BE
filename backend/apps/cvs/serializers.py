from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import CV
from .validators import validate_cv_file


class CVParsedContactSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField())
    phones = serializers.ListField(child=serializers.CharField())
    links = serializers.ListField(child=serializers.CharField())


class CVParsedStatsSerializer(serializers.Serializer):
    pages = serializers.IntegerField(allow_null=True)
    words = serializers.IntegerField()
    characters = serializers.IntegerField()


class CVParsedDataSerializer(serializers.Serializer):
    """Chỉ dùng cho tài liệu OpenAPI. Module AI có thể bổ sung thêm khóa vào cùng JSON."""

    version = serializers.IntegerField()
    source = serializers.CharField(help_text='parser: lấy bằng rule, không dùng AI')
    stats = CVParsedStatsSerializer()
    contact = CVParsedContactSerializer()


@extend_schema_field(CVParsedDataSerializer(allow_null=True))
class ParsedDataField(serializers.JSONField):
    """Trả nguyên JSON đã lưu (không lọc khóa) nhưng mô tả cấu trúc trong Swagger."""


class CVSerializer(serializers.ModelSerializer):
    """Một CV trong danh sách "CV của tôi"."""

    application_count = serializers.IntegerField(read_only=True, help_text='Số lần đã dùng CV này để ứng tuyển')
    file_url = serializers.SerializerMethodField(
        help_text='Link xem file (cần access token như mọi API); thêm ?download=1 để tải về'
    )

    class Meta:
        model = CV
        fields = [
            'id', 'title', 'original_filename', 'mime_type', 'file_size', 'language', 'is_default',
            'parse_status', 'parse_error', 'parsed_at', 'application_count', 'file_url', 'created_at', 'updated_at',
        ]

    def get_file_url(self, obj) -> str:
        url = reverse('candidate-cv-file', args=[obj.pk])
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


class CVDetailSerializer(CVSerializer):
    parsed_data = ParsedDataField(read_only=True)

    class Meta(CVSerializer.Meta):
        fields = CVSerializer.Meta.fields + ['raw_text', 'parsed_data']


class CVUploadSerializer(serializers.Serializer):
    file = serializers.FileField(help_text='File PDF hoặc DOCX, tối đa 5 MB')
    title = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default='', help_text='Tên CV; bỏ trống thì lấy theo tên file'
    )
    is_default = serializers.BooleanField(
        required=False, default=False, help_text='Đặt làm CV mặc định (CV đầu tiên luôn là mặc định)'
    )

    def validate_file(self, value):
        # Django ValidationError của validator được DRF đổi thành lỗi của trường `file`
        self._mime_type = validate_cv_file(value)
        return value

    def validate(self, attrs):
        attrs['mime_type'] = self._mime_type
        return attrs


class CVUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
