"""Embedding các tin đang tuyển để gợi ý việc làm không phải chờ ở lần dùng đầu tiên.

    python manage.py embed_jobs

Dùng cho dữ liệu có sẵn (nạp từ database/seed.sql, seed_demo...) vì các tin này không đi qua tín hiệu đăng tin.
Tin mới đăng / sửa sau đó được embedding tự động (ai.receivers.on_job_changed). Chạy lại nhiều lần được: tin có
vector còn mới thì bỏ qua, không tốn lượt gọi API.
"""
from django.core.management.base import BaseCommand, CommandError

from apps.ai.llm.exceptions import AIError
from apps.ai.vectorstore import indexer
from apps.jobs import selectors


class Command(BaseCommand):
    help = 'Embedding các tin tuyển dụng đang tuyển chưa có vector hoặc có vector đã cũ.'

    def handle(self, *args, **options):
        jobs = list(selectors.public_jobs())
        try:
            _, embedded = indexer.sync_jobs(jobs)
        except AIError as exc:
            raise CommandError(str(exc.detail)) from exc
        self.stdout.write(self.style.SUCCESS(
            f'Hoàn tất: {len(jobs)} tin đang tuyển, {embedded} tin vừa embedding, {len(jobs) - embedded} tin đã có vector.'
        ))
