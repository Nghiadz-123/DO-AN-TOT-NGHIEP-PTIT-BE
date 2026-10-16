from django.contrib import admin

from .models import CVAnalysis, JobMatch


@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    list_display = ['cv', 'score_total', 'scored_at', 'suggested_at', 'updated_at']
    list_select_related = ['cv']
    search_fields = ['cv__title', 'cv__candidate__user__email']
    raw_id_fields = ['cv', 'target_job']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ['cv', 'job', 'score', 'updated_at']
    list_select_related = ['cv', 'job']
    raw_id_fields = ['cv', 'job']
    readonly_fields = ['created_at', 'updated_at']
