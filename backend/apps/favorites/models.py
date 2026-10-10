"""Việc làm và công ty mà ứng viên đánh dấu yêu thích (UC-07 "lưu tin", mở rộng thêm công ty).

App đứng trên candidates, jobs, employers: các app đó không biết tới favorites (FK ngược dùng related_name='+').
"""
from django.db import models
from django.utils import timezone


class FavoriteJob(models.Model):
    candidate = models.ForeignKey(
        'candidates.CandidateProfile', on_delete=models.CASCADE, related_name='favorite_jobs', verbose_name='ứng viên'
    )
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='+', verbose_name='tin tuyển dụng')
    created_at = models.DateTimeField('ngày thêm', default=timezone.now, editable=False)

    class Meta:
        db_table = 'favorite_jobs'
        verbose_name = 'việc làm yêu thích'
        verbose_name_plural = 'việc làm yêu thích'
        ordering = ['-created_at', '-id']
        constraints = [models.UniqueConstraint(fields=['candidate', 'job'], name='uq_favorite_jobs_candidate_job')]

    def __str__(self):
        return f'{self.candidate_id} - {self.job_id}'


class FavoriteCompany(models.Model):
    candidate = models.ForeignKey(
        'candidates.CandidateProfile', on_delete=models.CASCADE, related_name='favorite_companies',
        verbose_name='ứng viên',
    )
    company = models.ForeignKey(
        'employers.Company', on_delete=models.CASCADE, related_name='+', verbose_name='công ty'
    )
    created_at = models.DateTimeField('ngày thêm', default=timezone.now, editable=False)

    class Meta:
        db_table = 'favorite_companies'
        verbose_name = 'công ty yêu thích'
        verbose_name_plural = 'công ty yêu thích'
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['candidate', 'company'], name='uq_favorite_companies_candidate_company')
        ]

    def __str__(self):
        return f'{self.candidate_id} - {self.company_id}'
