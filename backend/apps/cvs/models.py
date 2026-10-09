"""CV của ứng viên.

Mỗi lần upload là một bản ghi mới; CV đã dùng để nộp đơn thì không sửa tại chỗ, nhờ vậy NTD luôn
thấy đúng bản ứng viên đã nộp. Sau khi upload, file được bóc tách thành văn bản (cvs/parsers, không
dùng AI) và lưu vào các cột parse_*; phân tích/chấm điểm và đồng bộ vector store (vector_model,
vector_indexed_at) thuộc module AI (giai đoạn sau).
"""
import uuid
from pathlib import Path

from django.db import models
from django.db.models import CheckConstraint, Q

from common.models import SoftDeleteModel, TimeStampedModel, UUIDModel, choices_constraint
from common.storage import private_storage


class CVMimeType(models.TextChoices):
    PDF = 'application/pdf', 'PDF'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'DOCX'


class CVParseStatus(models.TextChoices):
    PENDING = 'pending', 'Chờ xử lý'
    PROCESSING = 'processing', 'Đang xử lý'
    COMPLETED = 'completed', 'Hoàn tất'
    FAILED = 'failed', 'Thất bại'


def cv_file_path(instance, filename):
    return f'cvs/{instance.candidate_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'


class CV(UUIDModel, TimeStampedModel, SoftDeleteModel):
    candidate = models.ForeignKey(
        'candidates.CandidateProfile', on_delete=models.CASCADE, related_name='cvs', verbose_name='ứng viên'
    )
    title = models.CharField('tên CV', max_length=150)
    file = models.FileField('file', upload_to=cv_file_path, storage=private_storage, max_length=500)
    original_filename = models.CharField('tên file gốc', max_length=255)
    mime_type = models.CharField('định dạng', max_length=100, choices=CVMimeType.choices)
    file_size = models.PositiveIntegerField('dung lượng (byte)')
    file_hash = models.CharField('SHA-256', max_length=64, db_index=True)
    language = models.CharField('ngôn ngữ', max_length=10, blank=True)
    is_default = models.BooleanField('CV mặc định', default=False)
    # Kết quả bóc tách (parser, không dùng LLM)
    parse_status = models.CharField(
        'trạng thái bóc tách', max_length=20, choices=CVParseStatus.choices, default=CVParseStatus.PENDING
    )
    parse_error = models.TextField('lỗi bóc tách', blank=True)
    raw_text = models.TextField('văn bản trích xuất', blank=True)
    parsed_data = models.JSONField('dữ liệu bóc tách', null=True, blank=True)
    parsed_at = models.DateTimeField('bóc tách lúc', null=True, blank=True)

    class Meta:
        db_table = 'cvs'
        verbose_name = 'CV'
        verbose_name_plural = 'CV'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['candidate', '-created_at'], name='idx_cvs_candidate')]
        constraints = [
            choices_constraint('mime_type', CVMimeType, 'ck_cvs_mime_type'),
            choices_constraint('parse_status', CVParseStatus, 'ck_cvs_parse_status'),
            CheckConstraint(condition=Q(file_size__gt=0), name='ck_cvs_file_size_positive'),
            # Mỗi ứng viên có tối đa 1 CV mặc định (partial unique index)
            models.UniqueConstraint(
                fields=['candidate'], condition=Q(is_default=True, deleted_at__isnull=True), name='uq_cvs_default'
            ),
        ]

    def __str__(self):
        return self.title
