from django.db import models
from django.utils import timezone

from common.models import choices_constraint


class Location(models.Model):
    """Tỉnh/thành phố (34 đơn vị hành chính cấp tỉnh từ 01/07/2025)."""

    name = models.CharField('tên', max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    country_code = models.CharField('mã quốc gia', max_length=2, default='VN')

    class Meta:
        db_table = 'locations'
        verbose_name = 'tỉnh/thành phố'
        verbose_name_plural = 'tỉnh/thành phố'
        ordering = ['id']

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField('tên', max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name='ngành cha'
    )

    class Meta:
        db_table = 'industries'
        verbose_name = 'ngành nghề'
        verbose_name_plural = 'ngành nghề'
        ordering = ['name']

    def __str__(self):
        return self.name


class SkillCategory(models.TextChoices):
    TECHNICAL = 'technical', 'Chuyên môn'
    SOFT = 'soft', 'Kỹ năng mềm'
    LANGUAGE = 'language', 'Ngoại ngữ'
    TOOL = 'tool', 'Công cụ'
    DOMAIN = 'domain', 'Nghiệp vụ'


class Skill(models.Model):
    """Danh mục kỹ năng chuẩn hóa, điều kiện để so khớp CV - JD chính xác.

    `aliases` gom các cách viết khác nhau ("ReactJS", "React.js") về một kỹ năng.
    Kỹ năng do nhà tuyển dụng (sau này cả AI/NLP) tự thêm có is_verified=False để admin duyệt.
    """

    name = models.CharField('tên', max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.CharField(
        'nhóm', max_length=20, choices=SkillCategory.choices, default=SkillCategory.TECHNICAL
    )
    aliases = models.JSONField('tên gọi khác', default=list, blank=True)
    is_verified = models.BooleanField('đã duyệt', default=False)
    created_at = models.DateTimeField('ngày tạo', default=timezone.now, editable=False)

    class Meta:
        db_table = 'skills'
        verbose_name = 'kỹ năng'
        verbose_name_plural = 'kỹ năng'
        ordering = ['name']
        constraints = [choices_constraint('category', SkillCategory, 'ck_skills_category')]

    def __str__(self):
        return self.name
