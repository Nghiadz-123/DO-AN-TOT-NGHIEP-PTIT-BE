from django.contrib import admin

from .models import FavoriteCompany, FavoriteJob


@admin.register(FavoriteJob)
class FavoriteJobAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'created_at']
    search_fields = ['candidate__user__email', 'job__title']
    raw_id_fields = ['candidate', 'job']


@admin.register(FavoriteCompany)
class FavoriteCompanyAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'company', 'created_at']
    search_fields = ['candidate__user__email', 'company__name']
    raw_id_fields = ['candidate', 'company']
