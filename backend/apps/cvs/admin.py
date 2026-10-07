from django.contrib import admin

from .models import CV


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['title', 'candidate', 'original_filename', 'mime_type', 'file_size', 'is_default', 'created_at']
    list_filter = ['mime_type', 'is_default']
    search_fields = ['title', 'original_filename', 'candidate__user__email']
    raw_id_fields = ['candidate']
    readonly_fields = ['file_hash', 'created_at', 'updated_at', 'deleted_at']
