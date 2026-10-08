"""Bóc tách (lại) văn bản CV, vd. CV có từ trước khi có chức năng bóc tách hoặc CV bị lỗi.

    python manage.py parse_cvs          # CV đang pending / failed
    python manage.py parse_cvs --all    # mọi CV chưa xóa
"""
from django.core.management.base import BaseCommand

from apps.cvs import services
from apps.cvs.models import CV, CVParseStatus


class Command(BaseCommand):
    help = 'Bóc tách văn bản các CV đang chờ xử lý hoặc bị lỗi.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Bóc tách lại mọi CV chưa xóa')

    def handle(self, *args, **options):
        queryset = CV.objects.all()
        if not options['all']:
            queryset = queryset.filter(parse_status__in=[CVParseStatus.PENDING, CVParseStatus.FAILED])

        completed = failed = 0
        for cv in queryset.iterator():
            services.parse_cv(cv)
            if cv.parse_status == CVParseStatus.COMPLETED:
                completed += 1
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(f'{cv.id} ({cv.original_filename}): {cv.parse_error}'))
        self.stdout.write(self.style.SUCCESS(f'Hoàn tất: {completed} CV thành công, {failed} CV lỗi.'))
