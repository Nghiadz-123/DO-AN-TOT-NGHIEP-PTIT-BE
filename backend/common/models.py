"""Abstract model dùng chung: khóa UUID, mốc thời gian, xóa mềm."""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone


class UUIDModel(models.Model):
    """Bảng nghiệp vụ dùng UUID: không đoán được id qua URL, dễ đồng bộ với vector store."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    # default thay cho auto_now_add để seed/test có thể đặt mốc thời gian trong quá khứ
    created_at = models.DateTimeField('ngày tạo', default=timezone.now, editable=False)
    updated_at = models.DateTimeField('ngày cập nhật', auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)


class AliveManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager mặc định: ẩn bản ghi đã xóa mềm. Dùng `all_objects` khi cần cả bản ghi đã xóa."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField('ngày xóa', null=True, blank=True, editable=False)

    objects = AliveManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = timezone.now()
        fields = ['deleted_at']
        if hasattr(self, 'updated_at'):
            fields.append('updated_at')
        self.save(update_fields=fields)


def choices_constraint(field, choices, name):
    """CHECK constraint cho cột enum (VARCHAR + CHECK như database/schema.sql)."""
    return CheckConstraint(condition=Q(**{f'{field}__in': choices.values}), name=name)
