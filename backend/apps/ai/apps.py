from django.apps import AppConfig


class AiConfig(AppConfig):
    name = 'apps.ai'
    label = 'ai'
    verbose_name = 'AI'

    def ready(self):
        from apps.cvs.signals import cv_deleted, cv_replaced
        from apps.jobs.signals import job_published, job_updated

        from .receivers import on_cv_deleted, on_job_changed

        cv_deleted.connect(on_cv_deleted, dispatch_uid='ai.on_cv_deleted')
        cv_replaced.connect(on_cv_deleted, dispatch_uid='ai.on_cv_replaced')  # kết quả AI của file cũ không còn đúng
        job_published.connect(on_job_changed, dispatch_uid='ai.on_job_published')
        job_updated.connect(on_job_changed, dispatch_uid='ai.on_job_updated')
