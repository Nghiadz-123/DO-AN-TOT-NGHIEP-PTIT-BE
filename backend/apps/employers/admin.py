from django.contrib import admin

from . import services
from .models import Company, Recruiter, VerificationStatus


class RecruiterInline(admin.TabularInline):
    model = Recruiter
    extra = 0
    fields = ['user', 'position', 'company_role', 'status', 'joined_at']
    raw_id_fields = ['user']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_code', 'verification_status', 'location', 'created_at', 'deleted_at']
    list_filter = ['verification_status', 'company_size']
    search_fields = ['name', 'tax_code', 'email']
    readonly_fields = ['slug', 'verified_at', 'verified_by', 'created_by', 'created_at', 'updated_at', 'deleted_at']
    inlines = [RecruiterInline]
    actions = ['verify', 'reject']

    def get_queryset(self, request):
        return Company.all_objects.all()  # admin thấy cả công ty đã xóa mềm

    @admin.action(description='Xác minh các công ty đã chọn')
    def verify(self, request, queryset):
        for company in queryset:
            services.set_verification(company, status=VerificationStatus.VERIFIED, by=request.user)
        self.message_user(request, f'Đã xác minh {queryset.count()} công ty.')

    @admin.action(description='Từ chối xác minh các công ty đã chọn')
    def reject(self, request, queryset):
        for company in queryset:
            services.set_verification(company, status=VerificationStatus.REJECTED, by=request.user)
        self.message_user(request, f'Đã từ chối {queryset.count()} công ty.')


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'position', 'company_role', 'status']
    list_filter = ['company_role', 'status']
    search_fields = ['user__email', 'user__full_name', 'company__name']
    raw_id_fields = ['user', 'company']
