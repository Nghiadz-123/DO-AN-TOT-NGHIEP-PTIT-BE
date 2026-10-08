from django.contrib import admin

from . import services
from .models import CV


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'candidate', 'original_filename', 'mime_type', 'file_size', 'is_default', 'parse_status',
        'created_at', 'deleted_at',
    ]
    list_filter = ['mime_type', 'is_default', 'parse_status']
    search_fields = ['title', 'original_filename', 'candidate__user__email']
    raw_id_fields = ['candidate']
    readonly_fields = [
        'file_hash', 'parse_status', 'parse_error', 'raw_text', 'parsed_data', 'parsed_at',
        'created_at', 'updated_at', 'deleted_at',
    ]
    actions = ['reparse']

    def get_queryset(self, request):
        return CV.all_objects.select_related('candidate__user')  # admin thấy cả CV đã xóa mềm

    @admin.action(description='Bóc tách lại các CV đã chọn')
    def reparse(self, request, queryset):
        count = 0
        for cv in queryset.filter(deleted_at__isnull=True):
            services.parse_cv(cv)
            count += 1
        self.message_user(request, f'Đã bóc tách lại {count} CV.')
