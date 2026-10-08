from django.contrib import admin

from .models import CandidateProfile


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'current_level', 'years_of_experience', 'location', 'is_open_to_work']
    list_filter = ['current_level', 'is_open_to_work', 'is_public']
    search_fields = ['user__email', 'user__full_name', 'headline']
    raw_id_fields = ['user']
