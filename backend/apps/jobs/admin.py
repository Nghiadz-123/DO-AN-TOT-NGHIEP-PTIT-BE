from django.contrib import admin

from .models import Job, JobSkill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 0
    raw_id_fields = ['skill']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'status', 'job_type', 'level', 'deadline', 'application_count', 'created_at']
    list_filter = ['status', 'job_type', 'level', 'work_mode']
    search_fields = ['title', 'company__name']
    raw_id_fields = ['company', 'created_by']
    readonly_fields = ['slug', 'published_at', 'closed_at', 'view_count', 'application_count',
                       'created_at', 'updated_at', 'deleted_at']
    inlines = [JobSkillInline]

    def get_queryset(self, request):
        return Job.all_objects.select_related('company')
