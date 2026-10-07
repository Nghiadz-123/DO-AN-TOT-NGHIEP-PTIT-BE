from django.contrib import admin

from .models import Industry, Location, Skill


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'country_code']
    search_fields = ['name', 'slug']


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'category']
    search_fields = ['name', 'slug']
    actions = ['mark_verified']

    @admin.action(description='Duyệt các kỹ năng đã chọn')
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'Đã duyệt {updated} kỹ năng.')
