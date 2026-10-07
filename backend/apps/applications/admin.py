from django.contrib import admin

from .models import Application, ApplicationStatusHistory


class StatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'note', 'created_at']
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'recruiter_rating', 'created_at']
    list_filter = ['status']
    search_fields = ['candidate__user__email', 'candidate__user__full_name', 'job__title']
    raw_id_fields = ['job', 'candidate', 'cv']
    readonly_fields = ['status_changed_at', 'created_at', 'updated_at']
    inlines = [StatusHistoryInline]
