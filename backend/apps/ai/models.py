"""Kết quả AI cho ứng viên: phân tích CV (hồ sơ cấu trúc, chấm điểm, gợi ý sửa), vector của CV / tin tuyển dụng
dùng cho gợi ý việc làm, và kết quả AI đánh giá chi tiết CV - tin.

Mọi kết quả gắn với CV của app cvs; CV bị xóa thì receivers.on_cv_deleted xóa luôn dữ liệu AI của CV đó.
Quan hệ dùng related_name='+' để app cvs / jobs không phụ thuộc ngược vào ai.
"""
from django.db import models
from django.db.models import CheckConstraint, Q

from common.models import TimeStampedModel, UUIDModel


class CVAnalysis(UUIDModel, TimeStampedModel):
    """Một bản ghi cho mỗi CV, giữ kết quả mới nhất của từng chức năng."""

    cv = models.OneToOneField('cvs.CV', on_delete=models.CASCADE, related_name='+', verbose_name='CV')
    # Hồ sơ cấu trúc do LLM bóc tách từ CV.raw_text (prompts.cv_analysis.CV_SCHEMA); tính lại khi văn bản CV đổi
    source_hash = models.CharField('SHA-256 văn bản CV đã bóc tách', max_length=64, blank=True)
    profile = models.JSONField('hồ sơ cấu trúc', null=True, blank=True)
    profiled_at = models.DateTimeField('bóc tách lúc', null=True, blank=True)
    # Chấm điểm (prompts.cv_analysis.SCORE_CRITERIA)
    score_total = models.PositiveSmallIntegerField('điểm CV', null=True, blank=True)
    score_breakdown = models.JSONField('điểm theo tiêu chí', default=dict, blank=True)
    strengths = models.JSONField('điểm mạnh', default=list, blank=True)
    weaknesses = models.JSONField('điểm cần cải thiện', default=list, blank=True)
    scored_at = models.DateTimeField('chấm điểm lúc', null=True, blank=True)
    # Gợi ý sửa CV theo tin mục tiêu (nếu có) + các tin đang tuyển gần CV nhất
    suggestions = models.JSONField('gợi ý sửa CV', default=list, blank=True)
    missing_keywords = models.JSONField('từ khóa nên bổ sung', default=list, blank=True)
    reference_jobs = models.JSONField('tin tham chiếu', default=list, blank=True)
    target_job = models.ForeignKey(
        'jobs.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name='tin mục tiêu'
    )
    suggested_at = models.DateTimeField('gợi ý lúc', null=True, blank=True)

    class Meta:
        db_table = 'cv_analyses'
        verbose_name = 'phân tích CV'
        verbose_name_plural = 'phân tích CV'
        constraints = [CheckConstraint(condition=Q(score_total__lte=100), name='ck_cv_analyses_score_range')]

    def __str__(self):
        return f'Phân tích CV {self.cv_id}'


class CVEmbedding(models.Model):
    """Vector của CV (từ hồ sơ cấu trúc); content_hash + model đổi thì embedding lại."""

    cv = models.OneToOneField('cvs.CV', on_delete=models.CASCADE, primary_key=True, related_name='+')
    content_hash = models.CharField('SHA-256 văn bản đã embedding', max_length=64)
    model = models.CharField('model embedding', max_length=100)
    vector = models.JSONField('vector')
    updated_at = models.DateTimeField('ngày cập nhật', auto_now=True)

    class Meta:
        db_table = 'cv_embeddings'
        verbose_name = 'vector CV'
        verbose_name_plural = 'vector CV'


class JobEmbedding(models.Model):
    """Vector của tin tuyển dụng; tin được sửa (content_hash đổi) thì embedding lại ở lần gợi ý sau."""

    job = models.OneToOneField('jobs.Job', on_delete=models.CASCADE, primary_key=True, related_name='+')
    content_hash = models.CharField('SHA-256 văn bản đã embedding', max_length=64)
    model = models.CharField('model embedding', max_length=100)
    vector = models.JSONField('vector')
    updated_at = models.DateTimeField('ngày cập nhật', auto_now=True)

    class Meta:
        db_table = 'job_embeddings'
        verbose_name = 'vector tin tuyển dụng'
        verbose_name_plural = 'vector tin tuyển dụng'


class JobMatch(UUIDModel, TimeStampedModel):
    """AI (LLM) đánh giá chi tiết mức độ phù hợp CV - tin; dùng lại tới khi CV hoặc nội dung tin thay đổi."""

    cv = models.ForeignKey('cvs.CV', on_delete=models.CASCADE, related_name='+', verbose_name='CV')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='+', verbose_name='tin tuyển dụng')
    score = models.PositiveSmallIntegerField('điểm AI')
    matched_skills = models.JSONField('kỹ năng phù hợp', default=list, blank=True)
    missing_skills = models.JSONField('kỹ năng còn thiếu', default=list, blank=True)
    reason = models.TextField('nhận xét', blank=True)
    cv_hash = models.CharField('SHA-256 văn bản CV', max_length=64)
    job_hash = models.CharField('SHA-256 nội dung tin', max_length=64)

    class Meta:
        db_table = 'match_results'
        verbose_name = 'AI đánh giá CV - tin'
        verbose_name_plural = 'AI đánh giá CV - tin'
        constraints = [
            models.UniqueConstraint(fields=['cv', 'job'], name='uq_match_results_cv_job'),
            CheckConstraint(condition=Q(score__lte=100), name='ck_match_results_score_range'),
        ]

    def __str__(self):
        return f'{self.cv_id} - {self.job_id}: {self.score}'
